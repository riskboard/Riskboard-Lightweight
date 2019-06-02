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
  app.config.update(
    MONGODB_URI = os.environ.get('MONGODB_URI'),
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME'),
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD'),
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE'),
  )
  client = MongoClient(app.config['MONGODB_URI'])
  db = client[app.config['MONGODB_DATABASE']]
  db.authenticate(app.config['MONGODB_USERNAME'], app.config['MONGODB_PASSWORD'])