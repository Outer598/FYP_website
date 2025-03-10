$(document).ready(function(){
    $('.message #submit').on('click', function(){
        
        title = $('.message #title').val()
        feedBack = $('.message #feedback').val()

        if(!title || !feedBack){
            $(".note").css("background", '#FF3131');
            $(".note h6").html("Title or Feed Back Missing");
            $(".note").fadeIn(1000).fadeOut(1000)
            return;
        }
        dataToSend = {
            'title': title,
            'feed_back': feedBack,
        };
        $.ajax({
            url: '/api/contact/postReview',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(dataToSend),
            success: function(response){
                $(".note").css("background", '#228B22');
                $(".note h6").html(response.message);
                $(".note").fadeIn(1000).fadeOut(1000)
                setTimeout(function() {
                    location.reload();
                }, 2000);
            }
        })
    });
});