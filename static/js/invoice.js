$(document).ready(function(){
    $("#search-invoice").on("input", function() {
        const searchValue = $(this).val().toLowerCase().trim();
        
        // Get all container items except the template
        $(".container .container-item:not(:first)").each(function(index) {
            const categoryName = $(this).find(".invoice-name").text().toLowerCase();
            const categoryId = $(this).find(".invoice-id").text().toLowerCase();
            const categoryItems = $(this).find(".invoice-items").text().toLowerCase();
            
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

    $(document).on('keydown', function(event) {
        if (event.key === "Escape" || event.key === "Enter" || event.key === "Delete") {
            event.preventDefault();  // Prevent the default action
        }
    });

    getinvoice();
    downloadInvoice();
})

function getinvoice(){
    $.ajax({
        url: `/api/invoice/all_invoice`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response)
            if (response.length !== 0){
                // Assuming your first row is a template
                const templateRow = $(".invoice.container .container-item").first();

                // Handle first row
                templateRow.find(".invoice-id").text(response[0].id);
                templateRow.find(".invoice-name").text(response[0].name);
                templateRow.find(".invoice-date").text(`${response[0].date}`);

                // Then create new rows for remaining items
                for (let i = 1; i < response.length; i++) {
                    // Clone the template row
                    let newRow = templateRow.clone();
                    
                    // Update the cloned row with new data
                    newRow.find(".invoice-id").text(response[i].id);
                    newRow.find(".invoice-name").text(response[i].name);
                    newRow.find(".invoice-date").text(`${response[i].date}`);
                    
                    // Append the new row to the table body
                    $(".invoice.container").append(newRow);
                }
            } else {
                $(".invoice.container").remove();
            };

        },
        error: function(xhr, status, error){
            console.log('error: ' + error)
        }
    });
}

function downloadInvoice(){
    $(document).on('click', '.invoice.container .container-item .actions .edit', function() {
        let container = $(this).closest(".container-item");
        let fileId = container.find(".invoice-id").text().trim();

        if (!fileId) {
            alert("File ID not found!");
            return;
        }

        $.ajax({
            url: `/api/invoice/downInvoice?id=${fileId}`,
            method: "GET",
            xhrFields: {
                responseType: 'blob'  // Crucial: treat response as binary data
            },
            beforeSend: function(xhr) {
                // Optional: Log request details for debugging
                console.log("Request URL:", xhr.url);
            },
            success: function(data, status, xhr) {
                // Log response headers for debugging
                console.log("Response Content-Type:", xhr.getResponseHeader('Content-Type'));
                console.log("Response Content-Disposition:", xhr.getResponseHeader('Content-Disposition'));

                let filename = "downloaded_file";  // Default filename
                let contentType = xhr.getResponseHeader("Content-Type") || 'application/octet-stream';

                // Extract filename from Content-Disposition header
                let disposition = xhr.getResponseHeader('Content-Disposition');
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    let matches = /filename="?([^"]+)"?/.exec(disposition);
                    if (matches && matches[1]) filename = matches[1];
                }

                // Create a Blob URL and trigger download
                let blob = new Blob([data], { type: contentType });
                let link = document.createElement("a");
                link.href = window.URL.createObjectURL(blob);
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            },
            error: function(xhr, status, error) {
                console.error('Download error:', error);
                console.log('Status:', status);
                console.log('Response:', xhr.responseText);

                $(".message").css("background", '#FF3131');
                $(".message h6").html(`Download failed: ${error}`);
                $(".message").fadeIn(1000).fadeOut(1000);
            }
        });
    });
}