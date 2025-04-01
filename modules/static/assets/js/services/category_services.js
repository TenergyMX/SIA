$(document).ready(function() {
    table_category_services();
});

function table_category_services() {
    $('#table_category_services').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_category_service/",
            type: 'GET',
            dataSrc: 'data',
            error: function(xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de las categorias");
            }
        },
        columns: [
            { data: 'id' },
            { data: 'name_category' },
            { data: 'short_name_category' },
            { data: 'description_category' },
            {
                data: "is_active_category",
                render: function (d) {
                    return d
                        ? '<span class="badge bg-outline-success">Activo</span>'
                        : '<span class="badge bg-outline-danger">Inactivo</span>';
                },
                className: "toggleable",
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


// Función para mostrar el formulario en modo agregar
function add_category_services() {
    var obj_modal = $("#mdl-crud-category-services");
    obj_modal.modal("show");

    // Configurar el modal para agregar
    $('#mdl-crud-category-services .modal-title').text('Agregar Categoría de servicios');
    $('#form_add_category_services').attr('onsubmit', 'add_category(); return false');
    
    // Establecer el valor predeterminado de 'is_active' a '1' para nuevos registros
    $('#form_add_category_services [name="is_active"]').val('1');
}

// Función para agregar una categoría
function add_category() {
    var form = $('#form_add_category_services')[0];
    var formData = new FormData(form);
    
    // Validar campos
    var name = formData.get('name').trim();
    var shortName = formData.get('short_name').trim();
    var description = formData.get('description').trim();

    if (!name || !shortName || !description) {
        Swal.fire({
            title: "¡Error!",
            text: "Todos los campos son obligatorios.",
            icon: "error",
            showConfirmButton: true
        });
        return;
    }

    $.ajax({
        url: '/add_category/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_category_services')[0].reset();
                $('#mdl-crud-category-services').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_category_services').DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    showConfirmButton: false,
                });
            }
        },
        error: function(error) {
            console.error("Error al guardar la categoría:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                showConfirmButton: false,
            });
        },
    });
}


// Evento para el botón de editar
function edit_category_services(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_category_services').DataTable().row(row).data();

    // Mostrar el modal
    $('#mdl-crud-category-services').modal('show');

    // Cambiar el título del modal para indicar que es una actualización
    $('#mdl-crud-category-services .modal-title').text('Editar Categoría de Servicios');

    // Cargar los datos en el formulario
    $('#form_add_category_services [name="id"]').val(data.id);
    $('#form_add_category_services [name="name"]').val(data.name_category);
    $('#form_add_category_services [name="short_name"]').val(data.short_name_category);
    $('#form_add_category_services [name="description"]').val(data.description_category);
    $('#form_add_category_services [name="is_active"]').val(data.is_active_category ? '1' : '0');

    // Configurar el formulario para editar
    $('#form_add_category_services').attr('onsubmit', 'edit_category(); return false');
    $('#active-field').removeClass('d-none'); // Mostrar el campo 'is_active'
}


// Función para editar una categoría
function edit_category() {
    var form = $('#form_add_category_services')[0];
    var formData = new FormData(form);
    $.ajax({
        url: '/edit_category_services/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_category_services')[0].reset();
                $('#mdl-crud-category-services').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_category_services').DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function(error) {
            console.error("Error al guardar la categoría:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
            });
        },
    });
}


// Función para eliminar una categoría
function delete_category_services(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_category_services').DataTable().row(row).data();
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
                url: '/delete_category_services/',
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
                            $('#table_category_services').DataTable().ajax.reload();
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

