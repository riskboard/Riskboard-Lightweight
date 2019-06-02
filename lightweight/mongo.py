import os
from lightweight import app

#  Initialize database client
from pymongo import MongoClient

# configure for hosting
APP_ENV = os.environ.get('APP_ENV')

if not APP_ENV:
  print('No APP_ENV set. Loading default mongo client...')
  # default vars for local testing
  client = MongoClient()
  db = client.test_database
else:
  MONGODB_URI = os.environ.get('MONGODB_URI')
  MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
  MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
  MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE')
  app.config['MONGODB_URI'] = MONGODB_URI
  app.config['MONGODB_USERNAME'] = MONGODB_USERNAME
  app.config['MONGODB_PASSWORD'] = MONGODB_PASSWORD
  app.config['MONGODB_DATABASE'] = MONGODB_DATABASE
  client = MongoClient(MONGODB_URI)
  db = client[MONGODB_DATABASE]
  db.authenticate(MONGODB_USERNAME, MONGODB_PASSWORD)