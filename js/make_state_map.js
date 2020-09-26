function make_state_map(fips,state_features) {
    const formatter = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })
    const state_lat_long = {
        '01':[32.806671,-86.791130],
        '02':[61.370716,-152.404419],
        '04':[33.729759,-111.431221],
        '05':[34.969704,-92.373123],
        '06':[36.116203,-119.681564],
        '08':[39.059811,-105.311104],
        '09':[41.597782,-72.755371],
        '10':[39.318523,-75.507141],
        '11':[38.897438,-77.026817],
        '12':[27.766279,-81.686783],
        '13':[33.040619,-83.643074],
        '15':[21.094318,-157.498337],
        '16':[44.240459,-114.478828],
        '17':[	40.349457	,-88.986137],
        '18':[39.849426	,-86.258278],
        '19':[42.011539	,-93.210526],
        '20':[38.526600	,-96.726486],
        '21':[37.668140	,-84.670067],
        '22':[31.169546	,-91.867805],
        '23':[44.693947	,-69.381927],
        '24':[	39.063946	,-76.802101],
        '25':[	42.230171	,-71.530106],
        '26':[	43.326618	,-84.536095],
        '27':[	45.694454	,-93.900192],
        '28':[	32.741646	,-89.678696],
        '29':[38.456085	,-92.288368],
        '30':[	46.921925	,-110.454353],
        '31':[	41.125370	,-98.268082],
        '32':[38.313515	,-117.055374],
        '33':[	43.452492	,-71.563896],
        '34':[	40.298904	,-74.521011],
        '35':[	34.840515	,-106.248482],
        '36':[	42.165726	,-74.948051],
        '37':[	35.630066	,-79.806419],
        '38':[	47.528912	,-99.784012],
        '39':[	40.388783	,-82.764915],
        '40':[	35.565342	,-96.928917],
        '41':[	44.572021	,-122.070938],
        '42':[	40.590752	,-77.209755],
        '44':[41.680893	,-71.511780],
        '45':[	33.856892	,-80.945007],
        '46':[	44.299782	,-99.438828],
        '47':[	35.747845	,-86.692345],
        '48':[	31.054487	,-97.563461],
        '49':[	40.150032	,-111.862434],
        '50':[	44.045876	,-72.710686],
        '51':[	37.769337	,-78.169968],
        '53':[	47.400902	,-121.490494],
        '54':[	38.491226	,-80.954453],
        '55':[	44.268543	,-89.616508],
        '56':[	42.755966	,-107.302490]
    };

    // fips codes
    alaska = '02';
    texas = '48';
    lat_lon = state_lat_long[fips];
    zoom_level = 6;
    if (fips==alaska) {
      lat_lon = [64.835365, -147.776749]
      zoom_level = 4;
    };
    if (fips == texas) {
      zoom_level = 5;
    }
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

    function onEachFeature(feature, layer) {
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
        });
    }
    geojson = L.geoJson(state_features, {
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
