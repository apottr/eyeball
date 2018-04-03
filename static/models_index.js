Element.prototype.removeAll = function () {
    while (this.firstChild) { this.removeChild(this.firstChild); }
    return this;
};
  
function makeGraph(el,g){
    let grph = g
    let graph = Viz(`
    digraph g {
      rankdir="LR"
      ${grph}
    }
    `,{"format": "png-image-element"})
    el.removeAll()
    el.appendChild(graph)
  }

  document.querySelectorAll("td[data-graph]").map(e => {
      makeGraph(e,e.dataset.graph)
  })