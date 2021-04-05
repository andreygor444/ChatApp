function fadeError() {
    const error = document.getElementsByClassName("form-error-message")[0]
    if (error && opacity) {
        if (opacity == 1) {
            opacity -= 0.01
            setTimeout(fadeError, 1000)
        } else if (opacity>0) {
            error.style.opacity = opacity
            opacity -= 0.02
            setTimeout(fadeError, 50)
        }
    }
}

opacity = 1
setTimeout(fadeError, 100)