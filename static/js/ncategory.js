$(document).ready(function(){
    $(".search-add #search-category").on("input", function() {
        var value = $(this).val().toLowerCase().trim(); // Ensure case-insensitive & no extra spaces
    
        $(".container .container-item").each(function(index, element) {
            var productData = $(element).text().toLowerCase();
            var match = productData.indexOf(value) >= 0;
    
            $(element)
                .toggleClass("hide", !match) // Hide non-matching items
                .css("--delay", index / 25 + "s");
        });
    });

    $(document).on("click", ".add-button", function(){
        console.log("clicked");
        $('.name-add').removeClass("display-type");
    });

    $(".name-add .add-actions .cancel, .delete-actions .submit").on("click", function(e){
        e.preventDefault();
        $('.name-add').addClass("display-type");
        $('.delete-name').addClass("display-type");
    });

    $(document).on("click", ".delete", function(){
        console.log("clicked");
        var productName = $(this).closest('.actions').parent().find(".category-name").text();
        console.log(productName)
        $('.delete-name h3').text(`Are your sure you want to delete ${productName}?`);
        $('.delete-name').removeClass("display-type");
    })
})