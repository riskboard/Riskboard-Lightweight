import requests
import os
import pandas as pd
import json
import heapq
from collections import defaultdict

class ArticleProcessor():
  def __init__(self, profile):
    self.locations = profile['locations']
    self.relevant_themes = profile['relevant_themes']
    self.relevant_theme_set = set(profile['relevant_themes'])
    self.gkg_theme_dict = self._get_gkg_theme_dict()

  def process_query(self, timespan=1440):
    '''
    Returns a list of objects corresponding to each
    location in the profile.

    For each object, it includes
    1. A list of relevant themes
    2. Inside of each theme, a list of relevant articles, sorted by tone
    '''
    query_result = []
    for loc in self.locations:
      theme_dict = defaultdict(list)
      GKG_URL = 'https://api.gdeltproject.org/api/v1/gkg_geojson'
      query_url = f'{GKG_URL}?QUERY=geoname:{loc["name"]}&OUTPUTTYPE=1&OUTPUTFIELDS=name,url,domain,sharingimage,tone,themes&TIMESPAN={timespan}'
      print(query_url)
      loc_data = json.loads(requests.get(query_url).text)

      for article in loc_data['features']:
        props = article['properties']
        gkg_themes = props['mentionedthemes'].split(';')
        rb_themes = self._convert_themes(gkg_themes)
        filtered_themes = list(self.relevant_theme_set & set(rb_themes))
        for t in filtered_themes:
          heapq.heappush(theme_dict[t], (props['urltone'], props['url'], props['urlsocialimage']))
      query_result.append((loc['name'], theme_dict))
    return query_result

  def _get_gkg_theme_dict(self):
    gkg_theme_dict = {}
    df = pd.read_csv(f'{os.getcwd()}/lightweight/utils/gkg_theme_info.csv')
    for index, row in df.iterrows():
      gkg_theme_dict[row.Name] = row.RB_Theme.split(';')
    return gkg_theme_dict

  def _convert_themes(self, gkg_themes):
    if not gkg_themes: return []

    def convert_theme(gkg_theme):
      if not gkg_theme in self.gkg_theme_dict: return None
      return self.gkg_theme_dict[gkg_theme]

    themes = set()
    converted = [themes.update(y) for y in (convert_theme(t) for t in gkg_themes) if y is not None]
    return list(themes)