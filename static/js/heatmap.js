var map;
var form_data;
var article_data;
var active_location_id;

const initialize_heatmap = () => {
  mapboxgl.accessToken = 'pk.eyJ1IjoicmpheTk4IiwiYSI6ImNqd2FkOWE5NDA4cjEzemtkNGlkNmxqaTUifQ.Zglo0zZl1zOEf0tYynhfzw';
  map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/dark-v9', // stylesheet location
    zoom: 1,
    maxZoom: 10,
    minZoom: 1,
    center: [0,0],
  });
  map.on('load', initialize_locations);
};

var size=100;

var pulsingDot = {
  width: size,
  height: size,
  data: new Uint8Array(size * size * 4),

  onAdd: function() {
    var canvas = document.createElement('canvas');
    canvas.width = this.width;
    canvas.height = this.height;
    this.context = canvas.getContext('2d');
  },

  render: function() {
    var duration = 1000;
    var t = (performance.now() % duration) / duration;

    var radius = size / 2 * 0.3;
    var outerRadius = size / 2 * 0.7 * t + radius;
    var context = this.context;

    // draw outer circle
    context.clearRect(0, 0, this.width, this.height);
    context.beginPath();
    context.arc(this.width / 2, this.height / 2, outerRadius, 0, Math.PI * 2);
    context.fillStyle = 'rgba(255, 200, 200,' + (1 - t) + ')';
    context.fill();

    // draw inner circle
    context.beginPath();
    context.arc(this.width / 2, this.height / 2, radius, 0, Math.PI * 2);
    context.fillStyle = 'rgba(255, 100, 100, 1)';
    context.strokeStyle = 'white';
    context.lineWidth = 2 + 4 * (1 - t);
    context.fill();
    context.stroke();

    // update this image's data with data from the canvas
    this.data = context.getImageData(0, 0, this.width, this.height).data;

    // keep the map repainting
    map.triggerRepaint();

    // return `true` to let the map know that the image was updated
    return true;
  }
};

const initialize_locations = () => {
  map.addImage('pulsing-dot', pulsingDot, { pixelRatio: 2 });

  const location_points = form_data.locations.map( (el, id) => {
    if (!el.coordinates) {
      return (null, null);
    };
    return {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": el.coordinates
      },
      "properties": {
        "title": el.name,
        "id": id,
      },
    }
  });

  map.addLayer({
    "id": "locations",
    "type": "symbol",
    "source": {
      "type": "geojson",
      "data": {
        "type": "FeatureCollection",
        "features": location_points,
      }
    },
    "layout": {
      "icon-image": "pulsing-dot",
      "text-field": "{title}",
      "text-font": ["DIN Offc Pro Medium"],
      "text-offset": [0, 0.6],
      "text-anchor": "top",
      "text-size": 12,
    },
    "paint": {
      "text-color": "#ffffff",
    },
  });

  map.on('click', 'locations', (e) => {
    active_location_id = e.features[0].properties.id;
    $('#locationModal').modal('toggle');
  });
};

const refresh_data = (timeScale) => {
  $.get({
    url: '/dashboard',
    data: {
      'render': false,
      'time_scale': 1,
    },
    xhrFields: {
      withCredentials: true,
    }
  }).then((data) => {
    form_data = data.form_data;
    article_data = JSON.parse(data.article_data);
    initialize_heatmap();
  });
};

$(() => {
  initial_time_scale='day';
  refresh_data(initial_time_scale);
})

$('#timeScaleSelect').on('change', () => {
  refresh_data(this.value);
});

//triggered when modal is about to be shown
$('#locationModal').on('show.bs.modal', function(e) {
  // populate the textbox
  $('#locationModal .modal-title').text(form_data.locations[active_location_id].name);
});