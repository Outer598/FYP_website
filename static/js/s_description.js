const supplierId = window.location.search.substring(1).split('&')[0].split('=')[1];

$(document).ready(function(){
   // Improved search function
    function handleSearch(searchInput, containerSelector) {
        const value = searchInput.toLowerCase().trim();
        
        $(containerSelector + " .container-item").each(function(index) {
            const itemText = $(this).text().toLowerCase();
            const shouldShow = itemText.includes(value);
            
            if (shouldShow) {
                $(this).removeClass("hide");
            } else {
                $(this).addClass("hide");
            }
            
            $(this).css("--delay", (index * 0.05) + "s");
        });
    }

    // Product search
    $("#search-product").on("input", function() {
        handleSearch($(this).val(), ".productsec");
    });

    // Invoice search
    $("#search-invoices").on("input", function() {
        handleSearch($(this).val(), ".invoicesec");
    });

    // Receipt search
    $("#search-receipts").on("input", function() {
        handleSearch($(this).val(), ".receiptsec");
    });

    $(document).on('click', '.sections nav ol li', function(){
        const trigger = $(this).text();
        console.log(trigger);

        if(trigger === 'Product'){
            $(".sections nav ol li .product-header span").addClass('active');
            $(".sections nav ol li .invoice-header span").removeClass('active');
            $(".sections nav ol li .receipt-header span").removeClass('active');

            $('.productsec').removeClass('display');
            $('.invoicesec').addClass('display');
            $('.receiptsec').addClass('display');
        } else if(trigger === 'Invoice'){
            $(".sections nav ol li .invoice-header span").addClass('active');
            $(".sections nav ol li .product-header span").removeClass('active');
            $(".sections nav ol li .receipt-header span").removeClass('active');

            $('.productsec').addClass('display');
            $('.invoicesec').removeClass('display');
            $('.receiptsec').addClass('display');
        } else if(trigger === 'Receipt'){
            $(".sections nav ol li .receipt-header span").addClass('active');
            $(".sections nav ol li .invoice-header span").removeClass('active');
            $(".sections nav ol li .product-header span").removeClass('active');

            $('.productsec').addClass('display');
            $('.invoicesec').addClass('display');
            $('.receiptsec').removeClass('display');
        }
    });

    let actor = ''
    $(".header div button, div .header-item button").on("click", function(){
        actor = $(this).parent().attr('class');
        
        if (actor === 'header-item'){
            actor = $(this).parent().parent().attr('class');
        }
        const currentValue = $(`.${actor} .supplierName, .${actor} .supplieremail, .${actor} .phoneNo, .${actor} .company`).text();
        
        
        $(".edit .edit-items label").text(`${actor}: `);
        $('.edit #edit').attr('value', `${currentValue}`);
        $(".edit").removeClass("display");
    });

    let productId = ''
    $(document).on('click', '.productsec .actions .message-button', function(){
        productId = $(this).closest(".actions").parent().find(".product-id").text();
        $('.email').removeClass('display');
        mailSupplier(productId)
    });

    // let productId = ''
    $(document).on('click', '.productsec .actions .reassign-button', function(){
        productId = $(this).closest(".actions").parent().find(".product-id").text();

        updateProduct(productId);
        $('.reassign').removeClass('display');
    });
    
    $(document).on('click', '.receiptsec .head-section .special .add-button', function(){
        $('.receipt').removeClass('display');
    });

    let clickedId = "";
    $(document).on("click", ".receiptsec .container .container-item.actions .delete-button", function(){

        var receiptName = $(this).closest('.actions').parent().find(".receipt-name").text();

        clickedId = $(this).closest(".actions").parent().find(".receipt-id").text();
        console.log("Report ID:", clickedId);

        $('.delete .delete-head-container .email-header').text(`Are your sure you want to delete ${receiptName}?`);
        $('.delete').removeClass("display");
    });

    $(document).on('click', '.email .email-actions .cancel, .receipt .receipt-actions .cancel, .reassign .reassign-actions .cancel, .delete .delete-actions .submit, .edit .edit-actions .cancel', function(){
        $('.email').addClass('display');
        $('.reassign').addClass('display');
        $('.receipt').addClass('display');
        $(".edit").addClass("display");
        $(".delete").addClass("display")
    });

    supplier();
    supplierInfo();
    supplierProducts();
})

function supplier() {
    $.ajax({
        url: '/api/Products/supplier',
        type: 'GET',
        contentType: 'application/json',
        success: function(response) {
            if (response.length !== 0) {
                const supplierSelect = $('#reassign');
                supplierSelect.empty();
                
                // Add suppliers to select
                response.supplierName.forEach(supplier => {
                    supplierSelect.append(new Option(supplier, supplier));
                });
                
            }
        }
    });
}

function updateProduct(productId) {
    $('.reassign .reassign-actions .submit').on('click', function(e){
        let changes = $('.reassign #reassign').val();
        console.log(productId)
        let dataToSend = {
            'supplier_id': changes
        }

        console.log(dataToSend);

        $.ajax({
            url: `/api/description/update?id=${productId}`,
            type: 'PATCH',
            contentType: 'application/json',
            data: JSON.stringify(dataToSend),
            success: function(response) {
                console.log(response);
                
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
}

function supplierInfo(){
    $.ajax({
        url: `/api/supplierDescription/info?id=${supplierId}`,
        type: 'GET',
        contentType:'application/json',
        success: function(response){

            // product core info
            $(document).find('.Name .supplierName').text(response.name);
            $(document).find('.Phone-No .phoneNo').text(response.phone);
            $(document).find('.Email .supplieremail').text(response.email);
            $(document).find('.Company .company').text(response.company);
        },
        error: function(xhr, status, error) {
            console.log('error: ' + error)
            let response = JSON.parse(xhr.responseText);

            $(".message").css("background", '#FF3131');
            $(".message h6").html(`${response.message}`);
            $(".message").fadeIn(1000).fadeOut(1000)
        }
    });
}

function supplierProducts(){
    $.ajax({
        url:`/api/supplierDescription/product?id=${supplierId}`,
        type:'GET',
        contentType: 'application/json',
        success: function(response){
            if (response.length !== 0){
                const productRowTemplate = $('.productsec .container .container-item').first();
                productRowTemplate.find('.product-id').text(response[0].id);
                productRowTemplate.find('.product-name').text(response[0].name);
                productRowTemplate.find('.stock').text(`${response[0].amount_remain} - remains`);
                
                for (let i = 1; i < response.length; i++){
                    let newProduct = productRowTemplate.clone();
                    newProduct.find('.product-id').text(response[i].id);
                    newProduct.find('.product-name').text(response[i].name);
                    newProduct.find('.stock').text(`${response[i].amount_remain} - remains`);
                    
                    $('.container').append(newProduct);

                } 
            } else {
                $(".productsec .container").remove();
            };
        },
    });
}

function mailSupplier(productId){

    $('.email .email-actions .submit').on('click', function(e){
        e.preventDefault();

        let amount = $('.email #email').val();
        console.log(productId)
        let dataToSend = {
            'amount': amount
        }

        console.log(dataToSend);

        $.ajax({
            url: `/api/supplierDescription/mail?id=${supplierId}&product_id=${productId}`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(dataToSend),
            success: function(response) {
                console.log(response);
                
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
}