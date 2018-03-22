const wkt = new ol.format.WKT()
const proj = new ol.proj.Projection({code: "EPSG:4326"})


let source = new ol.source.Vector({
    features: data.map(e => wkt.readFeature(e[1]))
})
let vector = new ol.layer.Vector({
    source: source,
    style: new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.2)'
          }),
          stroke: new ol.style.Stroke({
            color: '#ffcc33',
            width: 2
          }),
          image: new ol.style.Circle({
            radius: 7,
            fill: new ol.style.Fill({
              color: '#ffcc33'
            })
          })
    })
})

let map = new ol.Map({
    target: 'map',
    controls: ol.control.defaults({
        attributionOptions: {
            collapsible: false
        }
    }),
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM()
      }),
      vector
    ],
    view: new ol.View({
      center: ol.proj.fromLonLat([0,0]),
      zoom: 2
    })
});