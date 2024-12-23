$(document).ready(function(){
    table_companys();
})

function table_companys() {
    $('#table_companys').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_companys/",
            type: 'GET',
            dataSrc: 'data',

        },
        columns: [
            { title: "Id", data: "id" },
            { title: "Nombre", data: "name" },
            { title: "Direccion", data: "address" },
            { 
                title: "Acciones", 
                data: "btn_action",  
                render: function(data, type, row) {
                    return data;  // Devuelve el HTML para los botones
                }
            }
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10
    });
}

// Función para mostrar el modal para agregar empresas
function add_companys(button) {
    var obj_modal = $("#mdl_crud_company");
    obj_modal.modal("show");

    var row = $(button).closest('tr');
    var data = $('#table_companys').DataTable().row(row).data();

}

//funcion para agregar empresas 
function add_company() {
    var form = $('#form_add_company')[0];
    var formData = new FormData(form);

    $.ajax({
        url: '/add_company/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_company')[0].reset();
                $('#mdl_crud_company').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_companys').DataTable().ajax.reload();
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
function edit_companys(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_companys').DataTable().row(row).data();
    // Mostrar el modal
    $('#mdl_crud_company').modal('show');
    
    // Cambiar el título del modal para indicar que es una actualización
    $('#mdl_crud_company .modal-title').text('Editar Empresa');

    // Cargar los datos en el formulario
    $('#form_add_company [name="id"]').val(data.id);
    $('#form_add_company [name="name"]').val(data.name);
    $('#form_add_company [name="address"]').val(data.address);
    
    // Configurar el formulario para editar
    $('#form_add_company').attr('onsubmit', 'edit_company(); return false');
    
}

//funcion para editar las empresas
function edit_company() {
    var form = $('#form_add_company')[0];
    var formData = new FormData(form);

    
    $.ajax({
        url: '/edit_company/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_company')[0].reset();
                $('#mdl_crud_company').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_companys').DataTable().ajax.reload(); 
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
            let errorMessage = "Hubo un error al actualizar la empresa.";
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message; // Mensaje del servidor
            }

            console.error("Error al actualizar la empresa:", errorMessage);
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
function delete_company(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_companys').DataTable().row(row).data();
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
                url: '/delete_company/',
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
                            $('#table_companys').DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(error) {
                    console.error("Error al eliminar la empresa:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la empresa.", "error");
                }
            });
        }
    });
}
