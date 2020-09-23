function get_data(e)
{
    url = 'http://localhost:3000/us-rest/' + e.sourceTarget.feature['FIPS-code']
    console.log(url)
    fetch(url)
    .then(response => response.json())
    .then(data => draw_driver(JSON.parse(data)));
}
function draw_driver(json_data)
  {
    // alert(xinspect(json_data))
    // set the dimensions and margins of the graph
    var margin = { top: 20, right: 20, bottom: 30, left: 50 },
      width = 960 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom;

    // parse the date / time
    var parseTime = d3.timeParse("%Y");

    // set the ranges
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // define the line
    var valueline = d3
      .line()
      .x(function (d) {
        return x(d.Date);
      })
      .y(function (d) {
        return y(d.Imports);
      });
    // define the line

    var valueline2 = d3
      .line()
      .x(function (d) {
        return x(d.Date);
      })
      .y(function (d) {
        return y(d.Exports);
      });

    // append the svg obgect to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    d3.select(".anna-svg")
      .remove();
    d3.select("body")
      .append("anna-svg")
      .classed("anna-svg", true)
    var svg = d3
      .select(".anna-svg")
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    function draw(data, country) {
      var data = data[country];

      // format the data
      data.forEach(function (d) {
        var date = new Date(d.date);
        d.Date = date;
        d.Imports = +d.deaths_per;
        d.Exports = +d.deaths_per;
      });

      // sort years ascending
      data.sort(function (a, b) {
        return a["Date"] - b["Date"];
      });

      // Scale the range of the data
      x.domain(
        d3.extent(data, function (d) {
          return d.Date;
        })
      );
      y.domain([
        0,
        d3.max(data, function (d) {
          return Math.max(d.Imports, d.Exports);
        }),
      ]);

      // Add the valueline path.
      svg
        .append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline);
      // Add the valueline path.
      svg
        .append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", valueline2);
      // Add the X Axis
      svg
        .append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

      // Add the Y Axis
      svg.append("g").call(d3.axisLeft(y));
    }

    // Draw the graph
    draw(json_data, "county");
  }
  function get_county_covid()
  {
    url = "https://vpw7dxy2uf.execute-api.us-east-1.amazonaws.com/stage/us_hot";
    var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        console.log('readyState' + this.readyState);
        console.log(this.status)
        if (this.readyState == 4 && this.status == 200) {
          // document.getElementById("my-demo").innerHTML = JSON.stringify(this.responseText);
          var county_covid =JSON.parse(this.responseText);
          console.log('response: ' + county_covid['features']);
          make_map(county_covid);
        }
      };
      xhttp.open("GET", url, true);
      xhttp.send();
  }
