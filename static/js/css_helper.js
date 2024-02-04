function myFunction(id) {
  document.getElementById("seasondrop" + id).classList.toggle("show");
}


window.onclick = function(event) {
  if (!event.target.matches('.seasondropbtn')) {
    var dropdowns = document.getElementsByClassName("seasongroup");
    var i;
    for (i = 0; i < dropdowns.length; i++) {
      var openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show')) {
        openDropdown.classList.remove('show');
      }
    }
  }
}