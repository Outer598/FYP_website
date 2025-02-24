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
            $(".sections nav ol li .product span").addClass('active');
            $(".sections nav ol li .invoice span").removeClass('active');
            $(".sections nav ol li .receipt span").removeClass('active');

            $('.productsec').removeClass('display');
            $('.invoicesec').addClass('display');
            $('.receiptsec').addClass('display');
        } else if(trigger === 'Invoice'){
            $(".sections nav ol li .invoice span").addClass('active');
            $(".sections nav ol li .product span").removeClass('active');
            $(".sections nav ol li .receipt span").removeClass('active');

            $('.productsec').addClass('display');
            $('.invoicesec').removeClass('display');
            $('.receiptsec').addClass('display');
        } else if(trigger === 'Receipt'){
            $(".sections nav ol li .receipt span").addClass('active');
            $(".sections nav ol li .invoice span").removeClass('active');
            $(".sections nav ol li .product span").removeClass('active');

            $('.productsec').addClass('display');
            $('.invoicesec').addClass('display');
            $('.receiptsec').removeClass('display');
        }
    })
})