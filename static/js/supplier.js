$(document).ready(function(){
    $('.add-button').on('click', function(){
        $('.name-add').removeClass('display-type')
    })
    
    $(document).on('click', '.container .actions .delete', function(){
        let $row = $(this).closest('.container-item'); // or whatever your parent container class is
        let assignedProducts = $row.find('.supplier-items').text().split('-')[0];
        let supplierName = $row.find('.supplier-name').text();
        
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