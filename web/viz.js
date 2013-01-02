
var margin = 
  { top: 20, right: 20, bottom: 30, left: 40},
  width = 960 - margin.left - margin.right,
  height = 500 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
  .range([height, 0]);

var xAxis = d3.svg.axis()
  .scale(x)
  .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

function formatTime(ts) {
  var dd = new Date();
  dd.setTime(1000.0*ts);
  return dd.toLocaleString().substr(19,5);
}

var svg = d3.select("body")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
  ;

d3.json("/?q=%23ratp&l=20", function(error, jsondata) {

  var ts_data = jsondata['ts'];

  x.domain(ts_data.map(function(d) { return formatTime(d.timestamp); }));
  y.domain([0, d3.max(ts_data, function(d) { return d.tweets.length; })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Tweet Count");

  svg.selectAll(".bar")
      .data(ts_data)
     .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(formatTime(d.timestamp)); })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.tweets.length); })
      .attr("height", function(d) { return height - y(d.tweets.length); })
      .append("svg:title")
      .text(function(d) { 
        var l = d.tweets.length;
        var r = "";
        for (var i = 0; i < l; i++) {
          r += "[@"+d.tweets[i].user_id+"] "+d.tweets[i].text+"\n\n";
        }
        return r;
       })
  ;

    var fill = d3.scale.category20();

    var tags = new Array();
    var tags_count = {};
    var w = 0;
    for(var i = 0; i < ts_data.length; i++){
      var tweets = ts_data[i].tweets;
      for(var t = 0; t < tweets.length; t++) {
        var hashtags = tweets[t].hashtags;
        for(var h = 0; h < hashtags.length; h++) {
          ht = "#"+hashtags[h].toLowerCase();
          if(tags_count.hasOwnProperty()){
            tags_count[ht] += 1;
            continue;
          }
          tags[w] = ht;
          tags_count[ht] = 1;
          w += 1;
        }
      }
    }

    d3.layout.cloud().size([300, 300])
        .words(tags.map(function(d) {
          return {text: d, size: 10 + tags_count[d] * 90};
        }))
        .rotate(function() { return ~~(Math.random() * 2) * 90; })
        .font("Impact")
        .fontSize(function(d) { return d.size; })
        .on("end", draw)
        .start();

    function draw(words) {
      d3.select("body").append("svg")
          .attr("width", 300)
          .attr("height", 300)
        .append("g")
          .attr("transform", "translate(150,150)")
        .selectAll("text")
          .data(words)
        .enter().append("text")
          .style("font-size", function(d) { return d.size + "px"; })
          .style("font-family", "Impact")
          .style("fill", function(d, i) { return fill(i); })
          .attr("text-anchor", "middle")
          .attr("transform", function(d) {
            return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
          })
          .text(function(d) { return d.text; });
    }

});

