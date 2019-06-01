from datetime import datetime, timedelta
from metaphone import doublemetaphone
import numpy as np
import pandas as pd

def get_time_from_gkg(date_string):
  '''
  Converts dataframe time string to real datetime
  '''
  return datetime.strptime(date_string[:12], '%Y%m%d%H%M')

def get_date_time_obj(date):
  '''
  Creates a datetime object corresponding to a specified date string
  Dates should be formatted as follows:
  'YYYY-MM-DD'
  e.g. '2019 02 19'
  '''
  return datetime.strptime(date, '%m/%d/%Y')

def datetime_range(start, end, delta):
  current = start
  while current < end:
    yield current
    current += delta

def get_date_strings(start_date, end_date):
  '''
  Creates a list of strings, corresponding to 15-minute intervals
  from the specified start date to end date, inclusive of the first,
  exclusive of the second
  '''
  times = ([f"{dt.strftime('%Y%m%d%H%M')}00" for dt in datetime_range(start_date, end_date, timedelta(minutes=15))])
  return times

def get_date_url(date_string):
  '''
  Returns the corresponding GDelt 2.0 GKG URL
  '''
  return f'http://data.gdeltproject.org/gdeltv2/{date_string}.translation.gkg.csv.zip'

def get_gkg_schema_headers(schema='datacenter/utils/gkg_schema.csv'):
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
