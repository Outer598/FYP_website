$(document).ready(function(){
    $(".sidebar-toggler, .sidebar-menu-button").each(function(){
       $(this).on("click", function(){
            closeAllDropdowns();
    
    
            const toggled = $(".sidebar").toggleClass("collapsed");
            if(toggled){
              $(".chart-container.salrev").toggleClass("fit-toggle");
              $(".income-container").toggleClass("income-container-toggle");
              $(".recent-orders").toggleClass("recent-orders-toggle");
              $(".search-profile").toggleClass("search-toggle");
            }else{
              $(".chart-container.salrev").togglClass("fit-toggle");
            $(".income-container").toggleClass("income-container-toggle");
            $(".recent-orders").toggleClass("recent-orders-toggle");
            $(".search-profile").toggleClass("search-toggle");
            }
       });
    });

    $(".dropdown-toggle").each(function() {
        $(this).on("click", function(e){
            e.preventDefault();

            const dropdown = $(e.target).closest(".dropdown-container");
            const menu  = dropdown.find(".dropdown-menu")[0];
            const isOpen = dropdown.hasClass("open");

            closeAllDropdowns();

            toggleDropdown(dropdown, menu, !isOpen);
        });
        
    });

    if (window.innerWidth <= 1024) {
        $(".sidebar").toggleClass("collapsed");
    }

    $(".search input").on("focus", function(){
      $(".search button").css("color", "rgba(21, 26, 46, 0.5)")
    })
    $(".search input").on("blur", function(){
      $(".search button").css("color", "rgba(21, 26, 46, 0.2)")
    })

    // for graph data calls
    salRevenue();
    topCategories();
    periodicRevenue();
});

function toggleDropdown(dropdown, menu, isOpen){
    $(dropdown).toggleClass("open", isOpen);
    $(menu).css("height", isOpen ? `${menu.scrollHeight}px` : 0);
}

function closeAllDropdowns(){
    $(".dropdown-container.open").each(function(){
        const openDropdown = $(this)
        toggleDropdown(openDropdown, openDropdown.find(".dropdown-menu"), false)
    });
}

function salRevenue() {
  // Get the canvas context
  const canvas = $("#myChart")
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

  // Naira currency formatter with smart number formatting
  const currencyFormatter = (value) => {
      return '₦' + formatNumber(value);
  };

  $.ajax({
    url: '/api/dashboard/salRev',
    type: 'GET',
    contentType: 'application/json',
    success: function(response){
      new Chart(ctx, {
        type: 'line',
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
    
    // Helper functions for formatting
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
    
    function formatNumber(value) {
        if (value >= 1000000) {
            return `${(value / 1000000).toFixed(2)}M`;
        } else if (value >= 1000) {
            return `${(value / 1000).toFixed(2)}K`;
        }
        return new Intl.NumberFormat('en-NG', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
    },
    error: function(xhr, status, error){
      console.log("error:" + error);
    }
  });

  // Initialize the chart   
  
}

function topCategories() {
  // Get the canvas context
  const canvas = $("#myChart2")
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

  // Naira currency formatter with smart number formatting
  const currencyFormatter = (value) => {
      return '₦' + formatNumber(value);
  };

  $.ajax({
    url: '/api/dashboard/tCat',
    type: 'GET',
    contentType: 'application/json',
    success: function(response){
      // Initialize the chart
      new Chart(ctx, {
        type: 'bar',
        data: {
        labels: response.years,
        datasets: [
            {
                label: response.top3Categories[0].label,
                data: response.top3Categories[0].data,
                borderColor: '#8A2BE2',
                backgroundColor: 'rgba(138, 43, 226, 0.2)',
                tension: 0.6,
                fill: true,
                pointRadius: 3,  // Make points larger
                pointHoverRadius: 4,  // Make hover state even larger
                pointBackgroundColor: '#8A2BE2'  // Match point color to line
            },
            {
                label: response.top3Categories[1].label,
                data: response.top3Categories[1].data,
                borderColor: '#87CEFA',
                backgroundColor: 'rgba(135, 206, 250, 0.2)',
                tension: 0.6,
                fill: true,
                pointRadius: 3,  // Make points larger
                pointHoverRadius: 4,  // Make hover state even larger
                pointBackgroundColor: '#87CEFA'  // Match point color to line
            },
            {
                label: response.top3Categories[2].label,
                data: response.top3Categories[2].data,
                borderColor: '#87CEFA',
                backgroundColor: 'rgba(50, 205, 50, 0.2)',
                tension: 0.6,
                fill: true,
                pointRadius: 3,  // Make points larger
                pointHoverRadius: 4,  // Make hover state even larger
                pointBackgroundColor: '#87CEFA'  // Match point color to line
            },
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
                callbacks: {
                    title: function(tooltipItems) {
                        return 'Year: ' + tooltipItems[0].label;
                    },
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat('en-NG', {
                                style: 'currency',
                                currency: 'NGN',
                                minimumFractionDigits: 0,
                                maximumFractionDigits: 0
                            }).format(context.parsed.y);
                        }
                        return label;
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
            y: {
                beginAtZero: true,
                title: {
                    display: false
                },
                ticks: {
                    maxTicksLimit: 6,
                    callback: function(value) {
                        return currencyFormatter(value);
                    }
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
      error: function(xhr, status, error){
        console.log("error:" + error);
      }
  });
  
}

function periodicRevenue(){
  $.ajax({
    url: "/api/dashboard/average",
    type: 'GET',
    contentType: 'application/json',
    success: function(response){
      const daily = response.daily;
      const weekly = response.weekly;
      const monthly = response.monthly;
      const yearly = response.yearly;
      $(".daily h6").html(`₦ ${daily.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`);
      $(".weekly h6").html(`₦ ${weekly.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`);
      $(".monthly h6").html(`₦ ${monthly.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`);
      $(".yearly h6").html(`₦ ${yearly.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`);
    }, 
    error: function(xhr, status, error){
      console.log('error: ' + error);
    }
  });
}