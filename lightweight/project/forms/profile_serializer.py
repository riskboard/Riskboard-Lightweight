from flask import session

# TODO: Refactor this into a Serializer
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

  def inject_test_data(form_data):
    form_data['company_name'] = 'New Balance'
    form_data['email'] = 'rjiang@hpair.org'
    form_data['locations'] = [
      {'name': 'Bangkok', 'coordinates': [100.5018, 13.7563]},
      {'name': 'New York', 'coordinates': [-73.935242, 40.7306]},
      {'name': 'Shanghai', 'coordinates': [121.4737, 31.2304]},
    ]
    form_data['relevant_themes'] = ['Environment', 'Social', 'Government', 'Conflict', 'Law Enforcement', 'Information', 'Technology']
    return form_data

  form_data['relevant_themes'] = form_data['relevant_themes'].split(',')
  # form_data = inject_test_data(form_data)

  return form_data