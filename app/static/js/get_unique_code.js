function myFunction() {
  $.ajax({
            url: "/js/load_unique_link",
            dataType: 'text',
            success: function(code) {
                console.log("2")
                document.execCommand("copy");
                console.log("3")
            }
        })
}