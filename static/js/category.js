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

    $(".sidebar-toggler, .sidebar-menu-button").each(function(){
        $(this).on("click", function(){
            $(".table").toggleClass("widen");
        });
    });
    

    $(".edit").on("click", function(){
        const row = $(this).closest("tr");
        // console.log(row.text());

        const getColumnData = (index) => {
            return row.find('td').eq(index).text();
        };
        
        $(".edit-cat").removeClass("display-none");
        $(".table").addClass("opac");

        $(".edit-cat #category_name").attr("value", `${getColumnData(1)}`);
        
    });

    $("#edit-cancel, #add-cancel, #delete-cancel").on("click", function(e){
        e.preventDefault();

        $(".edit-cat, .add-cat, .delete-cat").addClass("display-none");
        $(".table").removeClass("opac");
    })

    $(".table-head .head button").on("click", function(){
        $(".add-cat").removeClass("display-none");
        $(".table").addClass("opac");
    });

    $(".delete").on("click", function(){
        const row = $(this).closest("tr");

        const getColumnData = (index) => {
            return row.find('td').eq(index).text();
        };

        $(".delete-cat h2").html(`Are you sure you want to Delete: ${getColumnData(1)}?`);
        $(".delete-cat").removeClass("display-none");
        $(".table").addClass("opac");
    });
})