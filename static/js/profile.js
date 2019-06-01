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
});