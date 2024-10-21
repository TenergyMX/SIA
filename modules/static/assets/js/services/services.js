$(document).ready(function() {
    table_services();
});

function table_services() {
    $('#table_services').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_services/",
            type: 'GET',
            dataSrc: 'data',

        },
        columns: [
            { data: 'id' },
            { data: 'category_service__name_category' },//categoria
            { data: 'name_service' },
            { data: 'description_service' },
            { data: 'provider_service__name' },//proveedor 
            { data: 'start_date_service' },
            { data: 'periodo' },
            { data: 'payment_date' },  // fecha_pago
            { data: 'price_service' },
            { 
                data: 'btn_history',//es para el boton de historial
                render: function(data, type, row) {
                    return data;  
                }
            },
            { 
                data: "btn_action",
                render: function(data, type, row) {
                    return data;  
                }
            }
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10
    });
}


// Función para cargar las categorías en el select
function get_services_categories(selectedCategoryId) {
    $.ajax({
        url: '/get_services_categories/',
        type: 'GET',
        success: function(response) {
            var select = $('#category_service');
            select.html(null); // Limpiar las opciones existentes
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
function get_services_providers(selectedProviderId) {
    $.ajax({
        url: '/get_services_providers/', 
        type: 'GET',
        success: function(response) {
            var select = $('#provider_service');
            select.html("<option value='' disabled selected>Seleccione proveedor</option>");
            $.each(response.data, function(index, provider) {
                var selected = provider.id == selectedProviderId ? 'selected' : '';
                select.append(`<option value="${provider.id}" ${selected}>${provider.name}</option>`);
            });
            select.val(selectedProviderId); // Establecer el valor seleccionado después de agregar las opciones
        },
        error: function(error) {
            console.error('Error al cargar los proveedores:', error);
            alert('Hubo un error al cargar los proveedores.');
        }
    });
}

// Función para mostrar el modal para agregar servicios
function add_services(button) {
    var obj_modal = $("#mdl-crud-services");
    obj_modal.modal("show");

    var row = $(button).closest('tr');
    var data = $('#table_services').DataTable().row(row).data();

    // Cargar las categorias 
    get_services_categories();
    //cargar los proveedores
    get_services_providers();

}

// Función para agregar un servicio
function add_service() {
    var form = $('#form_services')[0];
    var formData = new FormData(form);

    // Validar campos
    var categoryService = formData.get('category_service');
    var nameService = formData.get('name_service').trim();
    var descriptionService = formData.get('description_service').trim();
    var providerService = formData.get('provider_service');
    var startDateService = formData.get('start_date_service');
    var timeQuantityService = formData.get('time_quantity_service');
    var timeUnitService = formData.get('time_unit_service');
    var priceService = formData.get('price_service');

    if (!categoryService || !nameService || !descriptionService || !providerService ||
        !startDateService || !timeQuantityService || !timeUnitService || !priceService) {
        Swal.fire({
            title: "¡Error!",
            text: "Todos los campos son obligatorios.",
            icon: "error",
            showConfirmButton: true
        });
        return;
    }

    $.ajax({
        url: '/add_service/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_services')[0].reset();
                $('#mdl-crud-services').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_services').DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        },
        error: function(error) {
            console.error("Error al guardar el servicio:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                showConfirmButton: false,
                timer: 1500
            });
        },
    });
}


// Evento para el botón de editar
function edit_services(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_services').DataTable().row(row).data();
    // Mostrar el modal
    $('#mdl-crud-services').modal('show');
    
    // Cambiar el título del modal para indicar que es una actualización
    $('#mdl-crud-services .modal-title').text('Editar Servicio');

    // Cargar los datos en el formulario
    $('#form_services [name="id"]').val(data.id);
    $('#form_services [name="name_service"]').val(data.name_service);
    $('#form_services [name="description_service"]').val(data.description_service);
    $('#form_services [name="provider_service"]').val(data.provider_service);
    $('#form_services [name="start_date_service"]').val(data.start_date_service);
    $('#form_services [name="time_quantity_service"]').val(data.time_quantity_service);
    $('#form_services [name="time_unit_service"]').val(data.time_unit_service);
    $('#form_services [name="price_service"]').val(data.price_service);

    // Cargar categorías y seleccionar la categoría actual
    get_services_categories(data.category_service__id);
    // Cargar proveedores y seleccionar la categoría actual
    get_services_providers(data.provider_service__id);

    // Configurar el formulario para editar
    $('#form_services').attr('onsubmit', 'edit_service(); return false');
    
}

//funcion para editar los servicios
function edit_service() {
    var form = $('#form_services')[0];
    var formData = new FormData(form);

    // Validar campos
    var categoryService = formData.get('category_service');
    var nameService = formData.get('name_service').trim();
    var descriptionService = formData.get('description_service').trim();
    var providerService = formData.get('provider_service');
    var startDateService = formData.get('start_date_service');
    var timeQuantityService = formData.get('time_quantity_service');
    var timeUnitService = formData.get('time_unit_service');
    var priceService = formData.get('price_service');

    if (!categoryService || !nameService || !descriptionService || !providerService ||
        !startDateService || !timeQuantityService || !timeUnitService || !priceService) {
        Swal.fire({
            title: "¡Error!",
            text: "Todos los campos son obligatorios.",
            icon: "error",
            showConfirmButton: true
        });
        return;
    }
    
    $.ajax({
        url: '/edit_services/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_services')[0].reset();
                $('#mdl-crud-services').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_services').DataTable().ajax.reload(); 
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500
                });
            }
        },
        error: function(xhr, error) {
            // Extraer el mensaje de error del servidor
            let errorMessage = "Hubo un error al actualizar el servicio.";
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message; // Mensaje del servidor
            }

            console.error("Error al actualizar el servicio:", errorMessage);
            Swal.fire({
                title: "¡Error!",
                text: errorMessage,
                icon: "error",
                timer: 1500
            });
        },
    });
}

// Función para eliminar un servicio
function delete_services(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_services').DataTable().row(row).data();
    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, elimínalo!"
    }).then((result) => {
        if (result.isConfirmed) {
            // Si el usuario confirma la eliminación, hacer la solicitud AJAX
            $.ajax({
                url: '/delete_services/',
                type: 'POST',
                data: {
                    id: data.id
                },
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
                },
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500
                        }).then(() => {
                            // Recargar la tabla después de la eliminación exitosa
                            $('#table_services').DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(error) {
                    console.error("Error al eliminar la categoría:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la categoría.", "error");
                }
            });
        }
    });
}

