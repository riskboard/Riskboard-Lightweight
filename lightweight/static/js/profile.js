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
    'Miscellaneous', 'Law Enforcement', 'Leadership', 'Organized Crime',
    'People', 'Politics', 'Religion', 'Social', 'Sovereignty',
    'Technology', 'Terrorism', 'Trade', 'Violence', 'Weaponry']

  $('#theme-selector').html(
    themes.map(theme_field).join('')
  );

  $('.theme-circle').on('click', (e) => {
    $(e.target).toggleClass('selected');

    var selected = $('.theme-circle.selected').map((_, el) => {
      return $(el).attr('id');
    }).get();

    $("input[name='relevant_themes']").val(selected);
  });
});