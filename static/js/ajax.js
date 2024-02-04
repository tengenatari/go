$(document).ready(function () {
    $(document.getElementById("Send-req-Button")).on('click', function (){

        let element = document.getElementById("select-user");
        let value = element.value
        let text = element.options[element.selectedIndex].text;

        req = $.ajax({
            url : '/send-request',
            type: 'POST',
            data : {user2 : value, opponent: text}
        })
        req.done(function(data){
            let div = document.createElement('div');
            div.className = 'game-block'
            div.id = 'game-block' + data['game_id']

            div.innerHTML = data['page']
            document.getElementById('first-block').append(div)
        });


    });
    $(document).on('click', ".user-btn", function (){

            let game_id = $(this).attr('game_id')
            let winner = $(this).attr('winner')

            req = $.ajax({
                url: '/update-game/update',
                type: 'POST',
                data : {game_id: game_id, winner: winner}
            });
        req.done(function (){
            var element = document.getElementById('game-block'+game_id)
            element.parentNode.removeChild(element)
        });

    });
    $(document).on('click', ".dec-btn", function (){
        let game_id = $(this).attr("game_id")
        req = $.ajax({
            url: '/update-game/delete',
            type: 'POST',
            data: {game_id: game_id}

        });

        req.done(function() {

            let element = document.getElementById('game-block'+game_id)
            element.parentNode.removeChild(element)
        });
    });
    $(document).on('click', ".acc-btn", function(){
        let game_id = $(this).attr("game_id")
        req = $.ajax({
            url: '/update-game/accept',
            type: 'POST',
            data: {game_id : game_id}
        });
        req.done(function() {

            let element = document.getElementById('game-block'+game_id)
            element.parentNode.removeChild(element)
        });
    });


});