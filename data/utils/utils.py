from datetime import datetime, timedelta
from metaphone import doublemetaphone
import numpy as np
import pandas as pd

def get_date_time_obj(date):
  '''
  Creates a datetime object corresponding to a specified date string
  Dates should be formatted as follows:
  'YYYY-MM-DD'
  e.g. '2019 02 19'
  '''
  return datetime.strptime(date, '%Y-%m-%d')

def get_date_from_string(date_string):
  return f'{date_string[:4]}-{date_string[4:6]}-{date_string[6:8]}'

def get_date_string_list(date_obj, interval=15):
  '''
  Converts a given date into a string.

  Dates should be formatted as follows:
  'YYYY MM DD'
  e.g. '2019 02 19'

  Output:
  ['YYYYMMDD000000', 'YYYYMMDD001500', ..., 'YYYYMMDD234500']
  Default corresponds to the 15-minute intervals of a given day
  for access in the GDelt GKG 2.0
  '''
  # generate numbers
  time_nums = np.arange(0, 236000, interval*100)
  # generate dateString
  date_string = date_obj.strftime("%Y%m%d")
  # return as a list of formatted strings
  return [f'{date_string}{time_num:06}' for time_num in time_nums]

def date_range(start_date_obj, end_date_obj):
  '''
  Creates an iterable of dates corresponding to
  given start date object and end date object, inclusive.
  '''
  for n in range(int ((end_date_obj - start_date_obj).days)):
    yield start_date_obj + timedelta(n)

def get_date_range_strings(start_date, end_date):
  '''
  Creates a list of strings, corresponding to 15-minute intervals
  from the specified start date to end date, inclusive of the first,
  exclusive of the second
  '''
  start_date_obj = get_date_time_obj(start_date)
  end_date_obj = get_date_time_obj(end_date)
  output = []
  for date in date_range(start_date_obj, end_date_obj):
    output += get_date_string_list(date)
  return output

def get_date_url(date_string):
  '''
  Returns the corresponding GDelt 2.0 GKG URL
  '''
  return f'http://data.gdeltproject.org/gdeltv2/{date_string}.translation.gkg.csv.zip'

def get_schema_headers(schema='datacenter/utils/schema.csv'):
  '''
  Returns headers for dataframe
  '''
  return ['GKGRECORDID', 'DATE', 'SourceCollectionIdentifier', 'SourceCommonName', 'DocumentIdentifier', 'Counts', 'V2Counts', 'Themes', 'V2Themes', 'Locations', 'V2Locations', 'Persons', 'V2Persons', 'Organizations', 'V2Organizations', 'V2Tone', 'Dates', 'GCAM', 'SharingImage', 'RelatedImages', 'SocialImageEmbeds', 'SocialVideoEmbeds', 'Quotations', 'AllNames', 'Amounts', 'TranslationInfo', 'Extras']

def format_actors(actors):
  '''
  returns a list of lowercase actor names
  '''
  if not actors: return None
  return [actor.lower() for actor in actors]

def metaphone_name(name):
  '''
  returns the double metaphone abbreviation of a name
  '''
  metaphone_name = doublemetaphone(name)
  return (metaphone_name[0] + metaphone_name[1])
