const validAvatarExtensions = [".png", ".jpg", ".jpeg", ".webp", ".ico", ".gif"]
var counter = 0  // Нужен чтобы изображения не кэшировались


function makeFoundMemberBlock(memberName, memberSurname, memberId, prompt) {
    /**
     * Добавляет блок найденного пользователя при поиске участника когда создаёшь новый чат
     */
    prompt.append(
        `<div class="new-chat-member-variant">
            <div class="inline new-chat-member-variant-avatar-container">
                <img width="40" height="40" src="/static/img/user_avatars/${memberId}/icon.png" class="new-chat-member-variant-avatar" onerror="this.src = '/static/img/user_avatars/default/icon.png'">
            </div>
            <div class="inline new-chat-member-variant-info">
                <p>${memberName} ${memberSurname}</p>
                <p>id: ${memberId}</p>
            </div>
        </div>`
    )
}

function makeChatMember(memberId, memberName, memberSurname) {
    /**
     * Добавляет нового участника в список участников чата в окне создания чата
     */
    return `<img width="60" height="60" src="/static/img/user_avatars/${memberId}" class="new-chat-member" id="new-chat-member-${memberId}" name="${memberName}" surname="${memberSurname}" memberid="${memberId}" onerror="this.src = '/static/img/user_avatars/default/icon.png'">`
}

function makeRemoveMemberButton(leftIndent, bottomIndent, memberId) {
    /**
     * Добавляет на страницу кнопку удаления участника из создаваемого чата,
     * которая будет появляться при наведении курсора на иконку участника чата
     */
    $("body").append(
        `<button class="btn delete-member-btn" id="delete-member-${memberId}-from-new-chat-btn" memberid="${memberId}" style="left: ${leftIndent}px; bottom: ${bottomIndent}px">
            <img width="20" height="20" src="/static/img/close_button.png">
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
                counter++
                $("#chat-avatar-img").attr("src", `/${src}?update_number=${counter}`)
                // update_number нужен для того чтобы изображение не кэшировалось
            }
        })
        $("#reset-chat-avatar-btn").css({"visibility": "visible"})  // Отображается кнопка сброса аватара
    }
}

function searchMember() {
    /**
     * Отправляет запрос, введённый пользователем, на сервер и отображает пользователей, найденных по этому запросу
     */
    const value = $("#new-chat-member-name-input").val().trim()
    if (value) {
        $.ajax({
            url: "/js/find_user_helper/"+value,
            method: "GET",
            success: function(users) {
                const prompt = $("#new-chat-member-search-prompt")
                prompt.empty()
                for (i in users) {
                    const user = users[i]
                    if (!chatMemberIds.includes(user.id)) {
                        // Создание блока найденного пользователя
                        makeFoundMemberBlock(user.name, user.surname, user.id, prompt)
                        // Бинд блока найденного пользователя
                        $(prompt).children().last().click(function() {
                            $("#search-member-window").css({"visibility": "hidden"})  // Закрываем окно поиска пользователя
                            addMemberToChat(user.name, user.surname, user.id)
                        })
                    }
                }
            }
        })
    } else {
        $("#new-chat-member-search-prompt").empty()
    }
}

function bindMember(member) {
    member
    .mouseenter(function() {
        const memberId = Number(member.attr("memberid"))
        const memberName = member.attr("name")
        const memberSurname = member.attr("surname")
        if (!$(`#chat-member-nameplate-${memberId}`).length) {
            const self = $(this)
            const leftIndent = self.offset().left
            const bottomIndent = window.innerHeight-self.offset().top
            makeHoverMemberNamePlate(leftIndent-30, bottomIndent+5, memberName, memberSurname, memberId)
            makeRemoveMemberButton(leftIndent+30, bottomIndent-10, memberId)
            $(`#delete-member-${memberId}-from-new-chat-btn`)
            .click(function() {
                const memberId = Number($(this).attr("memberid"))
                $(this).remove()
                $(`#chat-member-nameplate-${memberId}`).remove()
                removeMemberFromChat(memberId)
            })
            .mouseleave(function() {
                const memberId = $(this).attr("memberid")
                if (!$(`#new-chat-member-${memberId}`).is(":hover")) {
                    $(`#chat-member-nameplate-${memberId}`).remove()
                    $(this).remove()
                }
            })
        }
    })
    .mouseleave(function() {
        const memberId = $(this).attr("memberid")
        const delBtn = $(`#delete-member-${memberId}-from-new-chat-btn`)
        if (!delBtn.is(":hover")) {
            $(`#chat-member-nameplate-${memberId}`).remove()
            delBtn.remove()
        }
    })
}

function addMemberToChat(memberName, memberSurname, memberId) {
    /**
     * Добавляет пользователя в список участников создаваемого чата
     */
    if (chatMemberIds.indexOf(memberId) !== -1) {
        return  // Если участник уже добавлен, добавлять его не нужно
    }
    chatMemberIds.push(memberId)
    const memberList = $("#new-chat-members-list")
    beforeHeight = memberList.height()
    $("#add-chat-member-btn").before(makeChatMember(memberId, memberName, memberSurname))  // Создание иконки добавленного участника
    member = $("#new-chat-members-list>.new-chat-member:last")
    if (memberList.height() > beforeHeight && $(".new-chat-member").length>1) {
        // Если список участников переполнен, нужно скрыть переполненную часть
        const allChatMembersList = $("#all-chat-members-list")
        member.appendTo(allChatMembersList)
        if (!$("#open-all-chat-members-window-btn").length) {
            $("#new-chat-members-list>.new-chat-member:last").prependTo(allChatMembersList)
            $("#add-chat-member-btn").before(`<img id="open-all-chat-members-window-btn" width="60" height="60" src="/static/img/add_button.png">`)
            $("#open-all-chat-members-window-btn")
            .click(function() {
                $("#search-member-window").css({"visibility": "hidden"})
                $("#chat-members-window").css({"visibility": "visible"})
            })
        }
    }
    // Бинд иконки добавленного участника
    bindMember(member)
}

function removeMemberFromChat(memberId) {
    const member = $(`#new-chat-member-${memberId}`)
    chatMemberIds.splice(chatMemberIds.indexOf(memberId), 1)
    const openMembersWindowBtn = $("#open-all-chat-members-window-btn")
    if (openMembersWindowBtn.length) {
        if (!$("#all-chat-members-list").has(member).length) {
            openMembersWindowBtn.before($("#all-chat-members-list>img:first"))
        }
        member.remove()
        const windowMembers = $("#all-chat-members-list>img")
        if (windowMembers.length === 1) {
            $("#chat-members-window").css({"visibility": "hidden"})
            openMembersWindowBtn.remove()
            $("#add-chat-member-btn").before($(windowMembers))
        }
    } else {
        member.remove()
    }
}

function resetChatAvatar() {
    $("#chat-avatar-img").attr("src", "/static/img/chat_avatars/default/icon.png")
    $(this).css({"visibility": "hidden"})
}

function clearAllWindows() {
    /**
     * Очищает все поля в окнах добавления чата и поиска пользователей
     */
    resetChatAvatar()
    $("#chat-name-input").val('')
    chatMemberIds = []
    $("#open-all-chat-members-window-btn").remove()
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
    $("#edit-chat-window").css({"visibility": "hidden"})
    $("#reset-chat-avatar-btn").css({"visibility": "hidden"})
    $("#search-member-window").css({"visibility": "hidden"})
    $("#chat-members-member-window").css({"visibility": "hidden"})
}


$(document).ready(function() {
    // Бинд полей ввода
    $("#chat-name-input").on("paste keyup", function() {
        $(this).css({"color": "#000", "border-color": "gray"})
    })
    $("#new-chat-member-name-input").on("paste keyup", searchMember)

    // Бинд кнопок
    $("#close-edit-chat-window-btn").click(function() {
        $("#chat-name-input").css({"color": "#000", "border-color": "gray"})
        closeAllWindows()
    })
    $("#reset-chat-avatar-btn").click(resetChatAvatar)
    $("#add-chat-member-btn").click(function () {
        $("#chat-members-window").css({"visibility": "hidden"})
        $("#search-member-window").css({"visibility": "visible"})
        searchMember()
    })
    $("#close-search-member-window-btn").click(function () {
        $("#search-member-window").css({"visibility": "hidden"})
    })
    $("#close-chat-members-member-window-btn").click(function() {
        $("#chat-members-window").css({"visibility": "hidden"})
    })

    // Задание правильного размера списку пользователей чата
    const windowInner = $("#chat-members-window-inner")
    const width = windowInner.width()
    const height = windowInner.height()
    const newWidth = width+20-width%67
    $("#all-chat-members-list").css({
        "width": newWidth,
        "height": height-60,
        "margin-left": Math.floor((width-newWidth)/2)
    })
})