import os
import urllib
import numpy as np
import pandas as pd
from datetime import datetime
from metaphone import doublemetaphone
# from bs4 import BeautifulSoup
# from pycountry import languages
# from langdetect import detect
# from rake_nltk import Rake

from ..utils.gkg_utils import (get_time_from_gkg, metaphone_name,
  get_gkg_schema_headers, get_date_time_obj, get_date_strings, get_date_url)

TYPE_ORGANIZATION = 'Organization'
TYPE_PERSON = 'Person'

def get_gkg_theme_dict():
  gkg_theme_dict = {}
  df = pd.read_csv(f'{os.getcwd()}/data/utils/gkg_theme_info.csv')
  for index, row in df.iterrows():
    gkg_theme_dict[row.Name] = row.RB_Theme.split(';')
  return gkg_theme_dict

gkg_theme_dict = get_gkg_theme_dict()

def convert_themes(gkg_themes):
  if not gkg_themes: return []
  def convert_theme(gkg_theme):
    if not gkg_theme in gkg_theme_dict: return None
    return gkg_theme_dict[gkg_theme]
  themes = set()
  converted = [themes.update(y) for y in (convert_theme(t) for t in gkg_themes) if y is not None]
  return list(themes)

def update_db_gkg(query, db):
  init_date_strings = get_date_strings(query['startDate'], query['endDate'])
  [update_database(date_string, db) for date_string in init_date_strings]
  return True

def update_database(date_string, db):
  '''
  Updates the database with information from a single day
  '''
  print(f'* Processing {date_string} Information...')

  # get datetime obj
  date = get_time_from_gkg(date_string)

  collection = db.test_dataframe_collection

  # if dataframe has been indexed, skip
  query = {'data_time': date}
  cursor = collection.find_one(query)
  if cursor:
    print (f"Already processed at ${cursor['indexed_time']}")
    return True

  success, df = get_gkg_dataframe(date_string)
  if not success:
    print('Dataframe not successfully read.')
    return False

  total_count = len(df)
  print(f'** {total_count} Rows')

  df.apply(lambda row: extract_gkg_data(row, date, db), axis=1)

  # store that dataframe has been indexed
  collection.insert_one({
    'data_time': date,
    'indexed_time': datetime.now()
  })

  print(f'  {date_string} processed.')
  return True

def get_gkg_dataframe(date_string):
  try:
    # get data url
    url = get_date_url(date_string)

    # read in data file
    df = pd.read_csv(url, compression='zip', encoding='latin1', header=None, sep='\t')
    df.columns =  get_gkg_schema_headers()
    return True, df
  except Exception as e:
    return False, None

def extract_gkg_data(data, date, db):
  '''
  Extracts the url, people, organizations, and location from
  one row in the GKG dataframe
  '''
  people_names = extract_data_list('Persons', data)
  org_names = extract_data_list('Organizations', data)
  actor_names = people_names+org_names

  gkg_themes = extract_data_list('Themes', data)
  rb_themes = convert_themes(gkg_themes)

  locations = extract_locations(data)

  social_video_embeds = len(extract_data_list('SocialVideoEmbeds', data))
  social_image_embeds = len(extract_data_list('SocialImageEmbeds', data))
  tone, positive_score, negative_score, polarity, _, self_reference_density, word_count = get_tone_params(data)

  # TODO: Improve relevancy score
  relevancy_score = (social_video_embeds+social_image_embeds+30)*negative_score*(word_count/200+4)*(np.exp(-self_reference_density))

  url = str(data['DocumentIdentifier'])
  # language, kwds = get_article_params(url)

  # Object Creation
  people_ids = [find_or_create_actor(db=db, actor_type=TYPE_PERSON, actor_name=name) for name in people_names]
  org_ids = [find_or_create_actor(db=db, actor_type=TYPE_ORGANIZATION, actor_name=name) for name in org_names]
  actor_ids = people_ids+org_ids

  article = {
    'type': 'Feature',
    'properties': {
      'url': url,
      'date': date,
      'actor_ids': actor_ids,
      'gkg_themes': gkg_themes,
      'rb_themes': rb_themes,
      'tone': tone,
      'positive_score': positive_score,
      'negative_score': negative_score,
      'polarity': polarity,
      'relevancy_score': relevancy_score,
      'word_count': word_count,
      'self_reference_density': self_reference_density
    },
  }

  article['geometry'] = {
    'type': 'MultiPoint',
    'coordinates': locations
  } if locations else None

  article_id = find_or_create_article(db, article)

  return article_id, actor_ids

def find_or_create_article(db, article):
  article_collection = db.test_article_collection
  # ensure unique articles
  cursor = article_collection.find_one({'url': article['properties']['url']})
  if not cursor:
    article_id = article_collection.insert_one(article).inserted_id
    return article_id
  return cursor['_id']

def get_tone_params(data):
  '''
  Gets tone parameters
  '''
  tone_params = [float(x) if x != 'nan' else 0 for x in str(data['V2Tone']).split(',')]
  # ensure proper length
  return tone_params if len(tone_params)==7 else [0]*7

def extract_locations(data):
  '''
  Exracts locations from a row in data
  '''
  locationStr = str(data['Locations'])
  if locationStr == 'nan':
    return None
  else:
    location_infos = [location.split('#') for location in locationStr.split(';')]
    locations = [l for l in (format_loc_info(loc) for loc in location_infos) if l is not None]
  return locations

def format_loc_info(loc):
  '''
  Converts a location in GDelt to a GDeltLocation class
  '''
  for el in loc:
    if el == '': return None

  loc_type, name, latitude, longitude = loc[0], loc[1], float(loc[4]), float(loc[5])
  return [longitude, latitude]

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

def extract_data_list(field_name, data, sep=';'):
  '''
  extracts list from fieldNames
  '''
  return list(filter(lambda x: x != 'nan' and x != '', str(data[field_name]).split(sep)))

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