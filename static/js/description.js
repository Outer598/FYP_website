const productId = window.location.search.substring(1).split('&')[0].split('=')[1];

$(document).ready(function() {
    $(".header div button").on("click", function(){
        var actor = $(this).parent().attr('class');
        console.log(actor);

        $(".edit .edit-items label").text(`${actor}: `);
        $(".edit").removeClass("display");
    });

    $(".edit .cancel").on("click", function(){
        $(".edit").addClass("display");
    });

    $(".container .header-item button").on("click", function(){
        var actor = $(this).closest('.header-item').parent().attr('class');
        console.log(actor);

        $(".edit .edit-items label").text(`${actor}: `);
        $(".edit").removeClass("display");
    });

    productInfo();
});

function productInfo(){
    $.ajax({
        url: `/api/description/get_product_info?id=${productId}`,
        type: 'GET',
        contentType:'application/json',
        success: function(response){
            console.log(response);

            // product core info
            $(document).find('.name .productName').text(response.productName);
            $(document).find('.supplier .suppliersName').text(response.SupplierName);
            $(document).find('.price .pricecon').text(`₦ ${response.price}`);

            //further info
            $(document).find('.currentStock .instock').text(response.currentStockLevel);
            $(document).find('.originalStock .original').text(response.originalStockLevel);
            $(document).find('.reorderlevel .reorder').text(response.reorderingThreshold);
            $(document).find('.AmountSold .amountsold').text(response.AmountSold);
        },
    });
}