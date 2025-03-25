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

            // Cargar los servicios asociados a la categoría seleccionada
            load_services_by_category(selectedCategoryId); 
        }
    });

    // Servicio 
    $('#service').change(function() {
        var selectedServiceId = $(this).val();
        var selectedCategoryId = $('#category').val(); 

        hideGraphics();

        if (selectedServiceId) {
            $('#graficaServicio').show();
            graficaEgresosServicio(selectedServiceId); 
        } else if (selectedCategoryId) {
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
        
        console.log("Rango de fecha seleccionado:", startDate, endDate);
        if (startDate && endDate) {
            hideGraphics();
            $('#graficaRangoFechaContainer').show();
            graficaEgresosRangoFecha(startDate, endDate); 
        }
    });    
    
}


// Función para ocultar las gráficas
function hideGraphics() {
    $('#graficaCategoria').hide();
    $('#graficaProveedor').hide();
    $('#graficaRangoFechaContainer').hide();
    $('#graficaServicio').hide();
    
    if (graficaEgresosCategoriaInstance) {
        graficaEgresosCategoriaInstance.destroy();
    }
    if (graficaEgresosProveedorInstance) {
        graficaEgresosProveedorInstance.destroy();
    }
    if (graficaEgresosRangoFechaInstance) {
        graficaEgresosRangoFechaInstance.destroy();
    }
    if (graficaEgresosServicioInstance) {
        graficaEgresosServicioInstance.destroy();
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
                    console.log('Datos de pagos:', payments);
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
                                        console.log('Valor recibido: ', value);  
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
    console.log('Función get_service_dashboard ejecutada');
    $.ajax({
        url: '/get_services_categories/',
        type: 'GET',
        success: function(response) {
            console.log(response);
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
            select.html("<option value='' selected>Seleccione un proveedor</option>"); 
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

$('#provider_services').change(function() {
    limpiarCampos(); // Llama a la función que limpia el formulario
});
// Evento para limpiar los campos cuando se selecciona un proveedor
$('#provider_services').change(function() {
    var selectedProviderId = $(this).val();
    if (selectedProviderId) {
        limpiarCampos(); 
    }
});

// Función para limpiar todos los campos del formulario
function limpiarCampos() {
    $('#category').val(''); 
    $('#service').val(''); 
    $('#start_date_service').val('');
    $('#end_date_service').val('');   
    hideGraphics(); 
}

// Evento para detectar cambios en las fechas de inicio y fin
$('#start_date_service, #end_date_service').change(function() {
    limpiarCamposFechas(); 
});

// Función para limpiar los campos de categoría, servicio y proveedor al seleccionar un rango de fecha
function limpiarCamposFechas() {
    $('#category').val('');
    $('#service').val('');  
    $('#provider_services').val(''); 
    hideGraphics(); 
}

// Evento para detectar cambios en la categoría o el servicio
$('#category, #service').change(function() {
    limpiarCamposCategoriaServicio(); 
});

// Función para limpiar los campos de fecha y proveedor al seleccionar una categoría o servicio
function limpiarCamposCategoriaServicio() {
    $('#start_date_service').val(''); 
    $('#end_date_service').val('');   
    $('#provider_services').val('');  
}

// Variables para almacenar la instancia de la gráfica
let graficaEgresosCategoriaInstance = null;
let graficaEgresosProveedorInstance = null;
let graficaEgresosRangoFechaInstance = null;
let graficaEgresosServicioInstance = null;

// Función para cargar la gráfica  por categoría
function graficaEgresosCategoria(categoryId) {
    $.ajax({
        url: '/get_services_by_category/' + categoryId + '/',  
        type: 'GET',
        success: function(response) {
            if (response.status === 'success') {
                var serviceNames = [];
                var payments = [];

                var categoryName = response.name_category || 'Categoría desconocida';   
                console.log("Nombre de la categoría:", categoryName); 
                $('#categoryNameTitle').text('Gráfica de Servicios de la Categoría: ' + categoryName);

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
                console.log("esto contiene el response", response);

                console.log("proveedor seleccionado:", providerName);

                if (providerName) {
                    // Actualizar el título de la gráfica con el nombre del proveedor
                    $('#proveedor_nombre_actualizado').text('Gráfica de Servicios del proveedor: ' + providerName);
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

// Función para cargar los servicios de una categoría seleccionada
function load_services_by_category(categoryId) {
    console.log("Entramos a la función para seleccionar un servicio por categoría");

    $.ajax({
        url: `/get_service_names_by_category/${categoryId}/`, 
        type: 'GET',
        dataType: "json",
        success: function(response) {
            console.log("Respuesta del servidor:", response); // Verificar la estructura de la respuesta
            
            var select = $('#service');
            select.prop('disabled', false);
            select.html("<option value='' disabled selected>Seleccione un servicio</option>");

            if (response.status === 'success' && Array.isArray(response.service_data)) {
                $.each(response.service_data, function(index, service) {
                    select.append(`<option value="${service.id}">${service.name}</option>`);
                });
                console.log("Opciones agregadas al select:", select.html());
            } else {
                alert('No se encontraron servicios para esta categoría.');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar servicios:', error);
            alert('Hubo un error al cargar los servicios.');
        }
    });
}

function graficaEgresosServicio(serviceId) {
    console.log("Solicitando datos para serviceId:", serviceId);
    
    $.ajax({
        url: `/get_service_expenses/${serviceId}/`, 
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            console.log("Datos recibidos:", response);
            if (response.success) {
                renderGraficaEgresosServicio(response.data);
            } else {
                console.error("Error al obtener datos:", response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error en la solicitud AJAX:", error);
        }
    });
}

function renderGraficaEgresosServicio(data) {
    console.log("Renderizando gráfica con datos:", data);
    
    $('#servicio_nombre_actualizado').text(`Gráfica de egresos del servicio: ${data.service_name}`);

    var ctx = document.getElementById("graficaEgresosServicio");

    if (!ctx) {
        console.error("No se encontró el canvas con id 'graficaEgresosServicio'");
        return;
    }
    
    ctx = ctx.getContext("2d");
    
    // Destruir instancia anterior si existe
    if (graficaEgresosServicioInstance) {
        graficaEgresosServicioInstance.destroy();
    }

    // Crear nueva gráfica
    graficaEgresosServicioInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.months,
            datasets: [{
                label: `Egresos para ${data.service_name}`,
                data: data.egresos, 
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
