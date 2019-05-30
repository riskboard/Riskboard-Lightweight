var form_data;

let get_form_data = (data) => {
  form_data = data;
  console.log(form_data);
};

let initialize_heatmap = (heatmap) => {
  mapbox_token = 'pk.eyJ1IjoicmpheTk4IiwiYSI6ImNqd2FkOWE5NDA4cjEzemtkNGlkNmxqaTUifQ.Zglo0zZl1zOEf0tYynhfzw'
  L.tileLayer(`https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=${mapbox_token}`, {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: mapbox_token,
  }).addTo(heatmap);
};

let initialize_locations = (heatmap) => {
  objects = form_data.locations.map( (el, i) => {
    if (!el.latitude | !el.longitude) {
      return (null, null);
    };
    var marker = L.marker([el.longitude, el.latitude]).addTo(heatmap);
    marker.bindPopup(el.name).openPopup();
    var circle = L.circle([el.longitude, el.latitude], {
      color: 'red',
      fillColor: '#f03',
      fillOpacity: 0.5,
      radius: 50000
    }).addTo(heatmap);
    return (marker, circle);
  });
};

$(() => {
  console.log('Document Ready');
  var heatmap = L.map('mapid').setView([0.0,0.0], 2);
  initialize_heatmap(heatmap);
  initialize_locations(heatmap);
});