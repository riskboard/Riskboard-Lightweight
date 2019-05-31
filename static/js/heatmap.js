const initialize_heatmap = (heatmap) => {
  mapbox_token = 'pk.eyJ1IjoicmpheTk4IiwiYSI6ImNqd2FkOWE5NDA4cjEzemtkNGlkNmxqaTUifQ.Zglo0zZl1zOEf0tYynhfzw'
  L.tileLayer(`https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=${mapbox_token}`, {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: mapbox_token,
  }).addTo(heatmap);
};

const initialize_locations = (heatmap, form_data, article_data) => {
  objects = form_data.locations.map( (el, i) => {
    if (!el.coordinates) {
      return (null, null);
    };
    var marker = L.marker(el.coordinates.reverse()).addTo(heatmap);
    let markerContent = `<b>${el.name}</b>` + 
      article_data[i].articles.map( (el, j) => 
      `<div><a href="${el.url}">(${j+1}) ${el.url} </a></div>`
      ).join('');
    marker.bindPopup(markerContent);
    var circle = L.circle(el.coordinates, {
      color: 'red',
      fillColor: '#f03',
      fillOpacity: 0.5,
      radius: article_data[i].count*5000,
    }).addTo(heatmap);
    return (marker, circle);
  });
};

const initialize_page = () => {
  $.get({
    url: '/dashboard',
    data: { 'render': false },
    xhrFields: {
      withCredentials: true,
    }
  }).then((data) => {
    const form_data = data.form_data;
    const article_data = JSON.parse(data.article_data);
    var heatmap = L.map('mapid').setView([0,0], 2);
    initialize_heatmap(heatmap);
    initialize_locations(heatmap, form_data, article_data);
  });
};

$(() => {
  initialize_page();
})