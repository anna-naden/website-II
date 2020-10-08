var data=[
    [300,150],
    [270,125],
    [150,375],
    [200,200]
    ]

var barchart_width = 800;
var barchart_height=400;
var bar_padding=5;

var svg = d3.select("#barchart")
    .append("svg")
    .attr("width", barchart_width)
    .attr("height", barchart_height);

//Create scales
var x_scale = d3.scaleLinear()
    .domain([0, d3.max(data, function(d) {
        return d[0];
    })])
    .range([0,barchart_width]);

var y_scale = d3.scaleLinear()
    .domain([0, d3.max(data, function(d) {
        return d[1];
    })])
    .range([0,barchart_height]);

// Create axes
var x_axis = d3.axisBottom(x_scale)
    .ticks(12);

var y_axis = d3.axisLeft(y_scale)
    .tickFormat(function( d) {
        return d + '%';
    });
    

svg.append('g')
    .attr('class', 'x-axis')
    .attr('transform', 'translate(0, '+(barchart_height-20) +')')
    .call(x_axis);

svg.append('g')
    .attr('class', 'y-axis')
    .attr('transform', 'translate(' + 60 +',0)')
    .call(y_axis);

svg.selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
    .attr("cx", function(d) {
        return x_scale(d[0]);
    })
    .attr("cy",function(d) {
        return y_scale(d[1]);
        })
     .attr("r", function(d) {
         return d[0]/10;
     })
     .attr("fill","grey");

// Create labels
     svg.append('g').selectAll('text')
        .data(data)
        .enter()
        .append('text')
        .text(function(d) {
            return d.join(',');
        })
        .attr('x' ,function(d) {
            return x_scale(d[0]);
        })
        .attr('y', function(d) {
            return y_scale(d[1]);
        })
        .attr('font-size', 16)
        .attr('fill', 'white')
        .attr('text-anchor', 'middle')
        
