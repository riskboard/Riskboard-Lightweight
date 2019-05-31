import os
import json
from collections import Counter

from flask import Flask
from flask import (render_template, session, request,
  redirect, url_for, abort, jsonify)
from flask_wtf.csrf import CSRFProtect

from bson.json_util import loads, dumps

from .data.processor.gkg_processor import GKGProcessor

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
client = MongoClient()
db = client.test_database

@app.route('/database', methods=["POST", "GET"])
def database():
  if request.method == 'GET':
    return render_template('database.html')
  elif request.method == 'POST':
    query = request.form.to_dict()
    processor = GKGProcessor(query=query, db=db)
    return redirect(url_for('index'))

@app.route('/')
def index():
  return render_template('index.html')

def initialize_form_data(form_data):
  form_data['num_locations'] = int(form_data['num_locations'])

  def make_location(form_data, id):
    return {
      'name': form_data[f'locationName{str(id)}'],
      'coordinates': [form_data[f'locationLong{str(id)}'], form_data[f'locationLat{str(id)}']]
    }

  form_data['locations'] = [make_location(form_data, i) for i in range(1, form_data['num_locations'])]

  form_data['companyName'] = 'New Balance'
  form_data['email'] = 'rjiang@hpair.org'
  form_data['locations'] = [
    {'name': 'Bangkok', 'coordinates': [100.5018, 13.7563]},
    {'name': 'New York', 'coordinates': [-73.935242, 40.7306]},
    {'name': 'Shanghai', 'coordinates': [121.4737, 31.2304]},
  ]

  # store form data
  session['form_data'] = form_data
  return form_data

def get_article_data(form_data):
  article_collection = db.test_article_collection

  def get_nearby_articles(location):
    # TODO: Implement relevancy score
    location_query = {
      'locations.loc': {
        '$near': {
          '$geometry': {
            'type': 'Point',
            'coordinates': location['coordinates'],
          },
        '$maxDistance': 5000,
        }
      }
    }
    theme_group = {
      '$group': {'gkg_themes'}
    }
    near_articles = article_collection.find(location_query)
    if not near_articles:
      return {
        'count': 0,
        'top_articles': [],
        'themes': [],
      }

    near_articles = list(near_articles)

    gkg_theme_counter = Counter()
    for article in near_articles:
      gkg_theme_counter.update(article['gkg_themes'])

    # TODO: Filter by relevancy
    return {
      'count': len(near_articles),
      'articles': near_articles[:10],
      'themes': gkg_theme_counter.most_common(5)
    }

  article_data = [get_nearby_articles(location) for location in form_data['locations']]
  return article_data

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
  if request.method == 'GET':
    form_data = session['form_data']
    article_data = get_article_data(form_data)
    if request.args.get('render') == 'false':
      return jsonify({
        'form_data': form_data,
        'article_data': dumps(article_data)
      })
  else:
    form_data = initialize_form_data(request.form.to_dict())
    article_data = get_article_data(form_data)
  return render_template('dashboard.html', form_data=form_data, article_data=article_data)