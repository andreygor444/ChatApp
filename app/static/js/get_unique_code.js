function getAndCopyUniqueCode() {
    $.ajax({
        url: "/js/get_invite_link_code",
        method: "GET",
        contentType: false,
        success: function(code) {
            $("body").append(`<span id="code-span">${code}</span>`)
            const codeSpan = $("#code-span")
            codeSpan.select()
            document.execCommand("copy")
            codeSpan.remove()
        }
    })
}
