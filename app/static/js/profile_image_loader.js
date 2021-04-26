var counter = 0  // Нужен чтобы изображения не кэшировались
const validAvatarExtensions = [".png", ".jpg", ".jpeg", ".webp", ".ico", ".gif"]


function resetNewChatAvatar() {
    $("#new-user-avatar-img").attr("src", "/static/img/user_avatars/default/icon.png")
    $(this).css({"visibility": "hidden"})
}

function validateAvatar(avatar) {
    /**
     * Проверяет корректность расширения загруженного в качастве аватара файла
     */
    return validAvatarExtensions.some(elem => avatar.endsWith(elem))
}

function loadFile(file) {
    /**
     * Загружает файл, который пользователь хочет поставить в качестве аватара чата,
     * и тут же ставит его на аватар
     */
    if (validateAvatar(file.name)) {
        // Отправляется запрос на сервер для загрузки аватара
        $.ajax({
            url: "/js/load_temporary_chat_avatar",
            method: "PUT",
            data: file,
            processData: false,
            contentType: false,
            success: function(src) {
                // Установка нового аватара
                src+="?update_number="+counter
                // update_number нужен для того чтобы изображение не кэшировалось
                counter++
                $("#new-user-avatar-img").attr("src", src)
            }
        })
        $("#reset-new-user-avatar-btn").css({"visibility": "visible"})  // Отображается кнопка сброса аватара
    }
}

$(document).ready(function() {
    // Бинд кнопок
    $("#reset-new-user-avatar-btn").click(resetNewChatAvatar)

})

function closeAllWindows() {
    $("#reset-new-user-avatar-btn").css({"visibility": "hidden"})
}
