$(document).ready(function(){
    $(".search-add #search-supplier").on("input", function() {
        var value = $(this).val().toLowerCase().trim(); // Ensure case-insensitive & no extra spaces
    
        $(".container .container-item").each(function(index, element) {
            var productData = $(element).text().toLowerCase();
            var match = productData.indexOf(value) >= 0;
    
            $(element)
                .toggleClass("hide", !match) // Hide non-matching items
                .css("--delay", index / 25 + "s");
        });
    });

    $('.add-button').on('click', function(){
        $('.name-add').removeClass('display-type')
    })
    
    let delID = ''
    $(document).on('click', '.container .actions .delete', function(){
        let $row = $(this).closest('.container-item'); // or whatever your parent container class is
        let assignedProducts = $row.find('.supplier-items').text().split('-')[0];
        let supplierName = $row.find('.supplier-name').text();
        delID = $row.find('.supplier-id').text();
        
        if (parseInt(assignedProducts) !== parseInt(0)){
            $('.cannot-delete h3').text(`Cannot Delete ${supplierName}`);
            $('.cannot-delete').removeClass('display-type');
        } else{
            $('.delete-name h3').text(`Cannot Delete ${supplierName}`);
            $('.delete-name').removeClass('display-type');
        }
    });

    $('.name-add .add-actions .cancel').on('click', function(){
        $('.name-add').addClass('display-type')
    });
    
    $('.cannot-delete .submit, .delete-name .delete-actions .submit').on('click', function(){
        $('.cannot-delete').addClass('display-type');
        $('.delete-name').addClass('display-type');
    });

    $(document).on('keydown', function(event) {
        if (event.key === "Escape" || event.key === "Enter" || event.key === "Delete") {
            event.preventDefault();  // Prevent the default action
        }
    });

    $('.name-add .submit').on('click', function(e){
        e.preventDefault();

        const suppliersName = $('.name-add #name').val();
        const suppliersPhoneNo = $('.name-add #phoneno').val();
        const suppliersEmail = $('.name-add #email').val();
        const suppliersCompaniesName = $('.name-add #cname').val();
        const data = {
            'suppliersName': suppliersName,
            'suppliersPhoneNo': suppliersPhoneNo,
            'suppliersEmail': suppliersEmail,
            'suppliersCompaniesName': suppliersCompaniesName,
        }
        console.log(data)
        $.ajax({
            url: '/api/supplier/all_supplier',
            type: 'POST',
            contentType:'application/json',
            data: JSON.stringify(data),
            success: function(response){
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);

                $(".edit").addClass("display");
                $(".message").fadeIn(1000).fadeOut(1000)
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

    $(document).on('click', '.delete-name .delete-actions .cancel', function(e){
        e.preventDefault();


        $.ajax({
            url: `/api/supplier/all_supplier/${delID}`,
            type:'DELETE',
            contentType: 'application/json',
            success: function(response){
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
            
            
                $(".message").fadeIn(1000).fadeOut(1000);
                $('.delete-name').addClass("display-type");
                setTimeout(function() {
                    location.reload();
                }, 1000);
            },
            error: function(xhr, status, error){    
                console.log('error: ' + error)
                let response = JSON.parse(xhr.responseText);

                $(".message").css("background", '#FF3131');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000)
            }
        });
    });

    allSuppliers();
})

function allSuppliers(){
    $.ajax({
        url: '/api/supplier/all_supplier',
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
                // Assuming your first row is a template
                const templateRow = $(".container-item").first();

                // Handle first row
                templateRow.find(".supplier-id").text(response[0].id);
                templateRow.find(".supplier-name").text(response[0].name);
                templateRow.find(".supplier-items").text(`${response[0].assignedProduct}-Assinged`);

                // Then create new rows for remaining items
                for (let i = 1; i < response.length; i++) {
                    // Clone the template row
                    let newRow = templateRow.clone();
                    
                    // Update the cloned row with new data
                    newRow.find(".supplier-id").text(response[i].id);
                    newRow.find(".supplier-name").text(response[i].name);
                    newRow.find(".supplier-items").text(`${response[i].assignedProduct}-Assigned`);
                    
                    // Append the new row to the table body
                    $(".container").append(newRow);
            }
        },
        error: function(xhr, status, error){
            console.log('error: ' + error)
        }
    });
}