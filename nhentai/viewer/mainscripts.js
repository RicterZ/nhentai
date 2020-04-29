function Search() {
    var input = document.getElementById("gallery-search").value.split(",");
    var galleries = document.getElementsByClassName("gallery");
    var galleriesArr = Array.from(galleries);

    galleriesArr.forEach(gallery => filter(gallery));

    function filter(gallery) {
        metadata = gallery.dataset.metadata;

        input.forEach(function(searchterm) {
            if(isMatch(metadata, searchterm)) {
                gallery.parentNode.style.display = "";
            }
            else {
                gallery.parentNode.style.display = "none";
            }
        });
    }

    function isMatch(searchOnString, searchText) {
        searchText = searchText.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        return searchOnString.match(new RegExp("\\b"+searchText, "i")) != null;
    }
}