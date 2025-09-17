document.addEventListener('DOMContentLoaded', function() {
    // Lấy dữ liệu từ biến toàn cục
    const { chartDates, chartProdResults, chartPcPlans, chartPersonDiffs, chartTypeLabels, chartTypeProdResults, chartTypePcPlans } = window.chartData;

    // Biểu đồ Sản lượng theo Ngày (Line Chart)
    const dailyCtx = document.getElementById('dailyProductionChart').getContext('2d');
    new Chart(dailyCtx, {
        type: 'line',
        data: {
            labels: chartDates,
            datasets: [
                {
                    label: 'Thực tế Sản xuất',
                    data: chartProdResults,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                },
                {
                    label: 'Kế hoạch PC',
                    data: chartPcPlans,
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Sản lượng Kế hoạch và Thực tế theo Ngày'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số lượng'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Ngày'
                    }
                }
            }
        }
    });

    // Biểu đồ Person Diff (Bar Chart)
    const personCtx = document.getElementById('personDiffChart').getContext('2d');
    new Chart(personCtx, {
        type: 'bar',
        data: {
            labels: chartDates,
            datasets: [
                {
                    label: 'Chênh lệch Nhân sự',
                    data: chartPersonDiffs,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Chênh lệch Nhân sự theo Ngày'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số người'
                    },
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return Number.isInteger(value) ? value : null;
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Ngày'
                    }
                }
            }
        }
    });

    // Biểu đồ Sản lượng theo Loại Sản phẩm (Bar Chart)
    const typeCtx = document.getElementById('productionByTypeChart').getContext('2d');
    new Chart(typeCtx, {
        type: 'bar',
        data: {
            labels: chartTypeLabels,
            datasets: [
                {
                    label: 'Thực tế Sản xuất',
                    data: chartTypeProdResults,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Kế hoạch PC',
                    data: chartTypePcPlans,
                    backgroundColor: 'rgba(255, 206, 86, 0.6)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Sản lượng Kế hoạch và Thực tế theo Loại Sản phẩm'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số lượng'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Loại Sản phẩm'
                    }
                }
            }
        }
    });
});