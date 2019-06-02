import pymongo
from collections import Counter

def get_article_data(db, form_data):
  '''
  Gets all articles, their data, and corresponding list
  of locations.
  '''
  article_collection = db.test_article_collection
  relevant_themes = form_data['relevant_themes']
  relevant_theme_set = set(relevant_themes) if relevant_themes else None
  location_list = []

  def get_relevant_articles(location):
    '''
    Get articles near location and with relevant themes
    '''
    geometry_query = {
      'geometry': {
        '$near': {
          '$geometry': {
            'type': 'Point',
            'coordinates': location['coordinates'],
          },
        '$maxDistance': 5000,
        }
      }
    }

    query = {
      '$and': [geometry_query]
    }

    if relevant_themes and relevant_themes != []:
      query['$and'].append({
        'properties.rb_themes': {
          '$in': relevant_themes
        }
      })

    print(query)

    relevant_articles = article_collection.find(query).sort(
      [('properties.relevancy_score', pymongo.DESCENDING)]
    )

    return list(relevant_articles) if relevant_articles else []

  def get_location_article_data(location, location_list):
    '''
    Filters articles based on key information, then
    Creates analytics
    '''
    relevant_articles = get_relevant_articles(location)

    theme_counter = Counter()
    for article in relevant_articles:
      if relevant_theme_set: theme_counter.update(
        list(set(article['properties']['rb_themes']) & relevant_theme_set))
      else: theme_counter.update(article['properties']['rb_themes'])

    # Pop off uninformative themes
    if 'Miscellaneous' in theme_counter:
      theme_counter.pop('Miscellaneous')

    article_geojson = {
      'type': 'FeatureCollection',
      'features': relevant_articles,
    }

    return {
      'count': len(relevant_articles),
      'articles': article_geojson,
      'themes': theme_counter.most_common(5)
    }

  article_data = [get_location_article_data(location, location_list) for location in form_data['locations']]
  return article_data