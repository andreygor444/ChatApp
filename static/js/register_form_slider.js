setTimeout ( function() {
    var scrollbar = document.getElementsByClassName("simplebar-scrollbar")[1]
    var scrollbar_height = Number(scrollbar.style.height.slice(0, -2))
    scrollbar.style.height = scrollbar_height - 40 + "px"
}, 300)