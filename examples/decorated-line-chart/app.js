var data=[
    {date: 2000, number: 23},
    {date: 2001, number: 24},
    {date: 2002, number: -25},
    {date: 2003, number: 68},
    {date: 2004, number:75}
    ]

// Date Formats
var time_parse = d3.timeParse('%Y');
var time_format = d3.timeFormat('%Y');

var barchart_width = 800;
var barchart_height=600;
var padding=40;

data.forEach(function(e,i) {
    data[i].date = time_parse(e.date);
});

//Create scales
var x_scale = d3.scaleTime()
    .domain([d3.min(data, function(d) {
        return d.date;
    }), d3.max(data, function(d) {
        return d.date;
    })])
    .range([padding, barchart_width-padding]);

var y_scale = d3.scaleLinear()
    .domain([0, d3.max(data, function(d) {
        return d.number;
    })])
    .range([barchart_height-padding,padding]);

// Create axes
var x_axis = d3.axisBottom(x_scale)
    .ticks(12)
    .tickFormat(time_format);

var y_axis = d3.axisLeft(y_scale)
    .ticks(3)

//Create elements
var svg = d3.select('#barchart')
    .append('svg')
    .attr('height', barchart_height)
    .attr('width', barchart_width);

//Draw and position the axes

svg.append('g')
    .attr('transform', 'translate(0, '+(barchart_height-padding) +')')
    .call(x_axis);

svg.append('g')
    .attr('class', 'y-axis')
    .attr('transform', 'translate(' + padding + ',0)')
    .call(y_axis);

//Create the line
var line = d3.line()
    .defined(function(d) {
        return d.number>=0 && d.number <=50;
    })
    .x(function(d) {
        return x_scale(d.date);
    })
    .y(function(d) {
        return y_scale(d.number);
    });

var important_line = d3.line()
    .defined(function(d) {
        return d.number>=50;
    })
    .x(function(d) {
        return x_scale(d.date);
    })
    .y(function(d) {
        return y_scale(d.number);
    });

var area = d3.area()
    .defined(function(d) {
        return d.number >=0;
    })
    .x(function(d) {
        return x_scale(d.date);
    })
    .y0(function(d) {
        return y_scale.range()[0];
    })
    .y1(function(d) {
        return y_scale(d.number)
    });

svg.append('path')
    .datum(data)
    .attr('d', line)
    .attr('fill','grey')
    .attr('d', area);

svg.append('path')
    .datum(data)
    .attr('d', line)
    .attr('fill','none')
    .attr('stroke', 'red')
    .attr('stroke-width', 5)
    .attr('d', important_line);