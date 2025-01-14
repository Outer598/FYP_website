$(document).ready(function(){

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