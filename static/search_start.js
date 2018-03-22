const wkt = new ol.format.WKT()
const proj = new ol.proj.Projection({code: "EPSG:4326"})


let source = new ol.source.Vector()
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
app.ClearControl = button_definer("clear","\uf1f8",e => {
    source.clear()
})

ol.inherits(app.ClearControl,ol.control.Control)

let map = new ol.Map({
    target: 'map',
    controls: ol.control.defaults({
        attributionOptions: {
            collapsible: false
        }
    }).extend([
        new app.ClearControl()
    ]),
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

//map.addInteraction(new ol.interaction.Modify({source: source}))

function addInteractions(){
    let draw = new ol.interaction.Draw({
        source: source,
        type: "Circle",
        geometryFunction: ol.interaction.Draw.createBox()
    })
    draw.on('drawend',e => {
        document.querySelector('input[name=wkt]').value = wkt.writeFeature(e.feature)
        document.querySelector('form').submit()
    })
    map.addInteraction(draw)
    map.addInteraction(new ol.interaction.Snap({source: source}))
}
addInteractions()