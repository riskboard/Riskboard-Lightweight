import json
from flask import session

class ProfileSerializer():
  def __init__(self, current_user):
    '''
    Initializes a profile serializer object
    '''
    self.user_id = current_user.get_id()

  def parse(self, request):
    '''
    Parses the profile request into python object
    '''
    data = json.loads(request.data)
    company_name = data['company_name']
    themes = data['relevant_themes']
    locations = data['locations']
    keywords = data['keywords']

    data = {
      '_id': self.user_id,
      'company_name': company_name,
      'relevant_themes': themes,
      'locations': locations,
      'keywords': keywords
    }

    # data = self.inject_test_data(data)

    return data

  def inject_test_data(self, data):
    '''
    Injects test locations into data
    '''
    data['company_name'] = 'New Balance'
    data['locations'] = [
      {'name': 'Bangkok', 'coordinates': [100.5018, 13.7563]},
      {'name': 'New York', 'coordinates': [-73.935242, 40.7306]},
      {'name': 'Shanghai', 'coordinates': [121.4737, 31.2304]},
    ]
    data['relevant_themes'] = ['Environment', 'Social', 'Government', 'Conflict', 'Law Enforcement', 'Information', 'Technology']
    return data