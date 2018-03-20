window.app = {}
let app = window.app

function button_definer(name,txt,clicked){
    return function(opt_options) {
      let options = opt_options || {}
  
      let button = document.createElement('button')
      button.innerHTML = txt
      let element = document.createElement('div')
      element.className = name+' ol-unselectable ol-control'
      element.appendChild(button)
      element.addEventListener("click",clicked)
      ol.control.Control.call(this, {
        element: element,
        target: options.target
      })
    }
}