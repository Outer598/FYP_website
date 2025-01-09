$(document).ready(function(){
    $(".search input").attr("placeholder", "Search for Categories")

    const search = $(".search input"), table_body = $("tbody tr");

    search.on("input", function() {
        let search_data = $(this).val().toLowerCase();
        
        table_body.each(function(index, element) {
            let table_data = $(element).text().toLowerCase();
            $(element).toggleClass("hide", table_data.indexOf(search_data) < 0)
                     .css("--delay", index/25 + "s");
        });
    });

    $(".sidebar").on("click", function(){
        $(".table").toggleClass("widen");
    });

    $(".edit").each(function(){
        $(this).on("click", function(){
            $(".edit-add").removeClass("display-none");
            $(".table").addClass("opac");
        });
    });
    $("#cancel").on("click", function(e){
        e.preventDefault();

        $(".edit-add").addClass("display-none");
        $(".table").removeClass("opac");
    })
})