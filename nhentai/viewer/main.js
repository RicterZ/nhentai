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
		toggler = document.getElementById("language")
		toggler.style.maxHeight = null;
		document.getElementsByClassName("accordion")[0].classList.toggle("active");
		var nav_btn = document.getElementsByClassName("nav-btn")[0];
		if (nav_btn.classList.contains("hidden")){
		  nav_btn.classList.toggle("hidden");
		}
		var node = filter_maker(this.innerText, "language");
		var check = filter_checker(this.innerText)
		if (check == true){
			nav_btn.appendChild(node);}
});
}
var category = document.getElementById("category").children;
for (var i = 0; i < category.length; i++){
	category[i].addEventListener("click", function() {
		document.getElementById("category").style.maxHeight = null;
		document.getElementsByClassName("accordion")[1].classList.toggle("active");

		var nav_btn = document.getElementsByClassName("nav-btn")[0];
		if (nav_btn.classList.contains("hidden")){
		  nav_btn.classList.toggle("hidden");
		}

		var node = filter_maker(this.innerText, "category");
		var check = filter_checker(this.innerText)
		if (check == true){
			nav_btn.appendChild(node);}
});
}
tag_maker(tags)
//-----------------------------------------------------------------------------------
//------------------------------------Functions--------------------------------------

function filter_maker(text, class_value){
    var node = document.createElement("a");
    var textnode = document.createTextNode(text);
    node.appendChild(textnode);
    node.classList.add(class_value);
    return node;
}

function filter_checker(text){
    var filter_tags = document.getElementsByClassName("nav-btn")[0].children;
	if (filter_tags == null){return true;}
	for (i in filter_tags){
		if (filter_tags[i].innerText == text){return false;}
	}
	return true;
}

function tag_maker(data){
	for (i in data){
		for (j in data[i]){
			var node = document.createElement("button");
			var textnode = document.createTextNode(data[i][j]);
			node.appendChild(textnode);
			node.classList.add("btn-2");
			node.classList.add(i);
			node.classList.add("hidden");
			document.getElementById("tags").appendChild(node);
		}
	}
}

var input = document.getElementById("tagfilter");

input.addEventListener("input", function() {
	var tags = document.querySelectorAll(".btn-2");
	if (this.value.length > 0) {
        for (var i = 0; i < tags.length; i++) {
            var tag = tags[i];
            var nome = tag.innerText;
            var exp = new RegExp(this.value, "i");;
            if (exp.test(nome)) {
                tag.classList.remove("hidden");
		    }
			else {
				tag.classList.add("hidden");
            }
        }
    } else {
        for (var i = 0; i < tags.length; i++) {
            var tag = tags[i];
				tag.classList.add('hidden');
        }
    }
});