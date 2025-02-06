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
    monthlySR();
    yearlySR();
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

function monthlySR() {
    // Get the canvas context
    const canvas = $("#monthlySales");
    console.log(canvas);
    if (canvas.length === 0) {
        console.log("Canvas not needed or not found, skipping.");
        return; // Exit the function if canvas is not needed
    }
    const ctx = canvas[0].getContext("2d");

    // Helper function to format large numbers
    const formatNumber = (value) => {
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
        }
        return value;
    };
    
    $.ajax({
        url: `/api/description/monthly?id=${productId}`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response)
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: response.months,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: response.revenue,
                            borderColor: '#8A2BE2',
                            backgroundColor: 'rgba(138, 43, 226, 0.2)',
                            tension: 0.6,
                            fill: true,
                            pointRadius: 3,
                            pointHoverRadius: 4,
                            pointBackgroundColor: '#8A2BE2',
                            yAxisID: 'y-revenue'
                        },
                        {
                            label: 'Sales',
                            data: response.sales,
                            borderColor: '#87CEFA',
                            backgroundColor: 'rgba(135, 206, 250, 0.2)',
                            tension: 0.6,
                            fill: true,
                            pointRadius: 3,
                            pointHoverRadius: 4,
                            pointBackgroundColor: '#87CEFA',
                            yAxisID: 'y-sales'
                        },
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: true,
                        mode: 'point'
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
                            callbacks: {
                                title: function(tooltipItems) {
                                    return 'Year: ' + tooltipItems[0].label;
                                },
                                label: function(context) {
                                    const value = context.parsed.y;
                                    if (value === null) return null;
                                    
                                    if (context.dataset.label === 'Revenue') {
                                        return `Revenue: ${formatCurrency(value)}`;
                                    } else {
                                        return `Sales: ${formatNumber(value)}`;
                                    }
                                }
                            }
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
                        'y-revenue': {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,
                            title: {
                                display: false
                            },
                            ticks: {
                                maxTicksLimit: 6,
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return `₦${(value / 1000000).toFixed(1)}M`;
                                    } else if (value >= 1000) {
                                        return `₦${(value / 1000).toFixed(1)}K`;
                                    }
                                    return `₦${value}`;
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        'y-sales': {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            title: {
                                display: false
                            },
                            ticks: {
                                maxTicksLimit: 6,
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return `${(value / 1000000).toFixed(1)}M`;
                                    } else if (value >= 1000) {
                                        return `${(value / 1000).toFixed(1)}K`;
                                    }
                                    return value;
                                }
                            },
                            grid: {
                                display: false  // Hide grid lines for second axis
                            }
                        }
                    }
                }
            });
        
            // Helper function for formatting currency
            function formatCurrency(value) {
                if (value >= 1000000) {
                    return `₦${(value / 1000000).toFixed(2)}M`;
                } else if (value >= 1000) {
                    return `₦${(value / 1000).toFixed(2)}K`;
                }
                return new Intl.NumberFormat('en-NG', {
                    style: 'currency',
                    currency: 'NGN',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                }).format(value);
            }
        }        
    })
    
}

function yearlySR() {
    // Get the canvas context
    const canvas = $("#YearlySales");
    console.log(canvas);
    if (canvas.length === 0) {
        console.log("Canvas not needed or not found, skipping.");
        return; // Exit the function if canvas is not needed
    }
    const ctx = canvas[0].getContext("2d");

    // Helper function to format large numbers
    const formatNumber = (value) => {
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
        }
        return value;
    };
    
    $.ajax({
        url: `/api/description/yearly?id=${productId}`,
        type: 'GET',
        contentType: 'application/json',
        success: function(response){
            console.log(response)
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: response.years,
                    datasets: [
                        {
                            label: 'Revenue',
                            data: response.revenue,
                            borderColor: '#8A2BE2',
                            backgroundColor: 'rgba(138, 43, 226, 0.2)',
                            tension: 0.6,
                            fill: true,
                            pointRadius: 3,
                            pointHoverRadius: 4,
                            pointBackgroundColor: '#8A2BE2',
                            yAxisID: 'y-revenue'
                        },
                        {
                            label: 'Sales',
                            data: response.sales,
                            borderColor: '#87CEFA',
                            backgroundColor: 'rgba(135, 206, 250, 0.2)',
                            tension: 0.6,
                            fill: true,
                            pointRadius: 3,
                            pointHoverRadius: 4,
                            pointBackgroundColor: '#87CEFA',
                            yAxisID: 'y-sales'
                        },
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: true,
                        mode: 'point'
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
                            callbacks: {
                                title: function(tooltipItems) {
                                    return 'Year: ' + tooltipItems[0].label;
                                },
                                label: function(context) {
                                    const value = context.parsed.y;
                                    if (value === null) return null;
                                    
                                    if (context.dataset.label === 'Revenue') {
                                        return `Revenue: ${formatCurrency(value)}`;
                                    } else {
                                        return `Sales: ${formatNumber(value)}`;
                                    }
                                }
                            }
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
                        'y-revenue': {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,
                            title: {
                                display: false
                            },
                            ticks: {
                                maxTicksLimit: 6,
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return `₦${(value / 1000000).toFixed(1)}M`;
                                    } else if (value >= 1000) {
                                        return `₦${(value / 1000).toFixed(1)}K`;
                                    }
                                    return `₦${value}`;
                                }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        'y-sales': {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            title: {
                                display: false
                            },
                            ticks: {
                                maxTicksLimit: 6,
                                callback: function(value) {
                                    if (value >= 1000000) {
                                        return `${(value / 1000000).toFixed(1)}M`;
                                    } else if (value >= 1000) {
                                        return `${(value / 1000).toFixed(1)}K`;
                                    }
                                    return value;
                                }
                            },
                            grid: {
                                display: false  // Hide grid lines for second axis
                            }
                        }
                    }
                }
            });
        
            // Helper function for formatting currency
            function formatCurrency(value) {
                if (value >= 1000000) {
                    return `₦${(value / 1000000).toFixed(2)}M`;
                } else if (value >= 1000) {
                    return `₦${(value / 1000).toFixed(2)}K`;
                }
                return new Intl.NumberFormat('en-NG', {
                    style: 'currency',
                    currency: 'NGN',
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                }).format(value);
            }
        }        
    })
    
}

