$(document).ready(function(){
    $(".search input").attr("placeholder", "Search for Categories")
 
    // Move the search event handler inside document.ready but update how it works
    $(".search input").on("input", function() {
        let search_data = $(this).val().toLowerCase();
        
        // Get the rows dynamically each time instead of storing them
        $("tbody tr").each(function(index, element) {
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
    

    $(document).on("click", '.edit',function(){
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

        $(".add-cat #add").on("click", function(e){
            e.preventDefault();
            const newCat= $(".add-cat #category_name").val();
            
            $.ajax({
                url: "/api/category/all_categories",
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    "categoryName": newCat
                }),
                success: function(response){
                    console.log(response)
                    if (response.message === "Name cannot be empty"){
                        $(".message").css("background", '#FF3131');   
                        $(".message h6").html("Name cannot be empty");   
                    } else if (response.message === "Category created successfully"){
                        $(".message").css("background", '#228B22');
                        $(".message h6").html("Category created successfully");
                    } else if (response.message === "Error creating category"){
                        $(".message").css("background", '#FF3131');
                        $(".message h6").html("Error creating category");
                    } else if (response.message === "Item already in Database"){
                        $(".message").css("background", '#FF3131');
                        $(".message h6").html("Item already in Database");
                    }
                    $(".edit-cat, .add-cat, .delete-cat").addClass("display-none");
                    $(".table").removeClass("opac");
                    $(".message").fadeIn(1000).fadeOut(1000)
                    window.location.href = "/inventory"
                },
                error: function(xhr, status, error){
                    console.log('error: ' + error)
                    let response =  JSON.parse(xhr.responseText);

                    if (response.message === "Item already in Database"){
                        $(".message").css("background", '#FF3131');
                        $(".message h6").html("Item already in Database");
                    } else if (response.message === "Error creating category"){
                        $(".message").css("background", '#FF3131');
                        $(".message h6").html("Error creating category");
                    } else if (response.message === "Name cannot be empty"){
                        $(".message").css("background", '#FF3131');   
                        $(".message h6").html("Name cannot be empty");   
                    }
                    $(".message").fadeIn(1000).fadeOut(1000)
                }
            })
        })
    });

    $(document).on("click", '.delete',function(){
        const row = $(this).closest("tr");

        const getColumnData = (index) => {
            return row.find('td').eq(index).text();
        };

        $(".delete-cat h2").html(`Are you sure you want to Delete: ${getColumnData(1)}?`);
        $(".delete-cat").removeClass("display-none");
        $(".table").addClass("opac");
    });

    Categories();
})

function Categories(){
    $.ajax({
        url: `/api/category/all_categories`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            // Assuming your first row is a template
            const templateRow = $(".category-list").first();

            // Handle first row
            templateRow.find(".id").text(response[0].id);
            templateRow.find(".name").text(response[0].label);
            templateRow.find(".product-count").text(`${response[0].productCount} Products`);

            // Then create new rows for remaining items
            for (let i = 1; i < response.length; i++) {
                // Clone the template row
                let newRow = templateRow.clone();
                
                // Update the cloned row with new data
                newRow.find(".id").text(response[i].id);
                newRow.find(".name").text(response[i].label);
                newRow.find(".product-count").text(`${response[i].productCount} Products`);
                
                // Append the new row to the table body
                $("tbody").append(newRow);
            }

        },
        error: function(xhr, status, error){
            console.log('error: ' + error)
        }
    });
}