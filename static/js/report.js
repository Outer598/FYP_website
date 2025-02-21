$(document).ready(function(){

    $(".search-add #search-report").on("input", function() {
        var value = $(this).val().toLowerCase().trim(); // Ensure case-insensitive & no extra spaces
    
        $(".container .container-item").each(function(index, element) {
            var productData = $(element).text().toLowerCase();
            var match = productData.indexOf(value) >= 0;
    
            $(element)
                .toggleClass("hide", !match) // Hide non-matching items
                .css("--delay", index / 25 + "s");
        });
    });

    $.ajax({
        url: '/api/report/all_reports',
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response);
            if (response.length !== 0){
                const reportRowTemplate = $('.container-item').first();
                reportRowTemplate.find('.report-id').text(response[0].id);
                reportRowTemplate.find('.report-name').text(response[0].name);
                
                for (let i = 1; i < response.length; i++){
                    let newProduct = reportRowTemplate.clone();
                    newProduct.find('.report-id').text(response[i].id);
                    newProduct.find('.report-name').text(response[i].name);
                    
                    $('.container').append(newProduct);

                } 
            } else {
                $(".container").remove();
            };
        }
    });
    // Handle Download
    
    $(document).on('click', '.container-item .actions .submit',function() {
        let container = $(this).closest(".container-item");
        let fileId = container.find(".report-id").text().trim();

        if (!fileId) {
            alert("File ID not found!");
            return;
        }

        $.ajax({
            url: "/api/report/reports/" + fileId,
            method: "GET",
            xhrFields: {
                responseType: 'blob'  // Treat response as binary data
            },
            success: function(data, status, xhr) {
                let filename = "downloaded_file";  // Default filename

                // Extract filename from Content-Disposition header if available
                let disposition = xhr.getResponseHeader('Content-Disposition');
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    let matches = /filename="([^"]+)"/.exec(disposition);
                    if (matches && matches[1]) filename = matches[1];
                }

                // Create a Blob URL and trigger download
                let blob = new Blob([data], { type: xhr.getResponseHeader("Content-Type") });
                let link = document.createElement("a");
                link.href = window.URL.createObjectURL(blob);
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
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
    
    let delID = '';
    $(document).on("click", ".delete", function(){
        console.log("clicked");
        let container = $(this).closest(".container-item");
        let fileId = container.find(".report-id").text().trim()
        delID = fileId

        var reportName = $(this).closest('.actions').parent().find(".report-name").text();
        
        delId = $(this).closest('.actions').parent().find(".product-id").text();
        console.log(delId);
        
        $('.delete-name h3').text(`Are your sure you want to delete ${reportName}?`);
        $('.delete-name').removeClass("display-type");
    });

    $(".delete-actions .submit").on("click", function(e){
        e.preventDefault();
        $('.delete-name').addClass("display-type");
    });

    // Handle Delete
    $(document).on('click', '.delete-name .cancel',function() {
        let fileId = delID
        

        $.ajax({
            url: "/api/report/reports/" + parseInt(fileId),
            method: "DELETE",
            success: function(response) {
                
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);


                $(".message").fadeIn(1000).fadeOut(1000);
                $('.delete-name').addClass("display-type");
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
    
})