var map;
var active_location_id;
const GKG_API_GEO_URL = 'https://api.gdeltproject.org/api/v2/geo/geo?';
const GKG_API_DOC_URL = 'https://api.gdeltproject.org/api/v2/doc/doc?';

const GKG_GEOJSON_URL='https://api.gdeltproject.org/api/v1/gkg_geojson';

$(() => {
  data = pull_data(display_article_data);
});

const display_article_data = (html) => {
  console.log(html);
  var article_html = $(html).filter('#maincontent').html();
  $('#articles').html(article_html);
};

const pull_data = (callback, themes=null, locations=null, num_results=10, format='html', mode='artlist') => {
  // // Gets the relevant data for a specified themes and locations query
  // const location_param = (loc) => `location:"${loc.name}" OR near:${loc.coordinates[1]},${loc.coordinates[0]},100`;

  // // default to all specified locations
  // var query_locs = locations ? locations : profile_obj.locations;

  // // default to all specified themes
  // var rb_themes = themes ? themes : profile_obj.relevant_themes;
  // // convert to gkg themes
  // var query_themes = theme_convert(rb_themes);

  // const location_query = query_locs.map((el) => location_param(el)).join(' OR ');
  // const theme_query = query_themes.map((t) => `theme:${t}`).join(' OR ');

  var params = {
    // 'query': `( ${location_query} ) ( ${theme_query} ) tone<-3`,
    'mode': mode,
    'format': format,
    'sortby': 'toneasc',
    'maxrecords': num_results,
    'trans': 'googtrans'
  };

  serialized_params = `${$.param(params)}&query=\"${profile_obj.company_name}\"`

  var query_url = `${GKG_API_DOC_URL}${ serialized_params }`;

  $.get({url: query_url}, (resp) => {
    callback(resp);
  });
};

const theme_convert = (rb_themes) => {
  converted = rb_themes.reduce((final_list, theme) => final_list.concat(theme_dict[theme]), initialValue=[]);
  return converted;
};

$('.location-select').on('click', (e) => {
  active_location_id = $(e.currentTarget).attr('id');
  $('#location-modal').modal('toggle');
});

//triggered when modal is about to be shown
$('#location-modal').on('show.bs.modal', function(e) {
  // populate the textbox
  $('#location-modal .dashhead-title').text(profile_obj.locations[active_location_id].name);
  $('.location-themes').html(
    // query_result[active_location_id].themes.map(create_theme_statcard).join('')
  );
  $('.location-articles').html(
    // article_data[active_location_id].articles.features.map(create_article_display).join('')
  );
});