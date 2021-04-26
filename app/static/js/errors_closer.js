function fadeErrors() {
    const errors = $(".alert-danger")
    if (errors.length && opacity) {
        if (opacity === 1) {
            opacity -= 0.01
            setTimeout(fadeErrors, 2000)
        } else if (opacity>0) {
            errors.each(function() {
                $(this).css({"opacity": opacity})
            })
            opacity -= 0.02
            setTimeout(fadeErrors, 50)
        } else {
            errors.remove()
        }
    }
}

opacity = 1
setTimeout(fadeErrors, 100)
