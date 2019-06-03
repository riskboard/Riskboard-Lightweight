var selected_themes;

$(() => {
  // set number of location inputs
  let num_inputs = current_profile.locations
    ? current_profile.locations.length
    : 3;

  $('.dropdown-button').on('click', () => {
    num_inputs += 1;
    $('#location-inputs').append(input_field(num_inputs));
    $("input[name='num_locations']").val(num_inputs);
  });

  $('#theme-selector').html(
    themes.map(theme_field).join('')
  );

  $('.theme-circle').on('click', (e) => {
    $(e.target).toggleClass('selected');

    selected_themes = $('.theme-circle.selected').map((_, el) => $(el).attr('id')).get();
  });

  $('#profile-form').on('submit', (e) => {
    // prevent event default
    e.preventDefault();

    // clear existing warnings
    $('.warning-text').empty();

    // validate and get data
    form_data = get_valid_data()
    console.log(form_data);

    // change request type based on whether or not current profile exists
    current_profile ? put_profile(form_data, callback) : post_profile(form_data, callback);
  });

  // populate current_profile
  current_profile ? populate_current_profile() : null;
});

const input_field = (i) => {
  return `
  <div class="input-group mt-2">
    <div class="input-group-prepend">
      <span class="input-group-text text-light">Location Information</span>
    </div>
    <input type="text" class="form-control" name="location_name_${i}" id="location_name_${i}" placeholder="Name of City or Location">
    <input type="text" class="form-control" name="location_long_${i}" id="location_long_${i}" placeholder="Longitude">
    <input type="text" class="form-control" name="location_lat_${i}" id="location_lat_${i}" placeholder="Latitude">
  </div>
`;
};

const theme_field = (theme) => {
  return `
    <div class="theme-circle-container m-2">
      <div class="theme-circle p-2" id="${theme}">${theme}</div>
    </div>
  `
};

const themes = ['Atrocity', 'Conflict', 'Cyber', 'Disaster',
  'Discrimination', 'Dissent', 'Energy', 'Economy', 'Environment',
  'Ethnic', 'Food', 'Government', 'Health', 'Information',
  'Infrastructure', 'Investment', 'IR', 'Media', 'Military',
    'Law Enforcement', 'Leadership', 'Organized Crime',
  'People', 'Politics', 'Religion', 'Social', 'Sovereignty',
  'Technology', 'Terrorism', 'Trade', 'Violence', 'Weaponry']

const get_valid_data = () => {
  if (!selected_themes || selected_themes.length < 5) {
    $('#theme-error').html(`<i class="fas fa-exclamation-triangle"></i> Please select at least 5 themes.`);
    return false;
  };

  [loc_data, errors] = get_loc_data();
  if (errors.length) {
    var merged_error = errors.join(' ');
    $('#location-error').html(`
    <i class="fas fa-exclamation-triangle"></i> ${merged_error}`);
    return false;
  };

  name = $('input[name="company_name"').val();

  form_data = {
    'company_name': name,
    'relevant_themes': selected_themes,
    'locations': loc_data,
  };

  return JSON.stringify(form_data);
};

const callback = (response) => {
  if (response.status == '200') {
    // TODO: create alerts
  }
};

const post_profile = (form_data, callback) => {
  // send POST request to server
  $.post({
    'url': '/profile',
    'data': form_data,
    'contentType': 'application/json',
    'dataType': 'json',
  }, callback);
};

const put_profile = (form_data, callback) => {
  // send PUT request to server
  $.ajax({
    'method': 'PUT',
    'url': '/profile',
    'data': form_data,
    'contentType': 'application/json',
    'dataType': 'json',
  }, callback);
};

const get_loc_data = () => {
  var loc_data = [];
  var errors = [];

  // validate location information
  const validate_loc = (loc_json) => {
    var is_valid = true;
    name = loc_json.name;
    [long, lat] = loc_json.coordinates;
    if (!long && !lat && !name) {
      return false;
    }
    if (long < -180 || lat > 180) {
      errors.push('Invalid longitude.');
      is_valid = false;
    }
    if (lat < -90 || lat > 90) {
      errors.push('Invalid latitude.');
      is_valid = false;
    }
    if (typeof(name) != 'string') {
      errors.push('Invalid name.');
      is_valid = false;
    }
    return is_valid;
  };

  // validate location information and create geoJSON
  $('.location-information').map((_, el) => {
    var loc_array = $(el).children(':input').map((_, i) => { return i.value});
    var loc_json = {
      'name': loc_array[0],
      'coordinates': [loc_array[1], loc_array[2]]
    };
    // if valid, push to loc_data
    validate_loc(loc_json) ? loc_data.push(loc_json) : false;
  });

  if (loc_data.length == 0) {
    errors.push('Please input at least one valid location.')
  };

  return [loc_data, errors];
};

const populate_current_profile = () => {
  // fill company name
  $('#company_name').val(current_profile.company_name);

  // select themes
  current_profile.relevant_themes.forEach((t) => {
    $(`.theme-circle[id="${t}"]`).toggleClass('selected');
  });
  selected_themes = current_profile.relevant_themes;

  // fill locations
  current_profile.locations.forEach((loc, id) => {
    location_fields = $(`.location-information:eq(${id}) :input`);
    console.log(location_fields[0]);
    location_fields[0].value = loc.name;
    location_fields[1].value = loc.coordinates[0];
    location_fields[2].value = loc.coordinates[1];
  });
};