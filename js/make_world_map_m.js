max_deaths = 40/25;
function make_world_map_m(features, marker_dict) {
    zoom_level = 4;
    lat_lon = [42.7339, 25.4858]
    var map = L.map('map').setView(lat_lon, zoom_level);

    function make_img_tag(ISO_A3) {
        w = document.getElementById('map').clientWidth/2;
        h = document.getElementById('map').clientHeight/2;
        const src = '"' + ISO_A3 + '.jpg"';
        ws = ' width="' + w +'"';
        wh = ' height="' + h + '"';
        return "<img src=" + src + ws + wh + "></img>";
    }
    // Markers for worst countries in the world
    function populate(marker_dict) {
        for (const ISO_A3 in marker_dict) {
            var marker = L.marker(new L.LatLng(marker_dict[ISO_A3][0], marker_dict[ISO_A3][1]), {}).addTo(map);
            marker.bindPopup(make_img_tag(ISO_A3));
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

    function show_plot_image(e) {
        ISO_A3 = e.target.feature.id.replace("?ISO_A3=","");
        const popup = L.popup().setLatLng(e['latlng']).setContent(make_img_tag(ISO_A3)).openOn(map);
    }
    function onEachFeature(feature, layer) {
        layer.on({
            click: show_plot_image
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

        div.innerHTML = 'Fatalities per 100K<br/>past 7 days<br/>' + labels.join('<br>');
        return div;
    };

    legend.addTo(map);
}
