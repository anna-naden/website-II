function get_state_features(fips)
{
  refresh_map_div();
  var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        var state_features = JSON.parse(this.responseText);
        make_state_map(fips,state_features);
      };
    };
    xhttp.open("GET", "https://qwwj8ox9l9.execute-api.us-east-1.amazonaws.com/stage/fips?fips="+fips, true);
    xhttp.send();
}
