$(document).ready(function(){
    $('#search').on('keyup', function() {
        const searchTerm = $(this).val().toLowerCase().trim();
        
        $('.container-item').each(function() {
            const invoiceId = $(this).find('.invoice-id').text().toLowerCase();
            const invoiceName = $(this).find('.invoice-name').text().toLowerCase();
            const invoiceDate = $(this).find('.invoice-date').text().toLowerCase();
            
            // Check if any of the invoice details match the search term
            const matches = 
                invoiceId.includes(searchTerm) || 
                invoiceName.includes(searchTerm) || 
                invoiceDate.includes(searchTerm);
            
            // Apply transition effect when showing/hiding items
            if (matches) {
                $(this).fadeIn(300);
            } else {
                $(this).fadeOut(300);
            }
        });
    });

    $(".search-add .add").on('click', function(){
        $(".add-invoice").removeClass('display-none')
    });

    invoiceId = ''
    $(document).on('click', '.container-item .actions .cancel',function(){
        delName = $(this).parent().parent().find('.invoice-name').text();
        invoiceId = $(this).parent().parent().find('.invoice-id').text();
        $('.delete-name h3').text(`Are you sure you want to delete ${delName}?`);
        $(".delete-name").removeClass('display-none')
    });
    
    $(".add-invoice #cancel, .delete-name .delete-actions .submit").on('click', function(){
        $(".add-invoice").addClass('display-none')
        $(".delete-name").addClass('display-none')
    });

    $(document).on('keydown', function(event) {
        if (event.key === "Escape" || event.key === "Enter" || event.key === "Delete") {
            event.preventDefault();  // Prevent the default action
        }
    });

    makeBold();
    uploadInvoice();
    getReceipt();
    getInvoice();
    loginInfo();
    downloadInvoice();
    downloadReceipt();
    deleteInvoice();
})

function makeBold(){
    if (window.location.pathname === '/supplier-dashboard') {
        $('.main-nav .invoice').addClass('bold');
        $('.main-nav .receipt').removeClass('bold');
    } else {
        $('.main-nav .invoice').removeClass('bold');
        $('.main-nav .receipt').addClass('bold');
    }
}

function uploadInvoice(){
    // Better to use one-time binding for the submit event
    $(document).off("click", ".add-invoice .upload-actions #submit").on("click", ".add-invoice .upload-actions #submit", function(e) {
        e.preventDefault();

        // Check if file is selected
        if (!$("#file")[0].files || !$("#file")[0].files[0]) {
            $(".message").css("background", '#FF3131');
            $(".message h6").html("Please select a file");
            $(".message").fadeIn(1000).fadeOut(1000);
            return;
        }

        // Check file type is one of the accepted formats
        const file = $("#file")[0].files[0];
        const fileType = file.type;
        const fileName = file.name;
        const fileExtension = fileName.split('.').pop().toLowerCase();
        
        // Array of accepted MIME types and extensions
        const acceptedMimeTypes = [
            "application/pdf",                           // PDF
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // DOCX
            "text/plain",                                // TXT
            "image/jpeg",                                // JPG/JPEG
            "image/png",                                 // PNG
            "image/tiff"                                 // TIF/TIFF
        ];
        
        const acceptedExtensions = ["pdf", "docx", "txt", "jpg", "jpeg", "png", "tif", "tiff"];
        
        if (!acceptedMimeTypes.includes(fileType) && !acceptedExtensions.includes(fileExtension)) {
            $(".message").css("background", '#FF3131');
            $(".message h6").html("Only PDF, DOCX, TXT, JPG, PNG, and TIF files are accepted");
            $(".message").fadeIn(1000).fadeOut(1000);
            return;
        }

        // Check if filename is provided
        const inputFileName = $("#name").val().trim();
        if (!inputFileName) {
            $(".message").css("background", '#FF3131');
            $(".message h6").html("Please provide a file name");
            $(".message").fadeIn(1000).fadeOut(1000);
            return;
        }

        console.log("File:", file);
        console.log("File name:", inputFileName);

        let formData = new FormData();
        formData.append("file", file);
        formData.append("file_name", inputFileName);

        console.log("FormData created, sending to server...");
    
        // Uncomment this AJAX request to enable file uploads
        $.ajax({
            url: `/api/receipt/upinvoice`,
            type: "POST",
            data: formData,
            processData: false,  // Important for FormData
            contentType: false,  // Important for FormData
            success: function(response) {
                console.log("Success response:", response);
                
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);

                $(".add-invoice").addClass("display-none"); // Hide the receipt form
                $(".message").fadeIn(1000).fadeOut(1000);
                setTimeout(function() {
                    location.reload();
                }, 2000);
            },
            error: function(xhr, status, error) {
                console.log('AJAX error:', error);
                console.log('Status:', status);
                console.log('Response text:', xhr.responseText);
                
                try {
                    let response = JSON.parse(xhr.responseText);
                    $(".message").css("background", '#FF3131');
                    $(".message h6").html(`${response.message}`);
                } catch (e) {
                    $(".message").css("background", '#FF3131');
                    $(".message h6").html("An error occurred while uploading the receipt");
                }
                
                $(".message").fadeIn(1000).fadeOut(1000);
            }
        });
    });
}

function getReceipt(){
    $.ajax({
        url: '/api/receipt/receipt',
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response);
            if (response.length !== 0){
                const receiptRowTemplate = $('.receipt .container-item').first();
                receiptRowTemplate.find('.receipt-id').text(response[0].id);
                receiptRowTemplate.find('.receipt-name').text(response[0].name);
                receiptRowTemplate.find('.receipt-date').text(`${response[0].date}`);
                console.log(response[0].supplier_id)
                
                for (let i = 1; i < response.length; i++){
                    let newreceipt = receiptRowTemplate.clone();
                    newreceipt.find('.receipt-id').text(response[i].id);
                    newreceipt.find('.receipt-name').text(response[i].name);
                    newreceipt.find('.receipt-date').text(`${response[i].date}`);
                    
                    $('.receipt.container').append(newreceipt);
                } 
            } else {
                $(".receipt.container").remove();
            };
        }
    })
}

function getInvoice(){
    $.ajax({
        url: '/api/receipt/invoice',
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response);
            if (response.length !== 0){
                const invoiceRowTemplate = $('.invoice .container-item').first();
                invoiceRowTemplate.find('.invoice-id').text(response[0].id);
                invoiceRowTemplate.find('.invoice-name').text(response[0].name);
                invoiceRowTemplate.find('.invoice-date').text(`${response[0].date}`);
                console.log(response[0].supplier_id)
                
                for (let i = 1; i < response.length; i++){
                    let newinvoice = invoiceRowTemplate.clone();
                    newinvoice.find('.invoice-id').text(response[i].id);
                    newinvoice.find('.invoice-name').text(response[i].name);
                    newinvoice.find('.invoice-date').text(`${response[i].date}`);
                    
                    $('.invoice.container').append(newinvoice);
                } 
            } else {
                $(".invoice.container").remove();
            };
        }
    })
}

function loginInfo(){
    $.ajax({
        url: "/whoami",
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response)
            $(".profile-sec .profile-sec-item span").html(`Welcome - ${response.user_name}`);
        },
        error: function(xhr, status, error){
        console.log('error: ' + error);
        }
    });
}

function downloadInvoice(){
    $(document).on('click', '.invoice .container-item .actions .add', function() {
        let container = $(this).closest(".container-item");
        let fileId = container.find(".invoice-id").text().trim();

        if (!fileId) {
            alert("File ID not found!");
            return;
        }

        $.ajax({
            url: `/api/receipt/downInvoice?id=${fileId}`,
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

function downloadReceipt(){
    $(document).on('click', '.receipt .container-item .actions .add', function() {
        let container = $(this).closest(".container-item");
        let fileId = container.find(".receipt-id").text().trim();

        if (!fileId) {
            alert("File ID not found!");
            return;
        }

        $.ajax({
            url: `/api/receipt/downReceipt?id=${fileId}`,
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

function deleteInvoice(){
    $(document).on('click', '.delete-name .delete-actions .cancel',function() {
        let fileId = invoiceId;
        console.log(fileId)

        $.ajax({
            url: "/api/receipt/downInvoice?id=" + parseInt(fileId),
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
}