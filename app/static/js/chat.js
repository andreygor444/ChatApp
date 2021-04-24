function makeMessage(messageText, senderName, senderSurname, senderId, isMessageMy) {
    var class_ = "my-message"
    if (!isMessageMy) {
        class_ = "not-my-message"
    }
    return `<div class="chat-message">
                <div>
                    <img class="sender sender-${senderId} ${class_}-sender" name="${senderName}" surname="${senderSurname}" width="50" height="50" src="/static/img/user_avatars/${senderId}/icon.png" onerror="this.src = '/static/img/user_avatars/default/icon.png'">
                    <p class="${class_}">${messageText}</p>
                </div>
            </div>`
}

function checkNewMessages() {
    $.ajax({
        url: `/js/get_unread_messages/${chatId}`,
        method: "GET",
        success: function(messages) {
            messages.forEach(function(message_data) {
                $("#br").before(makeMessage(message_data.text, message_data.sender.name, message_data.sender.surname, message_data.sender_id, false))
                const message = $(".chat-message:last")
                bindSender(message.find(".sender"))
                const height = message.find('p').height()+30
                message.css({"height": 0, "padding-bottom": `${height}px`, "padding-top": 0, "margin-right": "10px"})
                document.getElementById("br").scrollIntoView(false)
            })
        }
    })
}

function sendMessage() {
    const messageText = $("#chat-message-input").val()
    $.ajax({
        url: `/js/send_message/${chatId}`,
        method: "POST",
        data: messageText,
        contentType: false,
        processData: false,
        success: function(message_data) {
            $("#br").before(makeMessage(messageText, message_data.sender_name, message_data.sender_surname, message_data.sender_id, true))
            const message = $(".chat-message:last")
            bindSender(message.find(".sender"))
            const height = message.find('p').height()+30
            message.css({"height": 0, "padding-bottom": `${height}px`, "padding-top": 0, "margin-right": "10px"})
            document.getElementById("br").scrollIntoView(false)
            $("#chat-message-input").val('')
        }
    })
}

function bindSender(sender) {
    /**
     * Биндит аватарку пользователя, отправившего сообщение,
     * чтобы при наведении выводилась табличка с именем и фамилией
     */
    sender.mouseenter(function() {
        const element = $(this)
        const senderId = element.attr("class").split('-')[1].split(' ')[0]
        const senderName = element.attr("name")
        const senderSurname = element.attr("surname")
        const offset = element.offset()
        const left = offset.left-35
        const bottom = window.innerHeight-offset.top+5
        $("body").append(makeHoverMemberNamePlate(left, bottom, senderName, senderSurname, senderId))
    })
    .mouseleave(function() {
        const senderId = $(this).attr("class").split('-')[1].split(' ')[0]
        $(`#chat-member-nameplate-${senderId}`).remove()
    })
}

const chatId = window.location.pathname.split('/').pop()

$(document).ready(function() {
    const headerHeight = $("header").height()
    $("#main-content").prepend(`<div style="height: ${headerHeight}px;"></div>`)
    const chatHeaderHeight = $("#chat-header").height()
    const inputHeight = $("#chat-message-input-container").height()
    $("#chat-message-list").height(document.documentElement.clientHeight-headerHeight-chatHeaderHeight-inputHeight-10)
    $("#chat-message-input-container").width("-=5px")
    messageInputWidth = $("#chat-message-input-container-inner").width()
    $("#chat-message-input")
    .width(messageInputWidth-105)
    .keyup(function(event) {
        if (event.which === 13 && $("#chat-message-input").val()) {
            sendMessage()
        }
    })
    const messages = $(".chat-message")
    messages.each(function(i) {
        const message = messages.eq(i)
        paragraph = message.find('p')
        const height = paragraph.height()+30
        message.css({"height": 0, "padding-bottom": `${height}px`, "padding-top": 0, "margin-right": "10px"})
    })

    document.getElementById("br").scrollIntoView(false)

    $("#send-message-btn").click(function() {
        if ($("#chat-message-input").val()) {
            sendMessage()
        }
    })

    bindSender($(".sender"))

    setInterval(checkNewMessages, 1000)
})