max_deaths = 40/25;
function make_world_map(features, marker_dict, mobile) {
    zoom_level = 1;
    lat_lon = [54.835365, 0.0]
   var map = L.map('map').setView(lat_lon, zoom_level);

   // Markers for worst counties in the country
   var MyCustomMarker = L.Marker.extend({
        bindPopup: function(htmlContent, fips, options) {
                  
        if (options && options.showOnMouseOver) {
            
            // call the super method
            L.Marker.prototype.bindPopup.apply(this, [htmlContent, options]);
            
            // unbind the click event
            // this.off("click", this.openPopup, this);
            
            // bind the click event
            this.on("click", function(e) {
                if (mobile) {
                    var src = '"' + fips + '.jpg"';
                    const h = '"250"';
                    const w = '"300"';
                    const style = '" style="float: left"'
                    // const img_tag = "<img src=" + src + " width=" + w + " height=" + h + style + "></img>";
                    const img_tag = "<img src=" + src + style + "></img>";
                    src = '"covid-formula2.png"'
                    const img_tag2 = "<img src=" + src + style + "></img>";
                    document.getElementById('map').innerHTML = img_tag + "<br/>"+img_tag2;
                }
                else {
                    map.zoomIn(2);
                }
            });
            
            // bind to mouse over
            this.on("mouseover", function(e) {
                
                // get the element that the mouse hovered onto
                var target = e.originalEvent.fromElement || e.originalEvent.relatedTarget;
                var parent = this._getParent(target, "leaflet-popup");
 
                // check to see if the element is a popup, and if it is this marker's popup
                if (parent == this._popup._container)
                    return true;
                
                // show the popup
                if (!mobile) {
                    this.openPopup();
                }
            }, this);
            
            // and mouse out
            this.on("mouseout", function(e) {
                
                // get the element that the mouse hovered onto
                var target = e.originalEvent.toElement || e.originalEvent.relatedTarget;
                
                // check to see if the element is a popup
                if (this._getParent(target, "leaflet-popup")) {
 
                    L.DomEvent.on(this._popup._container, "mouseout", this._popupMouseOut, this);
                    return true;
 
                }
                
                // hide the popup
                this.closePopup();
                
            }, this);
            
        }
        
    },
 
    _popupMouseOut: function(e) {
        
        // detach the event
        L.DomEvent.off(this._popup, "mouseout", this._popupMouseOut, this);
 
        // get the element that the mouse hovered onto
        var target = e.toElement || e.relatedTarget;
        
        // check to see if the element is a popup
        if (this._getParent(target, "leaflet-popup"))
            return true;
        
        // check to see if the marker was hovered back onto
        if (target == this._icon)
            return true;
        
        // hide the popup
        this.closePopup();
        
    },
    
    _getParent: function(element, className) {
        
        var parent = element.parentNode;
        
        while (parent != null) {
            
            if (parent.className && L.DomUtil.hasClass(parent, className))
                return parent;
            
            parent = parent.parentNode;
            
        }
        
        return false;
        
    },
    fips:this.fips,
    mobile: this.mobile
    });

    var markers = new L.FeatureGroup();

    function populate(marker_dict) {
        for (const fips in marker_dict) {
            var marker = new MyCustomMarker(new L.LatLng(marker_dict[fips][0], marker_dict[fips][1]), mobile);
            const src = '"' + fips + '.jpg"';
            const img_tag = "<img src=" + src + style + "></img>";
            marker.bindPopup(img_tag, fips, {
                showOnMouseOver: true
            });
            markers.addLayer(marker);
        }
        return false;
    }

    map.addLayer(markers);

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


    // control that shows state info on hover
    var info = L.control({options: {position: 'topleft'}});

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };

    info.update = function (props) {
        this._div.innerHTML = '';
        if (props && !mobile) {
            ISO_A3 = props.adm0_a3;
            var src = '"' + ISO_A3 + '.jpg"';
            const h = '"250"';
            const w = '"300"';
            const style = '" style="float: left"'
            // const img_tag = "<img src=" + src + " width=" + w + " height=" + h + style + "></img>";
            const img_tag = "<img src=" + src + style + "></img>";
            src = '"covid-formula2.png"'
            const img_tag2 = "<img src=" + src + style + "></img>";
            this._div.innerHTML = img_tag + "<br/>"+img_tag2;

        }
        // this._div.innerHTML = '<h3>COVID-19 by County</h3>' + (props ?
            // '<b>' + props.name + '</b><br />' + formatter.format(props.density) + ' fatalities per 100,000 people in past 30 days</sup>'
            // : 'Mouse over a county to fatalities per capita.<br/>Click to see graph.');
    };

    info.addTo(map);

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
        // window.location.href = "ISO-A3-time-series2.html?ISO_A3=" + ISO_A3;
        if (ISO_A3 == 'USA') {
            window.location.href = 'us-hot2.html';
        }
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
