    // Try to label the counties
    L.LabelOverlay = L.Layer.extend({
        initialize: function(/*LatLng*/ latLng, /*String*/ label, options) {
            this._latlng = latLng;
            this._label = label;
            L.Util.setOptions(this, options);
        },
        options: {
            offset: new L.Point(0, 2)
        },
        onAdd: function(map) {
            this._map = map;
            if (!this._container) {
                this._initLayout();
            }
            map.getPanes().popupPane.appendChild(this._container);
            this._container.innerHTML = this._label;
            map.on('movestart', this._update_start, this);
            map.on('moveend', this._update_end, this);
            this._update_end();
        },
        onRemove: function(map) {
            map.getPanes().popupPane.removeChild(this._container);
            map.off('movestart', this._update_start, this);
            map.off('moveend', this._update_end, this);
        },
        _update_start: function(){
            L.DomUtil.setPosition(this._container, 0);
        },
        _update_end: function() {
            var pos = this._map.latLngToLayerPoint(this._latlng);
            var op = new L.Point(pos.x + this.options.offset.x, pos.y - this.options.offset.y);
            L.DomUtil.setPosition(this._container, op);
        },
        _initLayout: function() {
            // this._container = L.DomUtil.create('div', 'leaflet-label-overlay');
            this._container = L.DomUtil.create('div', 'leaflet-label-overlay');
            L.DomUtil.setTransform(this._container, L.Point(0,0))
            L.DomUtil.setPosition(this._container, L.Point(0,0))
        }
    });  
    coords = feature.geometry.coordinates[0][0];
    coords2 = [coords[1],coords[0]]
    var instance = new L.LabelOverlay(new L.latLng(coords2), feature.properties.name);
    map.addLayer(instance);
