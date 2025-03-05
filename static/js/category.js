$(document).ready(function(){
    $("#search-category").on("input", function() {
        const searchValue = $(this).val().toLowerCase().trim();
        
        // Get all container items except the template
        $(".container .container-item:not(:first)").each(function(index) {
            const categoryName = $(this).find(".category-name").text().toLowerCase();
            const categoryId = $(this).find(".category-id").text().toLowerCase();
            const categoryItems = $(this).find(".category-items").text().toLowerCase();
            
            // Check if any of the fields match the search value
            const matchFound = 
                categoryName.includes(searchValue) || 
                categoryId.includes(searchValue) || 
                categoryItems.includes(searchValue);
            
            // Toggle visibility with animation
            $(this)
                .toggleClass("hide", !matchFound)
                .css("--delay", index * 0.05 + "s");
        });
    });

    $(document).on("click", ".add-button", function(){
        console.log("clicked");
        $('.name-add').removeClass("display-type");
    });

    $(".name-add .add-actions .submit").on("click", function(e){
        e.preventDefault();
        const newCat= $(".name-add #create").val();
        console.log(newCat)
        $.ajax({
            url: "/api/category/all_categories",
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                "categoryName": newCat
            }),
            success: function(response){
                console.log(response);
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000);

                $(".name-add").addClass("display-type");
                setTimeout(function() {
                    location.reload();
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
    });

    $(".name-add .add-actions .cancel, .delete-actions .submit, .update-actions .cancel").on("click", function(e){
        e.preventDefault();
        $('.name-add').addClass("display-type");
        $('.delete-name').addClass("display-type");
        $('.edit-name').addClass("display-type");
    });

    let clickedId = "";
    $(document).on("click", ".delete", function(){

        var productName = $(this).closest('.actions').parent().find(".category-name").text();

        clickedId = $(this).closest(".container-item").find(".category-id").text();
        console.log("Category ID:", clickedId);

        $('.delete-name h3').text(`Are your sure you want to delete ${productName}?`);
        $('.delete-name').removeClass("display-type");
    });
    
    // Delete confirmation handler
    $(document).on("click", ".delete-name .delete-actions .cancel", function(e) {
        e.preventDefault();
        console.log("click")
        // Get the stored id
        const delID = clickedId;
    
        $.ajax({
            url: `/api/category/upDelCat/${delID}`,
            type: 'DELETE',
            contentType: 'application/json',
            success: function(response) {
                console.log('Success:', response);
            
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000);
            
                $('.delete-name').addClass("display-type"); // Hide delete prompt
                setTimeout(function() {
                    location.reload();
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
    
    let editId = "";
    $(document).on("click", ".edit", function(){
        console.log("clicked");
        let editName = $(this).closest('.actions').parent().find(".category-name").text();
        editId = $(this).closest('.actions').parent().find(".category-id").text();
        console.log(editId, editName);
        $('.edit-name #update').attr('value' ,`${editName}`);
        $('.edit-name').removeClass("display-type");
    });

    $(document).on("click", ".edit-name .update-actions .submit", function(e) {
        e.preventDefault();
        
        const editCategoryId = editId;
        const editedName = $(".edit-name #update").val();
        console.log(editCategoryId, editedName);
        $.ajax({
            url: `/api/category/upDelCat/${editCategoryId}`,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify({"category_name": editedName}),
            success: function(response) {
                console.log(response);
            
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000);
            
                $(".edit-name").addClass("display-type"); // Hide edit form
                setTimeout(function() {
                    location.reload();
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

    $(document).on('keydown', function(event) {
        if (event.key === "Escape" || event.key === "Enter" || event.key === "Delete") {
            event.preventDefault();  // Prevent the default action
        }
    });

    Categories();

    $(document).on("click", '.container-item .category-id, .container-item .category-name, .container-item .category-items', function(){
        const item= $(this).closest(".container-item");
        console.log(item);

        const itemId = item.find(".category-id").text();
        const itemName = item.find(".category-name").text();
        window.location.href = `/category/product?id=${itemId}&name=${itemName}`;
    })
});

function Categories(){
    $.ajax({
        url: `/api/category/all_categories`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            if (response.length !== 0){
                // Assuming your first row is a template
            const templateRow = $(".container-item").first();

            // Handle first row
            templateRow.find(".category-id").text(response[0].id);
            templateRow.find(".category-name").text(response[0].label);
            templateRow.find(".category-items").text(`${response[0].productCount}-Products`);
                
                // Then create new rows for remaining items
            for (let i = 1; i < response.length; i++) {
                // Clone the template row
                let newRow = templateRow.clone();
                
                // Update the cloned row with new data
                newRow.find(".category-id").text(response[i].id);
                newRow.find(".category-name").text(response[i].label);
                newRow.find(".category-items").text(`${response[i].productCount}-Products`);
                
                // Append the new row to the table body
                $(".container").append(newRow);
            }
            } else {
                $(".container").remove();
            };

        },
        error: function(xhr, status, error){
            console.log('error: ' + error)
        }
    });
}