$(() => {
  let num_inputs = $("input[name='num_locations']").val();

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

  $('.dropdown-button').on('click', () => {
    num_inputs += 1;
    $('#location-inputs').append(input_field(num_inputs));
    $("input[name='num_locations']").val(num_inputs);
  });

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

  $('#theme-selector').html(
    themes.map(theme_field).join('')
  );

  var selected_themes;

  $('.theme-circle').on('click', (e) => {
    $(e.target).toggleClass('selected');

    selected_themes = $('.theme-circle.selected').map((_, el) => $(el).attr('id')).get();
  });

  $('#profile-form').on('submit', (e) => {
    // prevent event default
    e.preventDefault();

    if (!selected_themes || selected_themes.length < 5) {
      $('#theme-error').html(`<i class="fas fa-exclamation-triangle"></i> Please select at least 5 themes.`); 
    };

    [loc_data, errors] = get_loc_data();
    if (errors.length) {
      var merged_error = errors.join(' ');
      $('#location-error').html(`
      <i class="fas fa-exclamation-triangle"></i> ${merged_error}`);
      return false;
    };
  });
});

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