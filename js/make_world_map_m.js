max_deaths = 10;
function make_world_map_m(features, marker_dict) {
    zoom_level = 4;
    lat_lon = [42.7339, 25.4858]
    var map = L.map('map').setView(lat_lon, zoom_level);

    // Markers for worst counties in the country
    var MyCusto

    function populate(marker_dict) {
        for (const fips in marker_dict) {
            var marker = L.marker(new L.LatLng(marker_dict[fips][0], marker_dict[fips][1]), {}).addTo(map);
            w = document.getElementById('map').clientWidth/2;
            h = document.getElementById('map').clientHeight/2;
            const src = '"' + fips + '.jpg"';
            ws = ' width="' + w +'"';
            wh = ' height="' + h + '"';
            const img_tag = "<img src=" + src + ws + wh + "></img>";
            marker.bindPopup(img_tag);
        }
        return false;
    }

    populate(marker_dict);


    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        maxZoom: 18,
        // attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        //     '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        //     'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        attribution: 'Data downloaded nightly from Johns Hoplins University',
        id: 'mapbox/light-v9',
        tileSize: 512,
        zoomOffset: -1,
        noWrap: false
    }).addTo(map);

    function style(feature) {
        return {
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7,
            fillColor: getColor(feature.properties.density, max_deaths)
        };
    }

    var geojson;

    function world_time_series(e) {
        ISO_A3 = e.target.feature.id.replace("?ISO_A3=","");
        if (ISO_A3 == 'USA') {
            window.location.href = 'us-hot2.html';
        }
    }
    function onEachFeature(feature, layer) {
        layer.on({
            click: world_time_series
        });
    }
    geojson = L.geoJson(features, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'legend'),
            grades = map_grades(max_deaths),
            labels = [],
            from, to;

        for (var i = 0; i < grades.length; i++) {
            from = grades[i];
            to = grades[i + 1];

            labels.push(
                '<label style="background-color:' + getColor(from*1.01, max_deaths) + '"></i> ' +
                from + (to ? '&ndash;' + to : '+'));
        }

        div.innerHTML = 'Fatalities per 100,000 in past 7 days' + '<br/>' + labels.join('<br>');
        return div;
    };

    legend.addTo(map);
}
