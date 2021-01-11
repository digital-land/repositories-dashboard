function onFilterSearch() {
  input = document.getElementById('filter-search-input');
  filter = input.value.toUpperCase();
  panelGroup = document.getElementById("repos-panel-group");
  panels = panelGroup.getElementsByClassName('panel');

  for (i = 0; i < panels.length; i++) {
    a = panels[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      panels[i].classList.remove("hide-from-search")
    } else {
      panels[i].classList.add("hide-from-search")
    }
  }
}

function onClickHideSuccessful() {
    var chk = document.getElementById("hide-success-checkbox").checked;
    panelGroup = document.getElementById("repos-panel-group");
    panels = panelGroup.getElementsByClassName('panel');

    if(chk) {
         for (i = 0; i < panels.length; i++) {
            if (panels[i].getElementsByClassName("panel-build-failure").length) {
              panels[i].classList.remove("hide-from-success-checkbox")
            } else {
              panels[i].classList.add("hide-from-success-checkbox")
            }
        }
    } else {
         for (i = 0; i < panels.length; i++) {
              panels[i].classList.remove("hide-from-success-checkbox")
        }
    }
}
