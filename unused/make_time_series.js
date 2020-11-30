function make_time_series(us_data, region_data, title) {
    
    // var data = features.county;
    // var us_data = features.us;
    //  title = "US and " + data.county + '\n Total fatalities to date per 100,000 persons:\n' +
    //     data.start_date + ' - ' + data.end_date;
    data = region_data.stats;
    us_data = us_data.stats;

    var barchart_width  = 800;
    var barchart_height = 600;
    var padding         = 40;

    // The date format
    data.forEach(function(e,i) {
        // data[i].date = time_parse(e.date);
        data[i].date = new Date(e.date);
    });

    us_data.forEach(function(e,i) {
        // data[i].date = time_parse(e.date);
        us_data[i].date = new Date(e.date);
    });


    // Creating scales
    var data_min_x=d3.min(data, function(d) {return d.date;});
    var us_data_min_x=d3.min(us_data, function(d) {return d.date;});
    var data_max_x = d3.max(data, function(d) { return d.date; });
    var us_data_max_x = d3.max(us_data, function(d) { return d.date; });
    var data_max_y=d3.max(data, function(d) {
        return d.deaths;
    });
    var us_data_max_y=d3.max(us_data, function(d) {
        return d.deaths;
    });
    var x_scale = d3.scaleTime()
                    .domain([
                        Math.min(data_min_x, us_data_min_x),
                        Math.max(data_max_x, us_data_max_x)
                        ])
                    .range([padding, barchart_width - padding]);

    var y_scale = d3.scaleLinear()
                    .domain([
                        0, 
                        Math.max(data_max_y, us_data_max_y)
                    ])
                    .range([barchart_height - padding, padding]);


    // Creating elements
    var svg =  d3.select('#county-time-series')
                .append('svg')  
                .attr('height', barchart_height)
                .attr('width', barchart_width);

    // Creating axis
    // The x-axis
    var x_axis = d3.axisBottom(x_scale)
                .ticks(5);
                // .tickFormat(time_format);

    // The y-axis
    var y_axis = d3.axisLeft(y_scale)
                .ticks(8);

    // Draw and position the axis
    svg.append('g')
    .attr('transform', 'translate(0,'+ (barchart_height-padding) +')')
    .call(x_axis);

    svg.append('g')
    .attr('class', 'y-axis')
    .attr('transform', 'translate(' + padding +',0)')
    .call(y_axis);

    svg.append("text")
    .attr("x", (barchart_width / 2))             
    .attr("y", padding / 2)
    .attr("text-anchor", "middle")  
    .style("font-size", "16px") 
    .style("text-decoration", "underline")  
    .text(title);

    // Creating the line
    var line1 = d3.line()
            .defined(function(d){
                return d.deaths >= 0;
            })
            .x(function(d){
                return x_scale(d.date);
            })
            .y(function(d){
                return y_scale(d.deaths);
            });

    // Creating the line
    var line2 = d3.line()
            .defined(function(d){
                return d.deaths >= 0;
            })
            .x(function(d){
                return x_scale(d.date);
            })
            .y(function(d){
                return y_scale(d.deaths);
            });

    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', 'grey')
        .attr('stroke-width', 5)
        .attr('d', line1);
    svg.append('path')
        .datum(us_data)
        .attr('fill', 'none')
        .attr('stroke', 'red')
        .attr('stroke-width', 5)
        .attr('d', line2);

    // Legend
    var legend = svg.append("g")
    .attr("class", "legend")
    .attr("x", barchart_width - 65)
    .attr("y", 25)
    .attr("height", 100)
    .attr("width", 100);

    legend.selectAll('rect')
            .data(data)
            .enter();

    legend.append("rect")
    .attr("x", barchart_width - 65)
    .attr("y", 25)
    .attr("width", 10)
    .attr("height", 10)
    .style("fill", function(d) { return "red" });

    legend.append("text")
    .attr("x", barchart_width - 40)
    .attr("y", 35)
    .text(function(d) { return "US" });
        }