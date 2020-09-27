// https://observablehq.com/@d3/horizontal-bar-chart@247
export default function define(runtime, observer) {
  const main = runtime.module();
  const fileAttachments = new Map([["alphabet.csv",new URL("./files/09f63bb9ff086fef80717e2ea8c974f918a996d2bfa3d8773d3ae12753942c002d0dfab833d7bee1e0c9cd358cd3578c1cd0f9435595e76901508adc3964bbdc",import.meta.url)]]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], function(md){return(
md`# Horizontal Bar Chart

This chart shows the relative frequency of letters in the English language.`
)});
  main.variable(observer("chart")).define("chart", ["d3","width","height","data","x","y","format","xAxis","yAxis"], function(d3,width,height,data,x,y,format,xAxis,yAxis)
{
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, width, height]);
  
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
);
  main.variable(observer("data")).define("data", ["d3","FileAttachment"], async function(d3,FileAttachment){return(
Object.assign(d3.csvParse(await FileAttachment("alphabet.csv").text(), ({letter, frequency}) => ({name: letter, value: +frequency})).sort((a, b) => d3.descending(a.value, b.value)), {format: "%"})
)});
  main.variable(observer("format")).define("format", ["x","data"], function(x,data){return(
x.tickFormat(20, data.format)
)});
  main.variable(observer("x")).define("x", ["d3","data","margin","width"], function(d3,data,margin,width){return(
d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)])
    .range([margin.left, width - margin.right])
)});
  main.variable(observer("y")).define("y", ["d3","data","margin","height"], function(d3,data,margin,height){return(
d3.scaleBand()
    .domain(d3.range(data.length))
    .rangeRound([margin.top, height - margin.bottom])
    .padding(0.1)
)});
  main.variable(observer("xAxis")).define("xAxis", ["margin","d3","x","width","data"], function(margin,d3,x,width,data){return(
g => g
    .attr("transform", `translate(0,${margin.top})`)
    .call(d3.axisTop(x).ticks(width / 80, data.format))
    .call(g => g.select(".domain").remove())
)});
  main.variable(observer("yAxis")).define("yAxis", ["margin","d3","y","data"], function(margin,d3,y,data){return(
g => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickFormat(i => data[i].name).tickSizeOuter(0))
)});
  main.variable(observer("barHeight")).define("barHeight", function(){return(
25
)});
  main.variable(observer("height")).define("height", ["data","barHeight","margin"], function(data,barHeight,margin){return(
Math.ceil((data.length + 0.1) * barHeight) + margin.top + margin.bottom
)});
  main.variable(observer("margin")).define("margin", function(){return(
{top: 30, right: 0, bottom: 10, left: 30}
)});
  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@6")
)});
  return main;
}
