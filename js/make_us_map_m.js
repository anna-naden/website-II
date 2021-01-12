const max_deaths = 40/25;

function make_us_map_m(statesData, marker_dict) {
    var map = L.map('map').setView([43.194, -99.1888], 5);

    function make_img_tag(fips) {
        const src = '"' + fips + '.jpg"';
        w = document.getElementById('map').clientWidth/1.5;
        h = document.getElementById('map').clientHeight/1.9;
        ws = ' width="' + w +'"';
        wh = ' height="' + h + '"';
        return "<img src=" + src + ws + wh + "></img>";
    }
    function populate(marker_dict) {
        for (const fips in marker_dict) {
            var marker = L.marker(new L.LatLng(marker_dict[fips][0], marker_dict[fips][1])).addTo(map);
            const src = '"' + fips + '.jpg"';
            const img_tag = "<img src=" + src + style + "></img>";
            marker.bindPopup(make_img_tag(fips));
        }
    }
    
    populate(marker_dict);

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
        fips = e.target.feature.id;
        if (fips.substring(0,3) == 'USA' ) {
            fips = fips.substring(3,5);
        }
        const popup = L.popup().setLatLng(e['latlng']).setContent(make_img_tag(fips)).openOn(map);
    }

    function onEachFeature(feature, layer) {
        layer.on({
            click: show_plot_image
        });
    }
    geojson = L.geoJson(statesData, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);
    map.attributionControl.addAttribution('Data from Johns Hoplins University');

    var legend = L.control({ position: 'bottomright' });

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

        div.innerHTML = 'Fatalities per 100K<br/>per day<br/>' + labels.join('<br>');
        return div;
    };

    legend.addTo(map);
}
