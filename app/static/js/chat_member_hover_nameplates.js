function makeHoverMemberNamePlate(leftIndent, bottomIndent, memberName, memberSurname, memberId) {
    /**
     * Добавляет на страницу небольшую табличку с именем и фамилией,
     * которая будет появляться при наведении курсора на иконку участника чата
     */
    $("body").append(
        `<div class="hover-chat-member-nameplate" id="chat-member-nameplate-${memberId}" style="left: ${leftIndent}px; bottom: ${bottomIndent}px">
            ${memberName} ${memberSurname}
        </div>`
    )
}
