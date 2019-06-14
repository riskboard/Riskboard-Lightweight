var map;

$(() => {
  initialize_map();

  $('#location-select').on('change', () => {
    active_location_id = $('#location-select').find(':selected').val();
    console.log(active_location_id);
    $('#location-modal').modal('toggle');
  });
});

const initialize_map = () => {
  mapboxgl.accessToken = 'pk.eyJ1IjoicmpheTk4IiwiYSI6ImNqd2FkOWE5NDA4cjEzemtkNGlkNmxqaTUifQ.Zglo0zZl1zOEf0tYynhfzw';
  map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/dark-v9', // stylesheet location
    zoom: 1,
    maxZoom: 13,
    minZoom: 1,
    center: [0,0],
  });
  map.on('load', () => {
    initialize_heatmap();
    initialize_points();
    initialize_locations();
  });
};

var size=120;

var pulsingDot = {
  width: size,
  height: size,
  data: new Uint8Array(size * size * 4),

  onAdd: function () {
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

  const location_points = profile_obj.locations.map( (el, id) => {
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
    $('#location-modal').modal('toggle');
  });
};

const initialize_heatmap = () => {
  const location_param = (loc) => `location:"${loc.name}" OR near:${loc.coordinates[1]},${loc.coordinates[0]},100`;

  const location_query = profile_obj.locations.map((el) => location_param(el)).join(' OR ');

  var params = {
    'query': `( ${location_query} ) tone<-5`,
    'mode': 'pointheatmap',
    'format': 'geoJSON',
    'sortby': 'toneasc',
  };

  var query_url = `${GKG_API_GEO_URL}&${$.param( params )}`;
  $.get({url: query_url}, (resp) => {
    var heatmap_points = resp;
    draw_heatmap(heatmap_points);
  });
};

const draw_heatmap = (data) => {
  map.addSource('articles', {
    'type': 'geojson',
    'data': data,
  });

  map.addLayer({
    'id': 'articles-heat',
    'type': 'heatmap',
    'source': 'articles',
    'maxzoom': 9,
    'paint': {
      // Constant weight
      "heatmap-weight": [
        'interpolate',
        ['linear'],
        ['get', 'count'],
        0, 0,
        6, 1
      ],
      // Color ramp for heatmap.  Domain is 0 (low) to 1 (high).
      // Begin color ramp at 0-stop with a 0-transparancy color
      // to create a blur-like effect.
      "heatmap-color": [
        "interpolate",
        ["linear"],
        ["heatmap-density"],
        0, "rgba(33,102,172,0)",
        0.2, "rgb(103,169,207)",
        0.4, "rgb(209,229,240)",
        0.6, "rgb(253,219,199)",
        0.8, "rgb(239,138,98)",
        1, "rgb(178,24,43)"
      ],
      // Increase the heatmap color weight weight by zoom level
      // heatmap-intensity is a multiplier on top of heatmap-weight
      "heatmap-intensity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        1, 0.2,
        9, 3
        ],
      // Adjust the heatmap radius by zoom level
      "heatmap-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        0, 2,
        9, 20
      ],
      // Transition from heatmap to circle layer by zoom level
      "heatmap-opacity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        1, 0.8,
        9, 0
      ],
    },
  });

}

const initialize_points = () => {
  total_data = profile_obj.locations.map(initialize_loc_points);
};

const initialize_loc_points = (loc, id) => {
  const location_param = `location:"${loc.name}" OR near:${loc.coordinates[1]},${loc.coordinates[0]},100`;

  var params = {
    'query': `( ${location_param} ) tone<-5`,
    'mode': 'pointdata',
    'format': 'geoJSON',
    'sortby': 'toneasc',
  };

  var query_url = `${GKG_API_GEO_URL}&${$.param( params )}`;
  $.get({url: query_url}, (resp) => {
    var article_point_data = resp;
    draw_points(article_point_data, id);
  });
};

const draw_points = (data, id) => {
  map.addSource(`articles-point-data-${id}`, {
    'type': 'geojson',
    'data': data,
  });

  console.log(data);

  map.addLayer({
    "id": `articles-point-${id}`,
    "type": "circle",
    "source": `articles-point-data-${id}`,
    "minzoom": 3,
    "paint": {
      // Size circle radius by earthquake magnitude and zoom level
      "circle-radius": [
        "interpolate",
        ["linear"],
        ["zoom"],
        5, ['/', ['number', ['get', 'count'], 10], 70],
        13, ['/', ['number', ['get', 'count'], 10], 60] 
      ],
      // Color circle by earthquake magnitude
      "circle-color": [
        "interpolate",
        ["linear"],
        ["get", "count"],
        100, "rgba(33,102,172,0)",
        200, "rgb(103,169,207)",
        300, "rgb(209,229,240)",
        400, "rgb(253,219,199)",
        500, "rgb(239,138,98)",
        600, "rgb(178,24,43)"
      ],
      "circle-stroke-color": "rgba(255,255,255,0.4)",
      "circle-stroke-width": 1,
      // Transition from heatmap to circle layer by zoom level
      "circle-opacity": [
        "interpolate",
        ["linear"],
        ["zoom"],
        7, 0,
        8, 1
      ]
    }
  });

  map.on('click', `articles-point-${id}`, (e) => {
    fillin_flashpoint_modal(e);
  });
};

const fillin_flashpoint_modal = (e) => {
  // set modal image
  var img_url = e.features[0].properties.shareimage;
  var img_html = `<img src="${img_url}" class="w-100"></img>`;
  $('#flashpoint-image').html(img_html);

  // set modal information header
  var coordinates = e.features[0].geometry.coordinates.slice();
  coordinates = coordinates.map((s) => s.toFixed(3));
  var article_count = e.features[0].properties.count;
  $('#flashpoint-modal .dashhead-title').text(`${article_count} Articles`);
  $('#flashpoint-modal .dashhead-subtitle').text(`LONG: ${coordinates[0]}, LAT: ${coordinates[1]}`)

  // add articles
  var inner_html = e.features[0].properties.html;
  $('#flashpoint-articles').html(inner_html);

  // show modal
  $('#flashpoint-modal').modal('toggle');
};

const create_theme_statcard = (theme) => {
  return `
    <div class="statcard statcard-danger p-2 m-2" style="width: 150px">
      <h3 class="statcard-number">
        ${theme[1]}
        <small class="delta-indicator delta-positive">6.75%</small>
      </h3>
      <span class="statcard-desc">${theme[0]}</span>
    </div>
  `
};

const create_article_display = (article) => {
  return `
    <li class="list-group-item"><a href="${article.properties.url}">${article.properties.url}</a></li>
  `
};
