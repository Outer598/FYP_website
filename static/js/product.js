$(document).ready(function(){

    $(".head #search").on("input", function() {
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
        $(".edit-pro #in-stock").attr("value", getColumnData(2));
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
});

function topProducts(){
    const canvas = $("#myChart3")
  if (!canvas) {
        console.log("Canvas not needed or not found, skipping.");
        return; // Exit the function if canvas is not needed
    }
  const ctx = canvas[0].getContext("2d");

    new Chart(ctx, {
    type: 'bar',
    data: {
    labels: ['Rice', 'Yam', 'Garri'],
    datasets: [
        {
            label: 'Top Products',
            data: [4000, 3000, 2000],
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
function leastProducts(){
    const canvas = $("#myChart4")
  if (!canvas) {
        console.log("Canvas not needed or not found, skipping.");
        return; // Exit the function if canvas is not needed
    }
  const ctx = canvas[0].getContext("2d");

    new Chart(ctx, {
    type: 'bar',
    data: {
    labels: ['Rice', 'Yam', 'Garri'],
    datasets: [
        {
            label: 'Least Favourite',
            data: [1000, 500, 250],
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