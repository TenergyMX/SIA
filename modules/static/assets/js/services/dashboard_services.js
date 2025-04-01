$(document).ready(function() {
    contadoresDashboard();//contadores
    graficaEgresos();//grafica principal
    get_service_dashboard();//servicios
    get_services_provider();//proveedores
    graficas_filtros();//mostrar las graficas
});

//funcion para mostrar las graficas por filtros 
function graficas_filtros() {

    // categoría
    $('#category').change(function() {
        var selectedCategoryId = $(this).val();
        if (selectedCategoryId) {
            hideGraphics();
            $('#graficaCategoria').show();
            graficaEgresosCategoria(selectedCategoryId);  
        }
    });

    // proveedor
    $('#provider_services').change(function() {
        var selectedProviderId = $(this).val();
        if (selectedProviderId) {
            hideGraphics();
            $('#graficaProveedor').show();
            graficaEgresosProveedor(selectedProviderId);  
        }
    });

    // Rango de fecha
    $('#start_date_service, #end_date_service').change(function() {
        var startDate = $('#start_date_service').val();
        var endDate = $('#end_date_service').val();
        
        if (startDate && endDate) {
            hideGraphics();
            $('#graficaRangoFechaContainer').show();
            graficaEgresosRangoFecha(startDate, endDate);  // Actualiza el parámetro para enviar el rango completo
        }
    });    
    
}


// Función para ocultar las gráficas
function hideGraphics() {
    $('#graficaCategoria').hide();
    $('#graficaProveedor').hide();
    $('#graficaRangoFechaContainer').hide();
    
    if (graficaEgresosCategoriaInstance) {
        graficaEgresosCategoriaInstance.destroy();
    }
    if (graficaEgresosProveedorInstance) {
        graficaEgresosProveedorInstance.destroy();
    }
    if (graficaEgresosRangoFechaInstance) {
        graficaEgresosRangoFechaInstance.destroy();
    }
}

// Función para cargar los datos de los contadores en el dashboard
function contadoresDashboard() {
    $.ajax({
        url: '/get_dashboard_data/',  
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                // Actualizar el total de servicios
                $('#servicesTotal').text(response.data.total_services);

                // Actualizar el total de egresos
                var totalEgresos = parseFloat(response.data.total_egresos);
                if (!isNaN(totalEgresos)) {
                    $('#egresosTotal').text(totalEgresos.toFixed(2)); 
                } else {
                    $('#egresosTotal').text('0.00'); 
                }  

                // Actualizar el total de pagos no pagados
                $('#paymentsTotal').text(response.data.total_non_paid_payments);
            } else {
                console.error("Error al obtener los datos del dashboard:", response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error en la llamada AJAX:", error);
        }
    });
}


// Función para cargar la gráfica 
function graficaEgresos() {
    $.ajax({
        url: '/get_dashboard_grafica/',  
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                var categories = [];
                var payments = [];

                response.data.forEach(function(item) {
                    categories.push(item.category);  
                    payments.push(Number(item.total_payment)); 
                });

                

                if (typeof graficaEgresos !== 'undefined') {
                    graficaEgresos.destroy();
                }

                var canvas = document.getElementById('graficaEgresos');
                var container = canvas.parentElement;

                var containerWidth = container.offsetWidth;
                var containerHeight = container.offsetHeight;

                canvas.width = containerWidth * 0.6;  
                canvas.height = containerHeight * 0.6;

                
                canvas.style.marginLeft = (containerWidth - canvas.width) / 2 + 'px';
                canvas.style.marginTop = (containerHeight - canvas.height) / 2 + 'px';

                // Crear la gráfica 
                var ctx = canvas.getContext('2d');
                var graficaEgresos = new Chart(ctx, {
                    type: 'pie',  
                    data: {
                        labels: categories,  
                        datasets: [{
                            label: 'Total de Egresos por Categoría',
                            data: payments,  
                            backgroundColor: ['#a5c334', '#2CB2F5', '#E24747', '#EED675', '#F2B252'],  
                            borderColor: '#fff',
                            borderWidth: 2,
                            fill: true, 
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(tooltipItem) {
                                        var value = tooltipItem.raw;
                                        if (typeof value === 'number' && !isNaN(value)) {
                                            return '$' + value.toFixed(2);
                                        } else {
                                            return '$0.00';  
                                        } 
                                    }
                                }
                            }                            
                        }
                    }
                });

            } else {
                console.error("Error al obtener los datos para la gráfica:", response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error:", error);
        }
    });
}


// Función para cargar las categorías en el select
function get_service_dashboard(selectedCategoryId) {
    $.ajax({
        url: '/get_services_categories/',
        type: 'GET',
        success: function(response) {
            
            var select = $('#category');
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


//Función para cargar los nombres de los proveedores han sido registrados
function get_services_provider(selectedProviderId) {
    $.ajax({
        url: '/get_services_providers/', 
        type: 'GET',
        success: function(response) {
            var select = $('#provider_services');
            select.html("<option value='' disabled selected>Seleccione proveedor</option>");
            $.each(response.data, function(index, provider) {
                var selected = provider.id == selectedProviderId ? 'selected' : '';
                select.append(`<option value="${provider.id}" ${selected}>${provider.name}</option>`);
            });
            select.val(selectedProviderId); 
        },
        error: function(error) {
            console.error('Error al cargar los proveedores:', error);
            alert('Hubo un error al cargar los proveedores.');
        }
    });
}

// Variables para almacenar la instancia de la gráfica
let graficaEgresosCategoriaInstance = null;
let graficaEgresosProveedorInstance = null;
let graficaEgresosRangoFechaInstance = null;

// Función para cargar la gráfica  por categoría
function graficaEgresosCategoria(categoryId) {
    $.ajax({
        url: '/get_services_by_category/' + categoryId + '/',  
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                var serviceNames = [];
                var payments = [];
                var categoryName = response.data && response.data.name_category ? response.data.name_category : 'Categoría desconocida';

                

                $('#categoryNameTitle').text('Gráfica de Servicios por Categoría: ' + categoryName);

                response.data.forEach(function(item) {
                    serviceNames.push(item.service_name);
                    payments.push(Number(item.total_payment));
                });


                // Crear la gráfica 
                var ctx = document.getElementById('graficaEgresosCategoria').getContext('2d');
                if (typeof graficaEgresosCategoriaInstance !== 'undefined'&& graficaEgresosCategoriaInstance !== null) {
                    graficaEgresosCategoriaInstance.destroy(); 
                }
                graficaEgresosCategoriaInstance = new Chart(ctx, {
                    type: 'bar',  
                    data: {
                        labels: serviceNames,  
                        datasets: [{
                            label: 'Egresos de Servicios por Categoría',
                            data: payments, 
                            backgroundColor: '#a5c334', 
                            borderColor: '#28a745',
                            borderWidth: 2,
                            fill: true, 
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(tooltipItem) {
                                        return '$' + tooltipItem.raw.toFixed(2);  
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                console.error("Error al obtener los datos para la gráfica:", response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error:", error);
        }
    });
}


// Función para cargar la gráfica por proveedor
function graficaEgresosProveedor(providerId) {
    $.ajax({
        url: '/get_services_by_provider/' + providerId + '/', 
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                var serviceNames = [];
                var payments = [];
                

                // Obtener el nombre del proveedor
                var providerName = response.provider_name;


                if (providerName) {
                    // Actualizar el título de la gráfica con el nombre del proveedor
                    $('#proveedor').text('Gráfica de Servicios del proveedor: ' + providerName);
                } else {
                    console.error("No se encontró el nombre del proveedor.");
                }

                
                response.data.forEach(function(item) {
                    serviceNames.push(item.service_name);
                    payments.push(Number(item.total_payment));
                });
                
                
                var ctx = document.getElementById('graficaEgresosProveedor').getContext('2d');
                if (typeof graficaEgresosProveedorInstance !== 'undefined' && graficaEgresosProveedorInstance !== null) {
                    graficaEgresosProveedorInstance.destroy(); 
                }
                graficaEgresosProveedorInstance = new Chart(ctx, {
                    type: 'bar',  
                    data: {
                        labels: serviceNames, 
                        datasets: [{
                            label: 'Egresos por Servicio',
                            data: payments,  
                            backgroundColor: '#2CB2F5',  
                            borderColor: '#0990D3',
                            borderWidth: 2,
                            fill: true, 
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(tooltipItem) {
                                        return '$' + tooltipItem.raw.toFixed(2); 
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                console.error("Error al obtener los datos para la gráfica:", response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error:", error);
        }
    });
}


// Función para cargar la gráfica por rango de fecha
function graficaEgresosRangoFecha(startDate, endDate) {
    if (!startDate || !endDate) {
        console.error("Por favor, selecciona un rango de fechas.");
        return;
    }

    $.ajax({
        url: '/get_services_by_date_range/',  
        type: 'GET',
        data: {
            start_date: startDate,
            end_date: endDate
        },
        success: function(response) {
            if (response.status === 'success') {
                var serviceNames = [];
                var payments = [];

                response.data.forEach(function(item) {
                    serviceNames.push(item.service_name); 
                    payments.push(Number(item.total_payment)); 
                });

                var ctx = document.getElementById('graficaRangoFechaCanvas').getContext('2d');
                graficaEgresosRangoFechaInstance = new Chart(ctx, {
                    type: 'bar',  
                    data: {
                        labels: serviceNames, 
                        datasets: [{
                            label: 'Egresos por Servicio',
                            data: payments, 
                            backgroundColor: '#E24747',  
                            borderColor: '#E32121',  
                            borderWidth: 2, 
                            fill: true, 
                        }]
                    },
                    options: {
                        responsive: true, 
                        plugins: {
                            legend: {
                                position: 'top', 
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(tooltipItem) {
                                        return '$' + tooltipItem.raw.toFixed(2); 
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                console.error("Error al obtener los datos para la gráfica:", response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error en la solicitud AJAX:", error);
        }
    });
}



