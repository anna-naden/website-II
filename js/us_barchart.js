function us_barchart() {
    const width=100;
    const height=100;
    const svg = d3.select("svg")
        .attr("viewBox", [0, 0, width, height]);
        // var data = Object.assign(d3.csvParse(await FileAttachment("alphabet.csv").text(), ({letter, frequency}) => ({name: letter, value: +frequency})).sort((a, b) => d3.descending(a.value, b.value)), {format: "%"})
        var d1={name: "E", value: 1};
        var d2={name: "T", value: 0.5};
        var c={columns: Array(2) ["letter","frequency"]};
        var f={format: "%"};
        var data = [d1,d2,c,f ];

        var format = ƒ(t);
        x = ƒ(n);
        y = ƒ(i);
        xAxis = ƒ(g);
        yAxis = ƒ(g);
        barHeight = 25;
        height = 693;
        margin ={top: 30, right: 0, bottom: 10, left: 30};
        
        

        svg.append("g")
        .attr("fill", "steelblue")
      .selectAll("rect")
      .data(data)
      .join("rect")
        .attr("x", x(0))
        .attr("y", (d, i) => y(i))
        .attr("width", d => x(d.value) - x(0))
        .attr("height", y.bandwidth());
    
    svg.append("g")
        .attr("fill", "white")
        .attr("text-anchor", "end")
        .attr("font-family", "sans-serif")
        .attr("font-size", 12)
      .selectAll("text")
      .data(data)
      .join("text")
        .attr("x", d => x(d.value))
        .attr("y", (d, i) => y(i) + y.bandwidth() / 2)
        .attr("dy", "0.35em")
        .attr("dx", -4)
        .text(d => format(d.value))
      .call(text => text.filter(d => x(d.value) - x(0) < 20) // short bars
        .attr("dx", +4)
        .attr("fill", "black")
        .attr("text-anchor", "start"));
  
    svg.append("g")
        .call(xAxis);
  
    svg.append("g")
        .call(yAxis);
  
    return svg.node();
  }
