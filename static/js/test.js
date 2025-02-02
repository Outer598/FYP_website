$(document).ready(function() {
    $(".header div button").on("click", function(){
        var actor = $(this).parent().attr('class');
        console.log(actor);

        $(".edit .edit-items label").text(`${actor}: `);
        $(".edit").removeClass("display");
    });

    $(".edit .cancel").on("click", function(){
        $(".edit").addClass("display");
    });

    $(".container .header-item button").on("click", function(){
        var actor = $(this).closest('.header-item').parent().attr('class');
        console.log(actor);

        $(".edit .edit-items label").text(`${actor}: `);
        $(".edit").removeClass("display");
    });
});