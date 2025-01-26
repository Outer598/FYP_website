const categoryId = window.location.search.substring(1).split('&')[0].split('=')[1];

$(document).ready(function(){

    $(".head #lookUp").on("input", function() {
        let search_data = $(this).val().toLowerCase();
        
        // Get the rows dynamically each time instead of storing them
        $("tbody tr").each(function(index, element) {
            let table_data = $(element).text().toLowerCase();
            $(element).toggleClass("hide", table_data.indexOf(search_data) < 0)
                        .css("--delay", index/25 + "s");
        });
    });

    $(document).on("click", '.edit', function() {
        const row = $(this).closest("tr");
        
        const getColumnData = (index) => {
            return row.find('td').eq(index).text();
        };
        
        // Store the category ID for the update operation
        $(".edit-pro").data('categoryId', getColumnData(0));
        
        $(".edit-pro").removeClass("display-none");
        $(".table").addClass("opac");
        $(".edit-pro #product_name").attr("value", getColumnData(1));
        $(".edit-pro #in-stock").attr("value", getColumnData(3));
        $(".edit-pro #price").attr("value", getColumnData(2));
        $(".edit-pro #edit-reorder").attr("value", getColumnData(5));
        $(".edit-pro #edit-supply").attr("value", getColumnData(6));
    });

    $("#edit-cancel, #add-cancel, #delete-cancel").on("click", function(e){
        e.preventDefault();

        $(".edit-pro, .add-pro, .delete-pro").addClass("display-none");
        $(".table").removeClass("opac");
    });

    $(".table-head .head button").on("click", function(){
        $(".add-pro").removeClass("display-none");
        $(".table").addClass("opac");

        
    });

    $(document).on("click", '.delete', function() {
        const row = $(this).closest("tr");
        
        const getColumnData = (index) => {
            return row.find('td').eq(index).text().trim(); // Added trim() to remove whitespace
        };
    
        // Log the ID we're getting
        console.log("Category ID:", getColumnData(0));
    
        $(".delete-pro h2").html(`Are you sure you want to Delete: ${getColumnData(1)}?`);
        $(".delete-pro").removeClass("display-none");
        $(".table").addClass("opac");
        
        // Store the row data for later use
        $(".delete-pro").data('row', row);
    });

    topProducts();
    leastProducts();
    categoryProducts();
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
                const productRowTemplate = $('.product-list').first();
                productRowTemplate.find('.id').text(response[0].id);
                productRowTemplate.find('.name').text(response[0].name);
                productRowTemplate.find('.price').text(`₦ ${response[0].price}`);
                productRowTemplate.find('.instock').text(response[0]['in-stock']);
                productRowTemplate.find('.amountsold').text(response[0]['amount-sold']);
                productRowTemplate.find('.reorder').text(response[0]['reordering-threshold']);
                productRowTemplate.find('.supplier').html(`${response[0].supplier.split(' ')[0]} <br>${response[0].supplier.split(' ')[1]}`);

                for (let i = 1; i < response.length; i++){
                    let newProduct = productRowTemplate.clone();
                    newProduct.find('.id').text(response[i].id);
                    newProduct.find('.name').text(response[i].name);
                    newProduct.find('.price').text(`₦ ${response[i].price}`);
                    newProduct.find('.instock').text(response[i]['in-stock']);
                    newProduct.find('.amountsold').text(response[i]['amount-sold']);
                    newProduct.find('.reorder').text(response[i]['reordering-threshold']);
                    newProduct.find('.supplier').html(`${response[i].supplier.split(' ')[0]} <br>${response[i].supplier.split(' ')[1]}`);
                    
                    $('tbody').append(newProduct);

                } 
            } else {
                $(".product-list").remove();
            };
        },
    });
}