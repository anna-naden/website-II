function make_us_map(statesData) {
    const formatter = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
    var map = L.map('map').setView([37.8, -96], 4);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox/light-v9',
        tileSize: 512,
        zoomOffset: -1,
        noWrap: true
    }).addTo(map);


    // control that shows state info on hover
    var info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };

    info.update = function (props) {
        if (props) {
        // this._div.innerHTML = '<h3>COVID-19 by State</h3>' + (props ?
        //     '<b>' + props.name + '</b><br />' + formatter.format(props.density) + ' fatalities per 100,000 people in past 30 days</sup>'
        //     : 'Mouse over a state or province to fatalities per capita.<br/>Click to see state detail map.');
        var ISO_A3 = props['fips'].substr(0,3)
        if (ISO_A3 == 'USA') {
            const src = '"' + props['fips'].substr(3,5) + '.jpg"';
            const h = '"300"';
            const w = '"300"';
            const style = '" style="float: left"'
            // const img_tag = "<img src=" + src + " width=" + w + " height=" + h + style + "></img>";
            const img_tag = "<img src=" + src + style + "></img>";
            this._div.innerHTML = img_tag;
        }
        if (ISO_A3.substr(0,3) == 'CAN') {
            const src = '"CAN' + props['fips'].substr(3,5) + '.jpg"';
            const h = '"300"';
            const w = '"300"';
            const style = '" style="float: left"'
            // const img_tag = "<img src=" + src + " width=" + w + " height=" + h + style + "></img>";
            const img_tag = "<img src=" + src + style + "></img>";
            this._div.innerHTML = img_tag;

        }
    }
    };

    info.addTo(map);


    // get color depending on population density value
    function getColor(d) {
        return d > 100 ? '#800026' :
            d > 80 ? '#BD0026' :
                d > 20 ? '#E31A1C' :
                    d > 10 ? '#FC4E2A' :
                        d > 5 ? '#FD8D3C' :
                            d > 2 ? '#FEB24C' :
                                d > 1 ? '#FED976' :
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
        // layer.openPopup();
    }

    var geojson;

    function resetHighlight(e) {
        var layer = e.target;
        geojson.resetStyle(e.target);
        info.update();
        layer.closePopup()
    }

    function state_hot(e) {
        fips = e.target.feature.id.substring(3, 5);
        ISO_A3 = e.target.feature.id.substring(0,3);
        if (ISO_A3 == 'USA') {
            window.location.href = "state-hot.html?fips=" + fips;
        }
    }

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: state_hot
        });
        // var ISO_A3 = feature['id'].substr(0,3)
        // if (ISO_A3 == 'USA') {
        //     const src = '"' + feature['id'].substr(3,5) + '.jpg"';
        //     const h = '"300"';
        //     const w = '"300"';
        //     const style = '" style="float: left"'
        //     const img_tag = "<img src=" + src + " width=" + w + " height=" + h + style + "></img>";
        //     layer.bindPopup(img_tag, {autoPan: true});
        // }
    }
    geojson = L.geoJson(statesData, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

    map.attributionControl.addAttribution('Population data &copy; <a href="http://census.gov/">US Census Bureau</a>');


    var legend = L.control({ position: 'bottomright' });

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
