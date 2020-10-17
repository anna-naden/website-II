function make_world_map(features) {
    const formatter = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })

    // features = features['features']

    zoom_level = 1;
   lat_lon = [54.835365, 0.0]
   var map = L.map('map').setView(lat_lon, zoom_level);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox/light-v9',
        tileSize: 512,
        zoomOffset: -1
    }).addTo(map);


    // control that shows state info on hover
    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };

    info.update = function (props) {
        this._div.innerHTML = '<h3>COVID-19 by County</h3>' + (props ?
            '<b>' + props.name + '</b><br />' + formatter.format(props.density) + ' fatalities per 100,000 people in past 30 days</sup>'
            : 'Mouse over a county to fatalities per capita.<br/>Click to see graph.');
    };

    info.addTo(map);


    // get color depending on population density value
    function getColor(d) {
        return d > 100 ? '#800026' :
                d > 80  ? '#BD0026' :
                d > 20  ? '#E31A1C' :
                d > 10  ? '#FC4E2A' :
                d > 5   ? '#FD8D3C' :
                d > 2   ? '#FEB24C' :
                d > 1   ? '#FED976' :
                            '#FFEDA0';
    }

    function style(feature) {
        return {
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7,
            fillColor: getColor(feature.properties.density)
        };
    }

    function highlightFeature(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 5,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.7
        });

        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            layer.bringToFront();
        }

        info.update(layer.feature.properties);
    }

    var geojson;

    function resetHighlight(e) {
        geojson.resetStyle(e.target);
        info.update();
    }

    function world_time_series(e) {
        ISO_A3 = e.target.feature.id.replace("?ISO_A3=","");
        window.location.href = "ISO-A3-time-series.html?ISO_A3=" + ISO_A3;
    }
    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: world_time_series
        });
    }
    geojson = L.geoJson(features, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend'),
            grades = [0, 1, 2, 5, 10, 20, 80, 100],
            labels = [],
            from, to;

        for (var i = 0; i < grades.length; i++) {
            from = grades[i];
            to = grades[i + 1];

            labels.push(
                '<label style="background-color:' + getColor(from + 1) + '"></i> ' +
                from + (to ? '&ndash;' + to : '+'));
        }

        div.innerHTML = labels.join('<br>');
        return div;
    };

    legend.addTo(map);
}
