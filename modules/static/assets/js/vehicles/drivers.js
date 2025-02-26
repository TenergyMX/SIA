$(document).ready(function() {
    // Obtener el ID del conductor desde la URL
    const urlParts = window.location.pathname.split("/");
    const driverId = urlParts[urlParts.length - 2]; 
    if (driverId) {
        loadDriverDetails(driverId);
    }

    table_licence();

    get_table_multa();

    // Llamar a la función de agregar licencia al hacer clic en un botón
    $(document).on('click', '[data-driver-licence="add-item"]', function() {
        var driver_id = $(this).data('driver-id');  
        btn_add_licence(driver_id);  
    });

    // Llamar a la función de agregar licencia al hacer clic en un botón
    $(document).on('click', '[data-driver-multa="add-item"]', function() {
        var driver_id = $(this).data('driver-id');  
        btn_add_multa(driver_id);  
    });

});


// Función para cargar los detalles del conductor
function loadDriverDetails(driverId) {
    $.ajax({
        url: `/drivers/info/${driverId}/details/`,  
        type: "GET",
        dataType: "json",
        success: function (response) {

            // Actualizar la tarjeta con los datos del conductor
            $("[data-key-value='id']").text(response.id);
            $("[data-key-value='name']").text(response.name);
            $("[data-key-value='company__name']").text(response.company__name);
            $("[data-key-value='number_phone']").text(response.number_phone);
            $("[data-key-value='address']").text(response.address);
            $(".card-img img").attr("src", response.image_path); 
        },
        error: function (xhr, status, error) {
            console.error("Error al obtener los detalles del conductor:", error);
        }
    });
}


function table_licence() {

    $('#table_licence').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_licence/",  
            type: 'GET',
            data: {
                id: driver_id                 
            },
            dataSrc: 'data',
            error: function(xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de las licencias");
            }
        },
        columns: [
            { title: "ID", data: "id"},
            { title: "Nombre del conductor", data: "driver_name" },
            { title: "Fecha de inicio", data: "start_date"},
            { title: "Fecha de vencimiento", data: "expiration_date"},
            {
                title: "Licencia de conducir",
                data: function (data) {
                    if (data["license_driver"]) {
                        // Verificar si la URL de la licencia es válida y mostrar el enlace
                        return `<a href="${data["license_driver"]}" target="_blank" class="btn btn-info">
                                <i class="fa-solid fa-download"></i> Descargar licencia
                            </a>`;
                    } else {
                        return "Sin Licencia de conducir";
                    }
                },
                orderable: false,
            },
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


// Función para mostrar el formulario en modo agregar
function btn_add_licence(driver_id) {
    console.log("entramos a la funcion del formulario agregar");
    var obj_modal = $("#mdl-crud-licencia");

    // Mostrar el modal
    obj_modal.modal("show");

    // Configurar el modal para agregar
    $('#mdl-crud-licencia .modal-title').text('Agregar licencia del conductor');
    $('#form_add_licence').attr('onsubmit', 'add_licence(); return false');

    // Cargar los detalles del conductor seleccionado
    loadDriverDetails(driver_id);

    // Función para cargar los detalles del conductor y rellenar el campo de nombre
    function loadDriverDetails(driverId) {
        if (!driverId) {
            console.error("ID del conductor no válido");
            return;
        }
    
        $.ajax({
            url: `/drivers/info/${driverId}/details/`,
            type: "GET",
            dataType: "json",
            success: function(response) {
                $('#name_driver').val(response.name);
                $('#name_driver_id').val(response.id); 
            },
            error: function(xhr, status, error) {
                console.error("Error al obtener los detalles del conductor:", error);
                Swal.fire({
                    title: "¡Error!",
                    text: "No se pudieron cargar los detalles del conductor.",
                    icon: "error"
                });
            }
        });
    }
    
}

// Función para agregar una licencia
function add_licence() {
    var form = $('#form_add_licence')[0];
    var formData = new FormData(form);
    
    $.ajax({
        url: '/add_licence/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_licence')[0].reset();
                $('#mdl-crud-licencia').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_licence').DataTable().ajax.reload();
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
            console.error("Error al guardar la licencia:", error);
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
function btn_edit_licence(boton) {
    var table = $('#table_licence').DataTable();
    var row = $(boton).closest('tr');  
    var data = table.row(row).data();  

    console.log("Datos de la fila seleccionada:", data);

    if (!data) {
        console.error("No se encontraron datos para editar.");
        return;
    }

    // Mostrar el modal
    $('#mdl-crud-licencia').modal('show');
    $('#mdl-crud-licencia .modal-title').text('Editar Licencia');

    // Llenar los campos del formulario
    $('#form_add_licence [name="id"]').val(data.id);
    $('#form_add_licence [name="name_driver"]').val(data.driver_name);
    $('#form_add_licence [name="start_date"]').val(data.start_date);
    $('#form_add_licence [name="expiration_date"]').val(data.expiration_date);

     // Mostrar el archivo si está disponible
     if (data.license_driver) {
        $('#current_license_link').html(`
            <a href="${data.license_driver}" target="_blank" class="btn btn-info">
                <i class="fa-solid fa-download"></i> Descargar licencia
            </a>
        `);
    } else {
        $('#current_license_link').html('');
    }

    // Configurar el formulario para actualizar
    $('#form_add_licence').attr('onsubmit', 'edit_licence(); return false');
}


//funcion para editar los datos de una licencia
function edit_licence() {
    var form = $("#form_add_licence")[0];
    var formData = new FormData(form);
    console.log(form);
    $.ajax({
        url: "/edit_licence/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (licence) {
            console.log("esto contiene el response para editar:", licence);
            if (licence.success) {
                $("#form_add_licence")[0].reset();
                $("#mdl-crud-licencia").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: licence.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_licence").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: licence.message,
                    icon: "error",
                    timer: 1500,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al actualizar la licencia:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al actualizar la licencia.",
                icon: "error",
                timer: 1500,
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}


//funcion para eliminar licencia
function delete_licence(boton) {
    var table = $('#table_licence').DataTable();
    var row = $(boton).closest('tr');  
    var data = table.row(row).data();  

    console.log("Datos de la fila:", data);  
    if (!data || !data.id) {
        console.error("No se pudo obtener el ID del conductor.");
        return;
    }

    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, eliminar"
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: '/delete_licence/',
                type: 'POST',
                data: { id: data.id },
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
                },
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500,  // Cierra la alerta después de 1500 ms
                            showConfirmButton: false
                        });

                        // Esperar 1500 ms antes de recargar la tabla
                        setTimeout(function() {
                            table.ajax.reload();
                        }, 1500);

                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(error) {
                    console.error("Error al eliminar la licencia:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la licencia.", "error");
                }
            });
        }
    });
}


// Función para mostrar el formulario en agregar multa
function btn_add_multa(driver_id) {
    console.log("entramos a la funcion del formulario agregar multas");
    var obj_modal = $("#mdl-crud-multa");

    // Mostrar el modal
    obj_modal.modal("show");

    // Configurar el modal para agregar
    $('#mdl-crud-multa .modal-title').text('Agregar multa del conductor');
    $('#form_add_multa').attr('onsubmit', 'add_multa(); return false');
   
    get_vehicles();
    // Cargar los detalles del conductor seleccionado
    loadDriverDetails(driver_id);

    // Función para cargar los detalles del conductor y rellenar el campo de nombre
    function loadDriverDetails(driverId) {
        if (!driverId) {
            console.error("ID del conductor no válido");
            return;
        }
    
        $.ajax({
            url: `/drivers/info/${driverId}/details/`,
            type: "GET",
            dataType: "json",
            success: function(response) {
                $('#name_driver_multa').val(response.name);
                $('#name_driver_multa_id').val(response.id); 
            },
            error: function(xhr, status, error) {
                console.error("Error al obtener los detalles del conductor:", error);
                Swal.fire({
                    title: "¡Error!",
                    text: "No se pudieron cargar los detalles del conductor.",
                    icon: "error"
                });
            }
        });
    }
    
}

// Función para cargar los vehículos
function get_vehicles(selectedVehicleId) {
    $.ajax({
        url: "/get_vehicles/",
        type: "GET",
        success: function (response) {
            var select = $("#vehicle");
            select.html(
                "<option value='' disabled selected>Seleccione un vehículo</option>"
            );
            $.each(response.data, function (index, vehicle) {
                var selected = vehicle.id == selectedVehicleId ? "selected" : "";
                select.append(
                    `<option value="${vehicle.id}" ${selected}>${vehicle.name}</option>`
                );
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los vehículos:", error);
            alert("Hubo un error al cargar los vehículos.");
        },
    });
}


// Función para agregar multa
function add_multa() {
    var form = $('#form_add_multa')[0];
    var formData = new FormData(form);
    
    $.ajax({
        url: '/add_multa/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
        console.log("esta es la información que contiene response:", response);
            if (response.success) {
                $('#form_add_multa')[0].reset();
                $('#mdl-crud-multa').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_multa').DataTable().ajax.reload();
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
            console.error("Error al guardar la multa:", error);
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


function get_table_multa() {

    $('#table_multa').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_multas/",  
            type: 'GET',
            data: {
                id: driver_id                 
            },
            dataSrc: 'data',
            error: function(xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de las multas");
            }
        },
        columns: [
            { title: "ID", data: "id"},
            { title: "Nombre del conductor", data: "driver_name" },
            { 
                title: "Vehiculo", data: "vehicle",
                render: function(data, type, row) {
                    return data.modelo;  
                }
            },
            { title: "Costo", data: "cost"},
            { title: "Notas", data: "notes"},
            { title: "Razón", data: "reason"},
            { title: "Fecha", data: "date"},            
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


// Evento para el botón de editar
function btn_edit_multa(boton) {
    var table = $('#table_multa').DataTable();
    var row = $(boton).closest('tr');  
    var data = table.row(row).data();  

    console.log("Datos de la fila seleccionada:", data);

    if (!data) {
        console.error("No se encontraron datos para editar.");
        return;
    }

    var vehicleId = data.vehicle.id;
    console.log("ID del vehículo:", vehicleId);
    var modelo = data.vehicle.modelo;
    console.log("este es el modelo de l vehiculo seleccionado:", modelo);


    // Mostrar el modal
    $('#mdl-crud-multa').modal('show');
    $('#mdl-crud-multa .modal-title').text('Editar Multa');

    // Llenar los campos del formulario
    $('#form_add_multa [name="id"]').val(data.id);
    $('#form_add_multa [name="name_driver_multa"]').val(data.driver_name);

    if ($('#vehicle option[value="' + vehicleId + '"]').length === 0) {
        $('#vehicle').append(`<option value="${vehicleId}">${modelo}</option>`);
    }
    $('#vehicle').val(vehicleId).trigger('change');
    
    $('#form_add_multa [name="cost"]').val(data.cost);
    $('#form_add_multa [name="notes"]').val(data.notes);
    $('#form_add_multa [name="reason"]').val(data.reason);
    $('#form_add_multa [name="date"]').val(data.date);

    // Configurar el formulario para actualizar
    $('#form_add_multa').attr('onsubmit', 'edit_multa(); return false');
}


//funcion para editar los datos de multa
function edit_multa() {
    var form = $("#form_add_multa")[0];
    var formData = new FormData(form);
    console.log(form);
    $.ajax({
        url: "/edit_multa/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (multa) {
            console.log("esto contiene el response para editar:", multa);
            if (multa.success) {
                $("#form_add_multa")[0].reset();
                $("#mdl-crud-multa").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: multa.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_multa").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: multa.message,
                    icon: "error",
                    timer: 1500,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al actualizar la multa:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al actualizar la multa.",
                icon: "error",
                timer: 1500,
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

//funcion para eliminar multa
function delete_multa(boton) {
    var table = $('#table_multa').DataTable();
    var row = $(boton).closest('tr');  
    var data = table.row(row).data();  

    console.log("Datos de la fila:", data);  
    if (!data || !data.id) {
        console.error("No se pudo obtener el ID de la multa.");
        return;
    }

    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, eliminar"
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: '/delete_multa/',
                type: 'POST',
                data: { id: data.id },
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
                },
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500,  // Cierra la alerta después de 1500 ms
                            showConfirmButton: false
                        });

                        // Esperar 1500 ms antes de recargar la tabla
                        setTimeout(function() {
                            table.ajax.reload();
                        }, 1500);

                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(error) {
                    console.error("Error al eliminar la multa:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la multa.", "error");
                }
            });
        }
    });
}

