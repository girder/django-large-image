// Fill select drop down
var options = geo.osmLayer.tileSources;
for (const option in options) {
  var newOption = document.createElement('option');
  newOption.value = option;
  newOption.text = options[option].name ? options[option].name : option;
  document.getElementById('basemapDropdown').appendChild(newOption)
}

var basemapDropdown = document.getElementById("basemapDropdown")
basemapDropdown.value = basemapLayer.source()

function changeBasemap() {
  if (basemapDropdown.value == '-- none --') {
    basemapLayer.visible(false)
  } else {
    basemapLayer.visible(true)
    basemapLayer.source(basemapDropdown.value)
  }
}
