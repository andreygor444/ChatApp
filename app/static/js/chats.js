var chatMemberIds = []  // Id пользователей, которые при создании нового чата будут добавлены в него

function checkNewMessages() {
    $.ajax({
        url: `/js/get_chats_with_unread_messages`,
        method: "GET",
        success: function(chats) {
            for (var chatId in chats) {
                const chat = $(`#chat-card-${chatId}`)
                chat.prependTo("#chat-list")
                const notifications = chat.find(".chat-notifications-container")
                if (notifications) {
                    notifications.remove()
                }
                const unreadMessages = chats[chatId].notifications
                var notificationsWidth
                switch (true) {
                    case unreadMessages<100:
                        notificationsWidth = 36
                        break
                    case unreadMessages<1000:
                        notificationsWidth = 55
                        break
                    case unreadMessages<10000:
                        notificationsWidth = 60
                        break
                    case unreadMessages<100000:
                        notificationsWidth = 70
                        break
                    case unreadMessages<1000000:
                        notificationsWidth = 85
                        break
                    case unreadMessages<10000000:
                        notificationsWidth = 100
                        break
                }
                chat.find("a").append(`<div class="inline chat-notifications-container">
                                           <div style="width: ${notificationsWidth}px;" class="chat-notifications">
                                               <span>${unreadMessages}</span>
                                           </div>
                                       </div>`)
                chat.find(".last-message-content").text(chats[chatId].last_message.text)
                chat.find(".last-message-sender-icon").attr("src", `/static/img/user_avatars/${chats[chatId].last_message.sender_id}/icon.png`)
                const dispatchDateTime = chats[chatId].last_message.dispatch_date
                const dispatchDate = dispatchDateTime.split(' ')[0]
                const dispatchTime = dispatchDateTime.split(' ')[1].slice(0, 5)
                chat.find(".last-message-dispatch-date>p").remove()
                chat.find(".last-message-dispatch-date").append(`<p>${dispatchDate}<br>${dispatchTime}</p>`)
            }
        }
    })
}

function makeNewChat(chatName, chatId, creatorId, firstMessageText, creationDate) {
    /**
     * Добавляет на страницу только что созданный чат
     */
    chat = `<div class="chat-card" id="chat-card-${chatId}">
                <a href="chats/${chatId}" class="link-but-not-link">
                    <div class="inline chat-avatar-container">
                        <img width="120" height="120" class="chat-avatar" src="/static/img/chat_avatars/${chatId}/icon.png" onerror="this.src = '/static/img/chat_avatars/default/icon.png'">
                    </div>
                    <div class="inline chat-card-info">
                        <div class="chat-title">
                            <h3>${chatName}</h3>
                        </div>
                        <div class="inline last-message">
                            <div class="inline last-message-sender-icon">
                                <img width="60" height="60" src="/static/img/user_avatars/${creatorId}/icon.png" onerror="this.src = '/static/img/user_avatars/default/icon.png'">
                            </div>
                            <div class="inline last-message-content">${firstMessageText}</div>
                            <div class="inline last-message-dispatch-date">
                                <p>${creationDate[0]}<br>${creationDate[1]}</p>
                            </div>
                        </div>
                    </div>
                    <div class="inline chat-notifications-container">
                        <div style="width: 36px;" class="chat-notifications">
                            <span>1</span>
                        </div>
                    </div>
                </a>
            </div>`
    $("#chat-list").prepend(chat)
}

function addChat() {
    chatName = $("#chat-name-input").val().trim()
    if (!chatName) {
        $("#chat-name-input").css({"color": "red", "border-color": "red"})
        return
    }
    closeAllWindows()
    if (chatMemberIds.length === 0) {
        chatMemberIds.push("none")
    }
    $.ajax({
        url: `/js/add_chat/${chatName}/${chatMemberIds.join(";")}`,
        method: "POST",
        data: $("#chat-avatar-loader").prop("files")[0],
        contentType: false,
        processData: false,
        success: function(json) {
            makeNewChat(chatName, json.chat_id, json.creator_id, json.first_message_text, json.date)
            clearAllWindows()
        }
    })
}

$(document).ready(function() {
    // Установка правильной ширины поля ввода названия чата
    width = Number($("#new-chat-data-input").css("width").slice(0, -2))-270+"px"
    $("#new-chat-name").css({"width": width})
    // Бинд кнопок
    $("#add-chat-btn").click(function() {
        $("#edit-chat-window").css({"visibility": "visible"})
        if ($("#chat-avatar-img").attr("src") !== "/static/img/chat_avatars/default/icon.png") {
            $("#reset-chat-avatar-btn").css({"visibility": "visible"})
        }
    })

    $("#apply-editing-chat-btn").click(addChat)

    setInterval(checkNewMessages, 1000)

    window.addEventListener( "pageshow", function ( event ) {
        if (event.persisted || ( typeof window.performance != "undefined" && window.performance.navigation.type === 2 )) {
            window.location.reload();
        }
    });
})
