const pages = Array.from(document.querySelectorAll('img.image-item'));
let currentPage = 0;
let showMetadata = 0;

function openMetadata() {
    var metadataPanel = document.getElementById("metadata-panel");
    if (showMetadata == 1) {
        metadataPanel.style.display = "none";
        showMetadata = 0;
    } else {
        metadataPanel.style.display = "block";
        showMetadata = 1;
    }
}

function changePage(pageNum) {
    const previous = pages[currentPage];
    const current = pages[pageNum];

    if (current == null) {
        return;
    }
    
    previous.classList.remove('current');
    current.classList.add('current');

    currentPage = pageNum;

    const display = document.getElementById('dest');
    display.style.backgroundImage = `url("${current.src}")`;

    document.getElementById('page-num')
        .innerText = [
                (pageNum + 1).toLocaleString(),
                pages.length.toLocaleString()
            ].join('\u200a/\u200a');
}

changePage(0);

document.getElementById('list').onclick = event => {
    if (pages.includes(event.target)) {
        changePage(pages.indexOf(event.target));
    }
};

document.getElementById('image-container').onclick = event => {
    const width = document.getElementById('image-container').clientWidth;
    const clickPos = event.clientX / width;

    if (clickPos < 0.5) {
        changePage(currentPage - 1);
    } else {
        changePage(currentPage + 1);
    }
};

document.onkeypress = event => {
    switch (event.key.toLowerCase()) {
        // Previous Image
        case 'w':
        case 'a':
            changePage(currentPage - 1);
            break;
        // Return to previous page
        case 'q':
            window.history.go(-1);
            break;
        // Next Image
        case ' ':
        case 's':
        case 'd':
            changePage(currentPage + 1);
            break;
    }// remove arrow cause it won't work
};

document.onkeydown = event =>{
    switch (event.keyCode) {
        case 37: //left
            changePage(currentPage - 1);
            break;
        case 38: //up
            changePage(currentPage - 1);
            break;
        case 39: //right
            changePage(currentPage + 1);
            break;
        case 40: //down
            changePage(currentPage + 1);
            break;
    }
};