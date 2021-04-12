function fadeErrors() {
    const errors = document.getElementsByClassName("alert-danger")
    if (errors.length && opacity) {
        if (opacity == 1) {
            opacity -= 0.01
            setTimeout(fadeErrors, 2000)
        } else if (opacity>0) {
            for (var i=0;i<errors.length;i++) {
                errors[i].style.opacity = opacity
            }
            opacity -= 0.02
            setTimeout(fadeErrors, 50)
        } else {
            for (var i=errors.length-1;i>=0;i--) {
                errors[i].remove()
            }
        }
    }
}

opacity = 1
setTimeout(fadeErrors, 100)