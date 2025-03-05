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

    $(document).on('click', '.container-item .actions .cancel',function(){
        delName = $(this).parent().parent().find('.invoice-name').text();
        $('.delete-name h3').text(`Are you sure you want to delete ${delName}?`);
        $(".delete-name").removeClass('display-none')
    });
    
    $(".add-invoice #cancel, .delete-name .delete-actions .submit").on('click', function(){
        $(".add-invoice").addClass('display-none')
        $(".delete-name").addClass('display-none')
    });

    makeBold();
    uploadInvoice();
    getReceipt();
    loginInfo();
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
        console.log("Supplier ID:", supplierId);
    
        // Uncomment this AJAX request to enable file uploads
        $.ajax({
            url: `/api/supplierDescription/getReceipt?id=${supplierId}`,
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