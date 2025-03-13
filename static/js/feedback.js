$(document).ready(function(){

    $("#search-feedback").on("input", function() {
        const searchValue = $(this).val().toLowerCase().trim();
        
        // Get all container items except the template
        $(".container .container-item:not(:first)").each(function(index) {
            const categoryName = $(this).find(".review-name").text().toLowerCase();
            const categoryId = $(this).find(".review-id").text().toLowerCase();
            const categoryItems = $(this).find(".date").text().toLowerCase();
            
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

    feedBack();

    let clickedId = "";
    $(document).on("click", ".container-item .actions .delete", function(){

        var productName = $(this).closest('.actions').parent().find(".review-name").text();

        clickedId = $(this).closest(".container-item").find(".review-id").text();
        console.log("feedback ID:", clickedId);

        $('.delete-name h3').text(`Are your sure you want to delete ${productName}?`);
        $('.delete-name').removeClass("display-type");
    });

    $(".delete-actions .submit").on("click", function(e){
        e.preventDefault();
        $('.delete-name').addClass("display-type");
    });

    $(document).on("click", ".delete-name .delete-actions .cancel", function(e) {
        e.preventDefault();
        console.log("click")
        // Get the stored id
        const delID = clickedId;
    
        $.ajax({
            url: `/api/feedback/delReview?id=${delID}`,
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

    $(document).on('click', '.container-item .actions .submit', function(){

        var Id = $(this).closest(".container-item").find(".review-id").text();
        console.log(Id)

        $.ajax({
            url: `/api/feedback/specReview?id=${Id}`,
            type: 'GET',
            contentType: 'application/json',
            success: function(response){
                $('.feedback-view h2').text(`Anonymous-${response.id}`);
                $('.feedback-view p').text(response.content);
            },
            error: function(xhr, status, error){
                console.log('error: ' + error)
            }
        });

        $('.feedback-view').removeClass("display-type");
    });

    $(".feedback-view .delete").on("click", function(e){
        e.preventDefault();
        $('.feedback-view').addClass("display-type");
    });
    
    $(document).on('keydown', function(event) {
        if (event.key === "Escape" || event.key === "Enter" || event.key === "Delete") {
            event.preventDefault();  // Prevent the default action
        }
    });
});

function feedBack(){
    $.ajax({
        url: `/api/feedback/getReview`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            if (response.length !== 0){
                // Assuming your first row is a template
            const templateRow = $(".container-item").first();

            // Handle first row
            templateRow.find(".review-id").text(response[0].id);
            templateRow.find(".review-name").text(response[0].name);
            templateRow.find(".date").text(response[0].date);
                
                // Then create new rows for remaining items
            for (let i = 1; i < response.length; i++) {
                // Clone the template row
                let newRow = templateRow.clone();
                
                // Update the cloned row with new data
                newRow.find(".review-id").text(response[i].id);
                newRow.find(".review-name").text(response[i].name);
                newRow.find(".date").text(response[i].date);
                
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