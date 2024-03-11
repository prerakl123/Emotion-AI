function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function slideFlashMessages() {
    var flashes = document.getElementsByClassName("flashes");
    for (var i = 0; i < flashes.length; i++) {
        await sleep(4000);
        flashes[i].classList.add("slide-out");
        await sleep(800);
        flashes[i].style.display = 'none';
    }
}
