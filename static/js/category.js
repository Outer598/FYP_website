$(document).ready(function(){
    $(".search input").attr("placeholder", "Search for Categories");
 
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
    

    // Handler for showing the edit dialog
    $(document).on("click", '.edit', function() {
        const row = $(this).closest("tr");
        
        const getColumnData = (index) => {
            return row.find('td').eq(index).text();
        };
        
        // Store the category ID for the update operation
        $(".edit-cat").data('categoryId', getColumnData(0));
        
        $(".edit-cat").removeClass("display-none");
        $(".table").addClass("opac");
        $(".edit-cat #category_name").attr("value", getColumnData(1));
    });

    // Separate handler for the actual update operation
    $(document).on("click", ".edit-cat #update", function(e) {
        e.preventDefault();
        
        const categoryId = $(".edit-cat").data('categoryId');
        const editedName = $(".edit-cat #category_name").val();
        
        $.ajax({
            url: `/api/category/upDelCat/${categoryId}`,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify({"category_name": editedName}),
            success: function(response) {
                console.log(response);
                
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);

                $(".edit-cat").addClass("display-none");
                $(".table").removeClass("opac");
                $(".message").fadeIn(1000).fadeOut(1000)
                setTimeout(function() {
                    window.location.href = "/inventory";
                }, 2000);
            },
            error: function(xhr, status, error) {
                console.log('error: ' + error)
                let response = JSON.parse(xhr.responseText);

                $(".message").css("background", '#FF3131');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000)
            }
        });
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

                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);

                $(".add-cat").addClass("display-none");
                $(".table").removeClass("opac");
                $(".message").fadeIn(1000).fadeOut(1000)
                setTimeout(function() {
                    window.location.href = "/inventory";
                }, 2000); 
            },
            error: function(xhr, status, error){
                console.log('error: ' + error)
                let response =  JSON.parse(xhr.responseText);

                $(".message").css("background", '#FF3131');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000)
            }
        })
    })

    $(document).on("click", '.delete', function() {
        const row = $(this).closest("tr");
        
        const getColumnData = (index) => {
            return row.find('td').eq(index).text().trim(); // Added trim() to remove whitespace
        };
    
        // Log the ID we're getting
        console.log("Category ID:", getColumnData(0));
    
        $(".delete-cat h2").html(`Are you sure you want to Delete: ${getColumnData(1)}?`);
        $(".delete-cat").removeClass("display-none");
        $(".table").addClass("opac");
        
        // Store the row data for later use
        $(".delete-cat").data('row', row);
    });
    
    // Delete confirmation handler
    $(document).on("click", ".delete-cat #delete", function(e) {
        e.preventDefault();
        
        // Get the stored row
        const row = $(".delete-cat").data('row');
        const getColumnData = (index) => {
            return row.find('td').eq(index).text().trim();
        };
    
        // Log the URL and ID being used
        const categoryId = getColumnData(0);
        console.log("Delete URL:", `/api/category/upDelCat/${categoryId}`);
    
        $.ajax({
            url: `/api/category/upDelCat/${categoryId}`,
            type: 'DELETE',
            contentType: 'application/json',
            success: function(response) {
                console.log('Success:', response);
                
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
    
                $(".delete-cat").addClass("display-none");
                $(".table").removeClass("opac");
                $(".message").fadeIn(1000).fadeOut(1000);
                setTimeout(function() {
                    window.location.href = "/inventory";
                }, 2000);
            },
            error: function(xhr, status, error) {
                console.log('Error status:', xhr.status);
                console.log('Error response:', xhr.responseText);
                console.log('Error:', error);
                
                let errorMessage;
                try {
                    let response = JSON.parse(xhr.responseText);
                    errorMessage = response.message;
                } catch(e) {
                    errorMessage = 'An error occurred while deleting the category';
                }
    
                $(".message").css("background", '#FF3131');
                $(".message h6").html(errorMessage);
                $(".message").fadeIn(1000).fadeOut(1000);
            }
        });
    });

    Categories();

    $(document).on("click", '.category-container .category-list .id, .category-container .category-list .name, .category-container .category-list .product-count', function(){
        const item= $(this).closest("tr");
        console.log(item);

        const itemData = (index) => {
            return item.find('td').eq(index).text().trim(); // Added trim() to remove whitespace
        };
        const itemId = itemData(0);
        const itemName = itemData(1);

        window.location.href = `/category/product?id=${itemId}&name=${itemName}`;
    })
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