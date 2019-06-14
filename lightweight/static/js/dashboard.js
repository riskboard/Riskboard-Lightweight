var map;
var active_location_id;
var TIMEFRAME;

const GKG_API_GEO_URL = 'https://api.gdeltproject.org/api/v2/geo/geo?';
const GKG_API_DOC_URL = 'https://api.gdeltproject.org/api/v2/doc/doc?';

const GKG_GEOJSON_URL='https://api.gdeltproject.org/api/v1/gkg_geojson';

$(() => {
  initialize_timeframe();
  load_keyword_articles();
});

const initialize_timeframe = () => {
  get_timeframe();
  $('.timeframe-button').on('click', (e) => {
    // clear all actives from menu
    $('.timeframe-button.active').toggleClass('active');
    $(e.currentTarget).toggleClass('active');
    TIMEFRAME = $(e.currentTarget).attr('value');
    refresh_keyword_articles();
  });
};

const get_timeframe = () => {
  TIMEFRAME = $('.active.timeframe-button').attr('value');
};

const refresh_keyword_articles = () => {
  $('#articles').empty();
  load_keyword_articles();
}

const load_keyword_articles = () => {
  const article_list_html = (kwd, inner_content) => {
    return `
    <div class="article-list">
      <h5>${kwd}</h5>
      ${inner_content}
    </div>
    `
  };

  const display_article_data = (kwd, html) => {
    var gkg_html = $(html).filter('#maincontent').html();
    var to_append = article_list_html(kwd, gkg_html);
    $('#articles').append(to_append);
  };

  // shallow copy keyword array
  query_keywords = [...profile_obj.keywords];
  // append company name
  query_keywords.push(profile_obj.company_name);

  query_keywords.forEach((kwd) => {
    var callback = (html) => display_article_data(kwd, html);
    pull_data(callback, keyword=kwd, timeframe=TIMEFRAME);
  });
};

const pull_data = (callback, keyword=null, themes=null, locations=null, num_results=5, timespan=TIMEFRAME, format='html', mode='artlist', sortby='toneasc') => {
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
    'sortby': sortby,
    'timespan': timespan,
    'maxrecords': num_results,
  };

  var query_string = `query=\"${keyword}\"`;
  var query_url = `${GKG_API_DOC_URL}${$.param(params)}&${query_string}`;
  console.log(query_url);

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