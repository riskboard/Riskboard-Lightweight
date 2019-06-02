from pymongo import GEOSPHERE, DESCENDING, IndexModel, TEXT
from datetime import datetime

from .gkg_processor import update_db_gkg

class DataProcessor():
  '''
  Creates a DataCenter.
  A DataCenter is a MongoDB instance specific to
  a client's needs, tailored to their interests and regions
  '''

  def __init__(self, query=None, db=None):
    '''
    Initializes a new DataCenter populated with data
    from the specified start date (inclusive) to the end date (exclusive)

    The data will be populated by data from specified geographies, as well
    as the specified actors involved in each geographies. Geographies are defined
    by the Region class.

    If no actors are specified, all actors will be included.

    Dates should be formatted as follows:
    'YYYY-MM-DD'
    e.g. '2019-02-19'
    '''
  
    print('Starting Data Processor')

    self.format_query(query)
    self.initialize_database(db)

    # Update with GKG Data
    update_db_gkg(query, db)

    print('Data Loaded')

  def format_query(self, query):
    '''
    Formats query to ensure correct types
    '''
    # initialize query
    self.query = query

    # convert query to datetime
    self.query['startDate'] = datetime.strptime(query['startDate'], '%m/%d/%Y')
    self.query['endDate'] = datetime.strptime(query['endDate'], '%m/%d/%Y')

  def initialize_database(self, db):
    '''
    Initializes database and ensures indices are correct
    '''
    # initialize database
    self.db = db

    # ensure dates are indexed
    dataframe_coll = db.test_dataframe_collection
    dataframe_coll.create_index([('data_time', DESCENDING)])

    # initialize location index
    article_collection = db.test_article_collection
    location_index = IndexModel([('geometry', GEOSPHERE)])
    text_index = IndexModel([('properties.url', TEXT), ('properties.rb_themes', TEXT)])
    article_collection.create_indexes([location_index, text_index])