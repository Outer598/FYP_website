const categoryId = window.location.search.substring(1).split('&')[0].split('=')[1];
const categoryName = window.location.search.substring(1).split('&')[1].split('=')[1];


$(document).ready(function(){
    $("#search-product").on("input", function() {
        const searchValue = $(this).val().toLowerCase().trim();
        
        // Get all container items except the template
        $(".container .container-item").each(function(index) {
            const categoryName = $(this).find(".category-name").text().toLowerCase();
            const categoryId = $(this).find(".category-id").text().toLowerCase();
            const categoryItems = $(this).find(".category-items").text().toLowerCase();
            
            // Check if any of the fields match the search value
            const matchFound = 
                categoryName.includes(searchValue) || 
                categoryId.includes(searchValue) || 
                categoryItems.includes(searchValue);
            
            // Toggle visibility with animation
            $(this)
                .toggleClass("hide", !matchFound)
                .css("--delay", index * 0.05 + "s");
        });
    });
    
    $(document).on("click", ".add-button", function(){
        console.log("clicked");
        $('.add-pro').removeClass("display-type");
    });

    $("#add-cancel, .delete-actions .submit").on("click", function(e){
        e.preventDefault();
        $('.add-pro').addClass("display-type");
        $('.delete-name').addClass("display-type");
    });

    $(document).on("click", ".add-pro #add", function(e){
        e.preventDefault();

        const newProductnName = $(".add-pro #add-product_name").val();
        const newProductPrice = $(".add-pro #add-price").val();
        const newProductInStock = $(".add-pro #add-in-stock").val();
        const newProductReorder = $(".add-pro #add-reorder").val();
        const newProductSupplier = $(".add-pro #add-supply").val();
        console.log(newProductnName, newProductPrice, newProductInStock, newProductReorder, newProductSupplier);

        $.ajax({
            url: `/api/Products/product?id=${categoryId}&name=${categoryName}`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                "productName": newProductnName,
                "price": newProductPrice,
                "stockLevel": newProductInStock,
                "reorderThreshold": newProductReorder,
                "supplierName": newProductSupplier
            }),
            success: function(response){
                console.log(response);
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
            
                $(".message").fadeIn(1000).fadeOut(1000);
                $('.add-pro').addClass("display-type");
                setTimeout(function() {
                    location.reload();
                }, 2000);
            }
            ,
            error: function(xhr, status, error){    
                console.log('error: ' + error)
                let response = JSON.parse(xhr.responseText);

                $(".message").css("background", '#FF3131');
                $(".message h6").html(`${response.message}`);
                $(".message").fadeIn(1000).fadeOut(1000)
            }
        });
    });

    let delId = ""
    $(document).on("click", ".delete", function(){
        console.log("clicked");
        var productName = $(this).closest('.actions').parent().find(".product-name").text();
        
        delId = $(this).closest('.actions').parent().find(".product-id").text();
        console.log(delId);
        
        $('.delete-name h3').text(`Are your sure you want to delete ${productName}?`);
        $('.delete-name').removeClass("display-type");
    });

    $(document).on("click", ".delete-name .delete-actions .cancel", function(e){
        e.preventDefault();
    
        // Log the URL and ID being used
        const productId = delId;
        console.log(productId);

        $.ajax({
            url: `/api/Products/upDelProd/${productId}`,
            type: 'DELETE',
            contentType: 'application/json',
            success: function(response){
                console.log(response);
                $(".message").css("background", '#228B22');
                $(".message h6").html(`${response.message}`);
            
                $(".message").fadeIn(1000).fadeOut(1000);
                $('.delete-name').addClass("display-type");
                setTimeout(function() {
                    location.reload();
                }, 2000);
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

    $(document).on('click', '.container-item .product-id, .container-item .product-name, .container-item .product-stock', function(){
        console.log('clicked')
        const item= $(this).closest(".container-item");
        const itemId = item.find('.product-id').text();
        const itemName = item.find('.product-name').text();
        console.log(itemId, itemName);
        window.location.href = `/product/description?id=${itemId}&name=${itemName}`
    });

    $(document).on('keydown', function(event) {
        if (event.key === "Escape" || event.key === "Enter" || event.key === "Delete") {
            event.preventDefault();  // Prevent the default action
        }
    });

    topProducts();
    leastProducts();
    categoryProducts();
    supplier();
});

function topProducts(){
    const canvas = $("#myChart3")
    if (!canvas) {
        console.log("Canvas not needed or not found, skipping.");
        return; // Exit the function if canvas is not needed
    }
    const ctx = canvas[0].getContext("2d");
    $.ajax({
        url: `/api/Products/topProduct?id=${categoryId}`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            new Chart(ctx, {
                type: 'bar',
                data: {
                labels: response.topProducts[0],
                datasets: [
                    {
                        label: 'Amount Sold',
                        data: response.topProducts[1],
                        borderColor: '#8A2BE2',
                        backgroundColor: 'rgba(138, 43, 226, 0.2)',
                        tension: 0.6,
                        fill: true,
                        pointRadius: 3,  // Make points larger
                        pointHoverRadius: 4,  // Make hover state even larger
                        pointBackgroundColor: '#8A2BE2'  // Match point color to line
                    }
                ]
                },
                options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: true,  // Only show tooltip when hovering directly over point
                    mode: 'point'     // Show tooltip for single point rather than all points at that x-value
                },
                plugins: {
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#000',
                        bodyColor: '#000',
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        padding: 12,
                        borderColor: '#ddd',
                        borderWidth: 1,
                        displayColors: true,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: false
                        },
                        grid: {
                            display: true,
                            borderDash: [5, 5],
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: false
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        border: {
                            display: false
                        }
                    }
                }
                }
                });
        },
        error: function(xhr, error, status){
            console.log('error: ' + error)
        }
    });
}
function leastProducts(){
    const canvas = $("#myChart4")
    if (!canvas) {
            console.log("Canvas not needed or not found, skipping.");
            return; // Exit the function if canvas is not needed
        }
    const ctx = canvas[0].getContext("2d");

    $.ajax({
        url: `/api/Products/topProduct?id=${categoryId}`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            new Chart(ctx, {
                type: 'bar',
                data: {
                labels: response.leastProducts[0],
                datasets: [
                    {
                        label: 'Amount Sold',
                        data: response.leastProducts[1],
                        borderColor: '#8A2BE2',
                        backgroundColor: 'rgba(138, 43, 226, 0.2)',
                        tension: 0.6,
                        fill: true,
                        pointRadius: 3,  // Make points larger
                        pointHoverRadius: 4,  // Make hover state even larger
                        pointBackgroundColor: '#8A2BE2'  // Match point color to line
                    }
                ]
                },
                options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: true,  // Only show tooltip when hovering directly over point
                    mode: 'point'     // Show tooltip for single point rather than all points at that x-value
                },
                plugins: {
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#000',
                        bodyColor: '#000',
                        titleFont: {
                            size: 14,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 13
                        },
                        padding: 12,
                        borderColor: '#ddd',
                        borderWidth: 1,
                        displayColors: true,
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: false
                        },
                        grid: {
                            display: true,
                            borderDash: [5, 5],
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: false
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        border: {
                            display: false
                        }
                    }
                }
                }
            });
        }
    });
}


function categoryProducts(){
    $.ajax({
        url:`/api/Products/product?id=${categoryId}`,
        type:'GET',
        contentType: 'application/json',
        success: function(response){
            if (response.length !== 0){
                const productRowTemplate = $('.container-item').first();
                productRowTemplate.find('.product-id').text(response[0].id);
                productRowTemplate.find('.product-name').text(response[0].name);
                productRowTemplate.find('.product-stock').text(`${response[0]['in-stock']} - remains`);
                
                for (let i = 1; i < response.length; i++){
                    let newProduct = productRowTemplate.clone();
                    newProduct.find('.product-id').text(response[i].id);
                    newProduct.find('.product-name').text(response[i].name);
                    newProduct.find('.product-stock').text(`${response[i]['in-stock']} - remains`);
                    
                    $('.container').append(newProduct);

                } 
            } else {
                $(".container").remove();
            };
        },
    });
}

function supplier() {
    $.ajax({
        url: '/api/Products/supplier',
        type: 'GET',
        contentType: 'application/json',
        success: function(response) {
            if (response.length !== 0) {
                const supplierSelect = $('#add-supply');
                supplierSelect.empty();
                
                // Add suppliers to select
                response.supplierName.forEach(supplier => {
                    supplierSelect.append(new Option(supplier, supplier));
                });
                
            }
        }
    });
}