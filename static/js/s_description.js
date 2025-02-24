$(document).ready(function(){
    function handleSearch(searchInput, containerSelector) {
        const value = searchInput.toLowerCase().trim();
        
        $(containerSelector + " .contianer-item").each(function(index) {
            const itemText = $(this).text().toLowerCase();
            const shouldShow = itemText.includes(value);
            
            $(this)
                .toggleClass("hide", !shouldShow)
                .css("--delay", (index * 0.05) + "s");
        });
    }

    // Product search
    $("#search-product").on("input", function() {
        handleSearch($(this).val(), ".productsec .container");
    });

    // Invoice search
    $("#search-invoices").on("input", function() {
        handleSearch($(this).val(), ".invoicesec .container");
    });

    // Receipt search
    $("#search-receipts").on("input", function() {
        handleSearch($(this).val(), ".receiptsec .container");
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

    $(document).on('click', '.productsec .actions .message-button', function(){
        $('.email').removeClass('display');
    });

    $(document).on('click', '.productsec .actions .reassign-button', function(){
        $('.reassign').removeClass('display');
    });
    
    $(document).on('click', '.receiptsec .head-section .special .add-button', function(){
        $('.receipt').removeClass('display');
    });

    $(document).on('click', '.email .email-actions .cancel, .receipt .receipt-actions .cancel, .reassign .reassign-actions .cancel, .delete .delete-actions .submit, .edit .edit-actions .cancel', function(){
        $('.email').addClass('display');
        $('.reassign').addClass('display');
        $('.receipt').addClass('display');
        $(".edit").addClass("display");
    });
})