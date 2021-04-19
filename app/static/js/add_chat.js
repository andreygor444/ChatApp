var counter = 0  // Нужен чтобы изображения не кэшировались
const validAvatarExtensions = [".png", ".jpg", ".jpeg", ".webp", ".ico", ".gif"]
var newChatMemberIds = []  // Id пользователей, которые при создании нового чата будут добавлены в него

function makeFoundMemberBlock(memberName, memberSurname, memberId, prompt) {
    /**
     * Добавляет блок найденного пользователя при поиске участника когда создаёшь новый чат
     */
    prompt.append(
        `<div class="new-chat-member-variant">
            <div class="inline new-chat-member-variant-avatar-container">
                <img width="40" height="40" src="static/img/user_avatars/${memberId}/icon.png" class="new-chat-member-variant-avatar" onerror="this.src = 'static/img/user_avatars/default/icon.png'">
            </div>
            <div class="inline new-chat-member-variant-info">
                <p>${memberName} ${memberSurname}</p>
                <p>id: ${memberId}</p>
            </div>
        </div>`
    )
}

function makeNewChatMember(memberId) {
    /**
     * Добавляет нового участника в список участников чата в окне создания чата
     */
    $("#add-chat-member-btn").before(
        `<img width="60" height="60" src="static/img/user_avatars/${memberId}" class="new-chat-member" id="new-chat-member-${memberId}" onerror="this.src = 'static/img/user_avatars/default/icon.png'">`
    )
}

function makeHoverMemberNamePlate(bottomIndent, memberName, memberSurname, memberId) {
    /**
     * Добавляет на страницу небольшую табличку с именем и фамилией,
     * которая будет появляться при наведении курсора на иконку участника чата
     */
    $("body").append(
        `<div class="hover-chat-member-nameplate" id="chat-member-nameplate-${memberId}" style="bottom: ${bottomIndent}px">
            ${memberName} ${memberSurname}
        </div>`
    )
}

function makeRemoveMemberButton(bottomIndent, memberId) {
    /**
     * Добавляет на страницу кнопку удаления участника из создаваемого чата,
     * которая будет появляться при наведении курсора на иконку участника чата
     */
    $("body").append(
        `<button class="btn delete-member-btn" id="delete-member-${memberId}-from-new-chat-btn" style="bottom: ${bottomIndent}px">
            <img width="20" heinht="20" src="static/img/close_button.png">
        </button>`
    )
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
                $("#new-chat-avatar-img").attr("src", src)
            }
        })
        $("#reset-new-chat-avatar-btn").css({"visibility": "visible"})  // Отображается кнопка сброса аватара
    }
}

function searchMember() {
    /**
     * Отправляет запрос, введённый пользователем, на сервер и отображает пользователей, найденных по этому запросу
     */
    const value = $(this).val().trim()
    if (value) {
        $.ajax({
            url: "/js/find_user_helper/"+value,
            method: "GET",
            success: function(users) {
                const prompt = $("#new-chat-member-search-prompt")
                prompt.empty()
                for (i in users) {
                    const user = users[i]
                    // Создание блока найденного пользователя
                    makeFoundMemberBlock(user.name, user.surname, user.id, prompt)
                    // Бинд блока найденного пользователя
                    $(prompt).children().last().click(function() {
                        addMemberToNewChat(user.name, user.surname, user.id)
                    })
                }
            }
        })
    } else {
        $("#new-chat-member-search-prompt").empty()
    }
}

function addMemberToNewChat(memberName, memberSurname, memberId) {
    /**
     * Добавляет пользователя в список участников создаваемого чата
     */
    $("#search-member-window").css({"visibility": "hidden"})  // Закрываем окно поиска пользователя
    if (newChatMemberIds.indexOf(memberId) !== -1) {
        return  // Если участник уже добавлен, добавлять его не нужно
    }
    newChatMemberIds.push(memberId)
    const memberList = $("#new-chat-members-list")
    beforeHeight = memberList.height()
    makeNewChatMember(memberId)  // Создание иконки добавленного участника
    membersAndBtn = memberList.children()
    member = membersAndBtn.eq(membersAndBtn.length-2)
    if (memberList.height() > beforeHeight && membersAndBtn.length > 2) {
        // Если список участников переполнен, нужно скрыть переполненную часть
        member.remove()
        return // FIXME --------- ДОДЕЛАТЬ ЭТО -----------
    }
    const bottomIndent = window.innerHeight-member.offset().top
    // Создание всплывающей таблицы с именем и фамилией добавленного участника
    makeHoverMemberNamePlate(bottomIndent+5, memberName, memberSurname, memberId)
    // Создание кнопки удаления добавленного участника
    makeRemoveMemberButton(bottomIndent-10, memberId)
    // Бинд кнопки удаления добавленного участника
    $(`#delete-member-${memberId}-from-new-chat-btn`).click(function() {
        $(this).remove()
        $(`#chat-member-nameplate-${memberId}`).remove()
        $(`#new-chat-member-${memberId}`).remove()
        newChatMemberIds.splice(newChatMemberIds.indexOf(memberId), 1)
    })
    .mouseleave(function() {
        if (!$(`#new-chat-member-${memberId}`).is(":hover")) {
            $(`#chat-member-nameplate-${memberId}`).css({"visibility": "hidden"})
            $(this).css({"visibility": "hidden"})
        }
    })
    .css({"visibility": "hidden"})
    // Бинд иконки добавленного участника
    member.mouseenter(function() {
        const left = $(this).offset().left
        $(`#chat-member-nameplate-${memberId}`)
        .css({"left": left-30+"px", "visibility": "visible"})
        $(`#delete-member-${memberId}-from-new-chat-btn`)
        .css({"left": left+30+"px", "visibility": "visible"})
    })
    .mouseleave(function() {
        const delBtn = $(`#delete-member-${memberId}-from-new-chat-btn`)
        if (!delBtn.is(":hover")) {
            const namePlate = $(`#chat-member-nameplate-${memberId}`)
            namePlate.css({"visibility": "hidden"})
            delBtn.css({"visibility": "hidden"})
        }
    })
}

function addChat() {
    chatName = $("#new-chat-name-input").val()
    if (!chatName) {
        $("#new-chat-name-input").css({"color": "red", "border-color": "red"})
        return
    }
    closeAllWindows()
    if (newChatMemberIds.length == 0) {
        newChatMemberIds.push("none")
    } 
    $.ajax({
        url: `/js/add_chat/${chatName}/${newChatMemberIds.join(";")}`,
        method: "POST",
        data: $("#new-chat-avatar-loader").prop("files")[0],
        contentType: false,
        processData: false,
    })
    clearAllWindows()
}

function resetNewChatAvatar() {
    $("#new-chat-avatar-img").attr("src", "static/img/chat_avatars/default/icon.png")
    $(this).css({"visibility": "hidden"})
}

function clearAllWindows() {
    /**
     * Очищает все поля в окнах добавления чата и поиска пользователей
     */
    resetNewChatAvatar()
    $("#new-chat-name-input").val('')
    newChatMemberIds = []
    $(".new-chat-member").remove()
    $(".delete-member-btn").remove()
    $(".hover-chat-member-nameplate").remove()
    $("#new-chat-member-search-prompt").empty()
    $("#new-chat-member-name-input").val('')
}

function closeAllWindows() {
    /**
     * Закрывает окно добавления чата и окно поиска пользователей
     */
    $("#add-chat-window").css({"visibility": "hidden"})
    $("#reset-new-chat-avatar-btn").css({"visibility": "hidden"})
    $("#search-member-window").css({"visibility": "hidden"})
}

$(document).ready(function() {
    // Установка правильной ширины поля ввода названия чата
    width = Number($("#new-chat-data-input").css("width").slice(0, -2))-270+"px"
    $("#new-chat-name").css({"width": width})
    // Бинд полей ввода
    $("#new-chat-name-input").on("paste keyup", function() {
        $(this).css({"color": "#000", "border-color": "gray"})
    })
    $("#new-chat-member-name-input").on("paste keyup", searchMember)
    // Бинд кнопок
    $("#add-chat-btn").click(function() {
        $("#add-chat-window").css({"visibility": "visible"})
        if ($("#new-chat-avatar-img").attr("src") !== "static/img/chat_avatars/default/icon.png") {
            $("#reset-new-chat-avatar-btn").css({"visibility": "visible"})
        }
    })

    $("#close-add-chat-window-btn").click(function() {
        $("#new-chat-name-input").css({"color": "#000", "border-color": "gray"})
        closeAllWindows()
    })
    
    $("#reset-new-chat-avatar-btn").click(resetNewChatAvatar)

    $("#add-chat-member-btn").click(function () {
        $("#search-member-window").css({"visibility": "visible"})
    })

    $("#apply-adding-chat-btn").click(addChat)

    $("#close-search-member-window-btn").click(function () {
        $("#search-member-window").css({"visibility": "hidden"})
    })
})
