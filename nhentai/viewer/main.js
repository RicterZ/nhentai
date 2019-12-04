//------------------------------------navbar script------------------------------------
var menu = document.getElementsByClassName("accordion");
for (var i = 0; i < menu.length; i++) {
  menu[i].addEventListener("click", function() {
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
	  this.classList.toggle("active");
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
	  this.classList.toggle("active");
    }
  });
}
var language = document.getElementById("language").children;
for (var i = 0; i < language.length; i++){
	language[i].addEventListener("click", function() {
		document.getElementById("language").style.maxHeight = null;
		document.getElementsByClassName("accordion")[0].classList.toggle("active");

		var toggler = document.getElementsByClassName("nav-btn")[0].classList;
				if (toggler.contains("hidden")){
		  toggler.toggle("hidden");
		}
});
}
var category = document.getElementById("category").children;
for (var i = 0; i < category.length; i++){
	category[i].addEventListener("click", function() {
		document.getElementById("category").style.maxHeight = null;
		document.getElementsByClassName("accordion")[1].classList.toggle("active");

		var toggler = document.getElementsByClassName("nav-btn")[0].classList;
				if (toggler.contains("hidden")){
		  toggler.toggle("hidden");
		}
});
}
//-----------------------------------------------------------------------------------
var tags = document.getElementById("tags");
for (i in data){
	tag_maker(data[i])
}
function tag_maker(data){
	var options = ["parody", "character", "tag", "artist", "group"];
		for (i in options){
			var i = options[i]
			if (data[i] != null){
				for (j in data[i]){
					var node = document.createElement("button");                   // Create a <li> node
					var textnode = document.createTextNode(data[i][j]);  					// Create a text node
					node.appendChild(textnode);                             // Append the text to <li>
					node.classList.add("btn-2");
					node.classList.add("parody");
					document.getElementById(i).appendChild(node);
					console.log("teste");
				}
			}
		}
}