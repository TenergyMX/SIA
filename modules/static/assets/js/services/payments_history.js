$(document).ready(function(){
    get_categories_payments();
})

// Función para cargar las categorías en el select
function get_categories_payments(selectedCategoryId) {
    $.ajax({
        url: '/get_services_categories_payments/',
        type: 'GET',
        success: function(response) {
            
            var select = $('#category_services');
            select.html(null);
            select.append("<option value='' disabled selected>Seleccione una categoría</option>");
            $.each(response.data, function(index, value) {
                var selected = value.id == selectedCategoryId ? 'selected' : '';
                select.append(
                    `<option value="${value.id}" ${selected}>${value.name_category}</option>`
                );
            });
        },
        error: function(error) {
            console.error('Error al cargar categorías:', error);
            alert('Hubo un error al cargar las categorías.');
        }
    });
}


function load_payment_graph() {

    var categoryId = $('#category_services').val();
    var startMonth = $('#start_month').val();
    var endMonth = $('#end_month').val();

   
    
    // Verificar si los elementos existen
    if ($('#category_services').length === 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El campo de categoría de servicios no está disponible.',
        });
        return;
    }
    if ($('#start_month').length === 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El campo de mes inicial no está disponible.',
        });
        return;
    }
    if ($('#end_month').length === 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El campo de mes final no está disponible.',
        });
        return;
    }


    // Verificar que la fecha de inicio no sea mayor a la fecha final
    if (new Date(startMonth) > new Date(endMonth)) {
        Swal.fire({
            icon: 'error',
            title: 'Fechas inválidas',
            text: 'La fecha de inicio es mayor a la fecha final. Por favor, ingrese una fecha válida.',
        });
        return;
    }

    $.ajax({
        url: '/get_payment_history_grafic/',
        type: 'GET',
        data: {
            category_id: categoryId,
            start_month: startMonth,
            end_month: endMonth
        },
        
        success: function(response) {
            if (response.success) {
                render_graph(response.months, response.total_payments);
            } else {
                alert(response.message);
            }
        },
        error: function(error) {
            console.error('Error al cargar historial de pagos:', error);
        }
    });
}

// Función para renderizar la gráfica
function render_graph(months, totalPayments) {
    var ctx = document.getElementById('graficaPagosCategorias').getContext('2d');

    // Si ya existe una gráfica, destruirla antes de crear una nueva
    if (window.paymentChart) {
        window.paymentChart.destroy();
    }

    // Crear una nueva gráfica
    window.paymentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months, // Etiquetas de los meses
            datasets: [{
                label: 'Total de Pagos ($)',
                data: totalPayments, // Totales por mes
                backgroundColor: '#a5c334', 
                borderColor: '#28a745',
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Mes'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Total Pagado ($)'
                    },
                    beginAtZero: true
                }
            }
        }
    });

    // Mostrar la gráfica
    $('#graficaPagos').show();
}
