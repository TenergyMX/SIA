$(document).ready(function() {
    table_driver_vehicles();

    //Previsualización de la imagen del conductor
    document.getElementById('driver_image').addEventListener('change', function(event) {
        const file = event.target.files[0]; // Obtiene el archivo seleccionado
        const preview = document.getElementById('image_preview'); 

        if (file) {
            const reader = new FileReader(); // Crea un FileReader para leer el archivo

            reader.onload = function(e) {
                preview.src = e.target.result; // Asigna la imagen al src del elemento <img>
                preview.style.display = 'block'; // Muestra la imagen
            };

            reader.readAsDataURL(file); // Lee el archivo como una URL de datos
        } else {
            preview.src = ''; // Limpia la previsualización si no hay archivo
            preview.style.display = 'none'; // Oculta la imagen
        }
    });
});

function table_driver_vehicles() {
    $('#table_driver_vehicles').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_vehicles_driver/",
            type: 'GET',
            dataSrc: 'data',
            error: function(xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de los conductores");
            }
        },
        columns: [
            { title: "ID", data: "id"},
            { title: "Nombre del conductor", data: "driver_name" },
            { title: "N. de telefono", data: "number_phone"},
            { title: "Dirección", data: "address"},
            { 
                title: "Acciones", data: "btn_action",
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

function get_users(selectedUserId) {
    $.ajax({
        url: "/get_users/",
        type: "GET",
        success: function (response) {
            var select = $("#driver_vehicle");
            select.html(
                "<option value='' disabled selected>Seleccione un usuario</option>"
            );
            $.each(response.data, function (index, user) {
                var selected = user.id == selectedUserId ? "selected" : "";
                var fullName = user.username + " " + user.last_name;  // Concatenar nombre y apellido
                select.append(`<option value="${user.id}" ${selected}>${fullName}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);
            alert("Hubo un error al cargar los usuarios.");
        },
    });
}

// Función para mostrar el formulario en modo agregar
function add_driver_vehicle() {
    console.log("estamos en la funcion de agregar conductor");
    var obj_modal = $("#mdl_crud_vehicle_driver");
    obj_modal.modal("show");
    get_users();

    // Configurar el modal para agregar
    $('#mdl_crud_vehicle_driver .modal-title').text('Agregar Conductor');
    $('#form_add_driver').attr('onsubmit', 'add_driver(); return false');

}

// Función para agregar un conductor
function add_driver() {
    var form = $("#form_add_driver")[0]; 
    var formData = new FormData(form); 

    $.ajax({
        url: "/add_driver/", 
        type: "POST", 
        data: formData, 
        processData: false, 
        contentType: false, 
        success: function (response) {
            console.log("esta es la respuestra");
            console.log(response);
            if (response.success) {
                $("#form_add_driver")[0].reset(); 
                $("#mdl_crud_vehicle_driver").modal("hide"); 
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_driver_vehicles").DataTable().ajax.reload(); 
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al guardar el conductor:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar el conductor. Intenta nuevamente.",
                icon: "error",
                timer: 1500,
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}


function edit_drivers(boton) {
    var row = $(boton).closest('tr');
    var register = $('#table_driver_vehicles').DataTable().row(row).data();
    $.ajax({
        url: "/get_drivers/", 
        type: "GET",
        data: { id: register.id }, 
        success: function(response) {
            console.log("esta es la información");
            console.log(response);
            if (response.success) {
                $('#mdl_crud_vehicle_driver').modal('show');
                // Cambiar el título del modal para indicar que es una actualización
                $('#mdl_crud_vehicle_driver .modal-title').text('Editar Información del Conductor');

                // Llenar el formulario con los datos obtenidos
                $('#form_add_driver [name="id"]').val(response.data.id);
                $('#form_add_driver [name="number_phone"]').val(response.data.number_phone);
                $('#form_add_driver [name="address"]').val(response.data.address);
                // Llamar a get_users() y pasar el ID del conductor
                get_users(response.data.driver_id);
                console.log("Nombre del conductor:", response.data.driver_id);
        
                // Configurar el formulario para editar
                $('#form_add_driver').attr('onsubmit', 'edit_driver(); return false');
                console.log("imagen:",response.data.driver_image)
                if (response.data.driver_image) {
                    $('#image_preview').attr('src', response.data.driver_image);
                    $('#image_preview').css('display', 'block');
                } else {
                    $('#image_preview').attr('src', '');
                    $('#image_preview').css('display', 'none');
                }
            } else {
                Swal.fire("Error", "No se encontraron los datos del conductor.", "error");
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al obtener los datos del conductor:", error);
            Swal.fire("Error", "Hubo un problema al cargar la información del conductor.", "error");
        }
    });
}


//funcion para editar los datos 
function edit_driver() {
    var form = $("#form_add_driver")[0];
    var formData = new FormData(form);

    $.ajax({
        url: "/edit_driver/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_driver")[0].reset();
                $("#mdl_crud_vehicle_driver").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_driver_vehicles").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al actualizar el equipo:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al actualizar el equipo.",
                icon: "error",
                timer: 1500,
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}


// Función para eliminar un conductor
function delete_driver(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_driver_vehicles').DataTable().row(row).data();
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
                url: '/delete_driver/',
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
                            $('#table_driver_vehicles').DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(error) {
                    console.error("Error al eliminar el conductor:", error);
                    Swal.fire("Error", "Hubo un error al eliminar el conductor.", "error");
                }
            });
        }
    });
}

