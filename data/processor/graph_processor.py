import logging
import urllib
from metaphone import doublemetaphone
from bs4 import BeautifulSoup
from pycountry import languages
from langdetect import detect
from rake_nltk import Rake

from ..utils.utils import metaphone_name

TYPE_ORGANIZATION = 'Organization'
TYPE_PERSON = 'Person'

def extract_data(data, date, db):
  '''
  Extracts the url, people, organizations, and location from
  one row in the GKG dataframe
  '''
  people_names = extract_data_list('Persons', data)
  org_names = extract_data_list('Organizations', data)
  actor_names = people_names+org_names

  gkg_themes = extract_data_list('Themes', data)
  locations = extract_locations(data)

  url = str(data['DocumentIdentifier'])
  # language, kwds = get_article_params(url)

  # Object Creation
  people_ids = [find_or_create_actor(db=db, actor_type=TYPE_PERSON, actor_name=name) for name in people_names]
  org_ids = [find_or_create_actor(db=db, actor_type=TYPE_ORGANIZATION, actor_name=name) for name in org_names]
  actor_ids = people_ids+org_ids

  article_id = create_article(
    db=db,
    url=url,
    date=date,
    locations=locations,
    actor_ids=actor_ids,
    # language=language,
    # keywords=kwds,
    gkg_themes=gkg_themes)

  return article_id, actor_ids

def create_article(db, url=None, date=None, language=None,
  locations=None, actor_ids=None, keywords=None, gkg_themes=None):
  article_collection = db.test_article_collection
  article = {
    'url': url,
    'date': date,
    'language': language,
    'locations': locations,
    'actor_ids': actor_ids,
    'keywords': keywords,
    'gkg_themes': gkg_themes,
  }
  article_id = article_collection.insert_one(article).inserted_id
  return article_id

def extract_locations(data):
  '''
  Exracts locations from a row in data
  '''
  locationStr = str(data['Locations'])
  if locationStr == 'nan':
    return None
  else:
    location_infos = [location.split('#') for location in locationStr.split(';')]
    locations = [format_loc_info(loc) for loc in location_infos]
  return locations

def format_loc_info(loc):
  '''
  Converts a location in GDelt to a GDeltLocation class
  '''
  loc_type, name, latitude, longitude = loc[0], loc[1], float(loc[4]), float(loc[5])
  return {
    'name': name,
    'loc_type': loc_type,
    'loc': {
      'type': 'Point',
      'coordinates': [longitude, latitude]
    }
  }

def find_or_create_actor(db, actor_type, actor_name):
  actor_collection = db.test_actor_collection

  # find an actor with the existing name
  met_name = metaphone_name(actor_name)
  existing_actor = actor_collection.find_one({'met_name': met_name})
  if not existing_actor:
    actor = {
      'actor_type': actor_type,
      'actor_name': actor_name,
      'met_name': met_name
    }
    actor_id = actor_collection.insert_one(actor).inserted_id
    return actor_id
  else:
    return existing_actor['_id']

def extract_data_list(field_name, data):
  '''
  extracts list from fieldNames
  '''
  return list(filter(lambda x: x != 'nan' and x != '', str(data[field_name]).split(';')))

def get_article_params(url):
  SENTENCE_COUNT=4
  text = extractText(url)
  language = languages.get(alpha_2=detect(text)).name

  r = Rake(language, max_length=3)
  r.extract_keywords_from_text(text)

  kwds = r.get_ranked_phrases()[:10]

  return language, kwds

def extractText(url):
  try:
    with urllib.request.urlopen(url) as url:
      html = url.read()

    soup = BeautifulSoup(html, "html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    # get text
    text = soup.body.get_text(separator=' ')
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text
  except:
    return ''