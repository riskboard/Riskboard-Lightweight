import os
import json
from collections import Counter

import pymongo
from flask import Flask
from flask import (render_template, session, request,
  redirect, url_for, abort, jsonify)
from flask_wtf.csrf import CSRFProtect

from bson.json_util import loads, dumps

from data.processor.data_processor import DataProcessor

# Initialize app
app = Flask(__name__)

# Protect with CSRF
# csrf = CSRFProtect(app)

app.config.update(
  # Set secret key
  SECRET_KEY = os.urandom(32),
  # WTF_CSRF_ENABLED = True,
  DEBUG = True,
)

# Initialize database client
from pymongo import MongoClient

# configure for hosting
MONGODB_URI = os.environ.get('MONGODB_URI')
print('MONGODB_URI', MONGODB_URI)
if MONGODB_URI:
  app.config['MONGODB_URI'] = MONGODB_URI
  client = MongoClient(MONGODB_URI)
else:
  client = MongoClient()

db = client.test_database

@app.route('/database', methods=["POST", "GET"])
def database():
  if request.method == 'GET':
    return render_template('database.html')
  elif request.method == 'POST':
    query = request.form.to_dict()
    processor = DataProcessor(query=query, db=db)
    return redirect(url_for('index'))

@app.route('/')
def index():
  return render_template('index.html')

def initialize_form_data(form_data):
  form_data['num_locations'] = int(form_data['num_locations'])

  def make_location(form_data, id):
    name = form_data[f'location_name_{str(id)}']
    coordinates = [form_data[f'location_long_{str(id)}'], form_data[f'location_lat_{str(id)}']]
    if name == '' or coordinates[0] == '' or coordinates[1] == '':
      return None
    return {
      'name': name,
      'coordinates': coordinates
    }

  form_data['locations'] = [
    y for y in (
      make_location(form_data, i) for i in range(1, form_data['num_locations'])
    ) if y is not None ]

  form_data['company_name'] = 'New Balance'
  form_data['email'] = 'rjiang@hpair.org'
  form_data['locations'] = [
    {'name': 'Bangkok', 'coordinates': [100.5018, 13.7563]},
    {'name': 'New York', 'coordinates': [-73.935242, 40.7306]},
    {'name': 'Shanghai', 'coordinates': [121.4737, 31.2304]},
  ]

  form_data['relevant_themes'] = None

  # store form data
  session['form_data'] = form_data
  return form_data

def get_article_data(form_data):
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
    query = {
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

    if relevant_themes and relevant_themes != []:
      query['rb_themes'] = {
        '$in': relevant_themes
      }

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
        list(article['properties']['rb_themes']) & relevant_theme_set)
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

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
  if request.method == 'GET':
    form_data = session['form_data']
    article_data = get_article_data(form_data)
    if request.args.get('render') == 'false':
      return jsonify({
        'form_data': form_data,
        'article_data': dumps(article_data),
      })
  else:
    form_data = initialize_form_data(request.form.to_dict())
    article_data = get_article_data(form_data)
  return render_template('dashboard.html', form_data=form_data, article_data=article_data)