$(document).ready(function() {
    load_table_equi();
});

function load_table_equi() {
    $('#table_equipments_tools').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: '/get_equipments_tools/',
            type: 'GET',
            dataSrc: 'data',
            error: function(xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de los equipos.");
            }
        },
        columns: [
            { data: 'id' },
            { data: 'equipment_category__name' },
            { data: 'equipment_name' },
            { data: 'equipment_type' },
            { data: 'equipment_brand' },
            { data: 'equipment_description' },
            { data: 'cost' },
            { data: 'amount' },
            { data: 'equipment_area__name' },
            { data: 'equipment_responsible__username' },
            { data: 'equipment_location__location_name' },
            {
                title: "Ficha técnica",
                data: function (d) {
                    if (d["equipment_technical_sheet"]) {
                        return `<a href="/${d["equipment_technical_sheet"]}" class="btn btn-sm btn-outline-primary" target="_blank">Ficha técnica</a>`;
                    } else {
                        return "Sin Ficha técnica";
                    }
                },
                orderable: false,
            },
            {
                data: 'btn_action',  
                orderable: false
            }
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10
    });
}

//funcion para cargar el documento del equipo 
function openDocument(url) {
    if (url) {
        window.open(url, '_blank');
    }
}

// Función para cargar las categorías en el select
function get_equipment_categories(selectedCategoryId) {
    $.ajax({
        url: '/get_equipment_categories/',
        type: 'GET',
        success: function(response) {
            var select = $('#categoria_id');
            select.html(null); // Limpiar las opciones existentes
            select.append("<option value='' disabled selected>Seleccione una categoría</option>");
            $.each(response.data, function(index, value) {
                var selected = value.id == selectedCategoryId ? 'selected' : '';
                select.append(
                    `<option value="${value.id}" ${selected}>${value.name}</option>`
                );
            });
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar categorías:', error);
            alert('Hubo un error al cargar las categorías.');
        }
    });
}

// Función para cargar las areas en el select
function get_equipment_areas(selectedAreaId) {
    $.ajax({
        url: '/get_equipment_areas/',
        type: 'GET',
        success: function(response) {
            var select = $('#equipment_area');
            select.html(null); // Limpiar las opciones existentes
            select.append("<option value='' disabled selected>Seleccione una de las areas existentes</option>");
            $.each(response.data, function(index, value) {
                var selected = value.id == selectedAreaId ? 'selected' : '';
                select.append(
                    `<option value="${value.id}" ${selected}>${value.name}</option>`
                );
            });
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar las areas existentes:', error);
            alert('Hubo un error al cargar las areas existentes.');
        }
    });
}


//Función para cargar los nombres de los usuarios que ya han sido registrados para agregar un equipo o herramienta
function get_responsible_users(selectedUserId) {
    $.ajax({
        url: '/get_responsible_users/', 
        type: 'GET',
        success: function(response) {
            var select = $('#responsible_equipment');
            select.html("<option value='' disabled selected>Seleccione responsable temporal</option>");
            $.each(response.data, function(index, user) {
                var selected = user.id == selectedUserId ? 'selected' : '';
                select.append(`<option value="${user.id}" ${selected}>${user.username}</option>`);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar los usuarios:', error);
            alert('Hubo un error al cargar los usuarios.');
        }
    });
}

// Función para cargar las ubicaciones que ya han sido registrados
function get_locations(selectedLocationId) {
    $.ajax({
        url: '/get_locations/', 
        type: 'GET',
        success: function(response) {
            const select = $('#equipment_location');
            select.html("<option value='' disabled selected>Seleccione una de las ubicaciones existentes</option>");
            $.each(response.data, function(index, location) {
                const selected = location.id == selectedLocationId ? 'selected' : '';
                select.append(`<option value="${location.id}" ${selected}>${location.location_name}</option>`);
            });
            // opción para agregar una nueva ubicación
            select.append('<option value="add_new">Agregar otra ubicación no existente</option>');
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar las ubicaciones:', error);
            alert('Hubo un error al cargar las ubicaciones. Inténtelo de nuevo más tarde.');
        }
    });
}

//funcion para mostrar las empresas en el select al momento de cargar el modal para agregar una nueva responsiva
function get_company(selectedCompanyId) {
    $.ajax({
        url: '/get_company/',
        type: 'GET',
        success: function(response) {
            var select = $('#location_company');
            select.html(null); // Limpiar las opciones existentes
            select.append("<option value='' disabled selected>Seleccione una de las empresas existentes</option>");
            $.each(response.data, function(index, value) {
                var selected = value.id == selectedCompanyId ? 'selected' : '';
                select.append(
                    `<option value="${value.id}" ${selected}>${value.name}</option>`
                );
            });
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar las empresas existentes:', error);
            alert('Hubo un error al cargar las empresas existentes.');
        }
    });
}


//fucion para mostrar el modal de una nueva ubicacion 
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('equipment_location').addEventListener('change', function() {
        if (this.value === 'add_new') {
            var locationModal = new bootstrap.Modal(document.getElementById('mdl-crud-location'));
            locationModal.show();
            this.value = "";
            get_company();
        }
    });
});


// Función para agregar una nueva ubicación
function add_location() {
    var form = $('#form_location')[0]; // Obtén el formulario
    var formData = new FormData(form); // Crea un FormData del formulario

    $.ajax({
        url: '/add_location/',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            console.log(response); // Verifica la respuesta
            if (response.success) {
                $('#form_location')[0].reset(); // Resetea el formulario
                $('#mdl-crud-location').modal('hide'); // Cierra el modal

                // Actualiza el select de ubicaciones
                var select = $('#equipment_location'); 
                var newOption = new Option(response.new_location.name, response.new_location.id);
                select.append(newOption); 

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500
                });
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al guardar la ubicación:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar la ubicación. Intenta nuevamente.",
                icon: "error",
                timer: 1500
            });
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    });
}

// Función para mostrar el formulario
function add_equipment() {
    var obj_modal = $("#mdl-crud-equipments-tools");
    obj_modal.modal("show");
    get_equipment_categories(); // Llama a la función para cargar categorías al abrir el modal
    get_equipment_areas();//llama a ala funcion para cargar las areas existentes
    get_responsible_users();// Cargar los responsables
    get_locations();
}

// Función para agregar un equipo o herramienta
function add_equipment_tool() {
    var form = $('#form_add_equipments_tools')[0]; // Obtén el formulario
    var formData = new FormData(form); // Crea un FormData del formulario

    $.ajax({
        url: '/add_equipment_tools/', // URL del endpoint
        type: 'POST', // Método POST
        data: formData, // Datos del formulario
        processData: false, // No procesar los datos
        contentType: false, // No establecer el tipo de contenido
        success: function(response) {
            if (response.success) {
                // Si la respuesta es exitosa
                $('#form_add_equipments_tools')[0].reset(); // Resetea el formulario
                $('#mdl-crud-equipments-tools').modal('hide'); // Cierra el modal
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_equipments_tools').DataTable().ajax.reload(); // Recarga la tabla
            } else {
                // Si la respuesta no es exitosa
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500
                });
            }
        },
        error: function(xhr, status, error) {
            // Manejo de errores AJAX
            console.error("Error al guardar el equipo:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar el equipo. Intenta nuevamente.",
                icon: "error",
                timer: 1500
            });
        },
        beforeSend: function(xhr) {
            // Configura el token CSRF
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    });
}

function edit_button(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_equipments_tools').DataTable().row(row).data();

    // Mostrar el modal de edición
    $('#mdl-crud-equipments-tools').modal('show');
    $('#mdl-crud-equipments-tools .modal-title').text('Editar equipo');

    // Rellenar el formulario con los datos del equipo
    $('#form_add_equipments_tools [name="id"]').val(data.id);
    $('#form_add_equipments_tools [name="equipment_name"]').val(data.equipment_name);
    $('#form_add_equipments_tools [name="equipment_type"]').val(data.equipment_type);
    $('#form_add_equipments_tools [name="equipment_brand"]').val(data.equipment_brand);
    $('#form_add_equipments_tools [name="equipment_description"]').val(data.equipment_description);
    $('#form_add_equipments_tools [name="cost"]').val(data.cost);
    $('#form_add_equipments_tools [name="amount"]').val(data.amount);
    $('#form_add_equipments_tools [name="equipment_area"]').val(data.equipment_area);
    $('#form_add_equipments_tools [name="equipment_responsible"]').val(data.equipment_responsible);

    // Cargar categorías y seleccionar la categoría actual
    get_equipment_categories(data.equipment_category__id);

    // Cargar categorías y seleccionar la categoría actual
    get_equipment_areas(data.equipment_area__id);

    get_responsible_users(data.equipment_responsible__id)

    get_locations(data.equipment_location__id)
    // Cambiar la acción del formulario a la de edición
    $('#form_add_equipments_tools').attr('onsubmit', 'edit_equipments_tools(); return false');
}

//funcion para editar los equipos o herramientas
function edit_equipments_tools() {
    var form = $('#form_add_equipments_tools')[0];
    var formData = new FormData(form);
    
    $.ajax({
        url: '/edit_equipments_tools/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_equipments_tools')[0].reset();
                $('#mdl-crud-equipments-tools').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_equipments_tools').DataTable().ajax.reload(); 
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500
                });
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al actualizar el equipo:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al actualizar el equipo.",
                icon: "error",
                timer: 1500
            });
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    });
}



//funcion para eliminar los datos
function delete_equipment_tool(boton){
    var row = $(boton).closest('tr');
    var data = $('#table_equipments_tools').DataTable().row(row).data();

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
                url: '/delete_equipment_tool/', 
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
                            $('#table_equipments_tools').DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(xhr, status, error) {wh
                    console.error("Error al eliminar el equipo:", error);
                    Swal.fire("Error", "Hubo un error al eliminar el equipo.", "error");
                }
            });
        }
    });
}

//Función para cargar los nombres de los usuarios para agregar una nueva responsiva
function get_responsible_user(selectedUserId) {
    $.ajax({
        url: '/get_responsible_user/', 
        type: 'GET',
        success: function(response) {
            var select = $('#equipment_responsible');
            select.html(""); // Limpiar las opciones existentes
            
            // Agregar opciones
            if (response.data.length > 0) {
                $.each(response.data, function(index, user) {
                    var selected = user.id == selectedUserId ? 'selected' : '';
                    select.append(`<option value="${user.id}" ${selected}>${user.username}</option>`);
                });
                
                // Si no se pasó un ID seleccionado, seleccionar el primer usuario
                if (!selectedUserId) {
                    select.val(response.data[0].id); // Selecciona el primer usuario
                }
            }
        },
        error: function(xhr, status, error) {
            console.error('Error al cargar los usuarios:', error);
            alert('Hubo un error al cargar los usuarios.');
        }
    });
}


// Función para mostrar el modal de responsiva
function modal_responsiva(button) {
    var obj_modal = $("#mdl-crud-responsiva");
    obj_modal.modal("show");

    var row = $(button).closest('tr');
    var data = $('#table_equipments_tools').DataTable().row(row).data();
    $('#form_responsiva [name="equipment_name"]').val(data.equipment_name);

    // Cargar los responsables
    get_responsible_user();
    // Asignar eventos para calcular la diferencia de fechas
    $('#fecha_inicio, #fecha_entrega').on('change', calcularDiferencia);
}

// Función para calcular la diferencia de días entre la fecha de inicio y la fecha de entrega
function calcularDiferencia() {
    var fechaentrega = $('#fecha_entrega').val();

    if (fechaentrega) {
        $.ajax({
            url: '/get_server_date/', 
            type: 'GET',
            success: function(response) {
                var server_date = response.server_date; // Fecha actual del servidor en formato YYYY-MM-DD

                // Convertir la fecha del servidor a un objeto Date en UTC
                var fecha_inicio = new Date(server_date + 'T00:00:00Z');
                var fecha_entrega_date = new Date(fechaentrega);

                // Convertir la fecha de entrega a la misma zona horaria que la fecha del servidor
                fecha_entrega_date.setMinutes(fecha_entrega_date.getMinutes() - fecha_entrega_date.getTimezoneOffset());

                // Verificar si las fechas son válidas
                if (isNaN(fecha_inicio.getTime()) || isNaN(fecha_entrega_date.getTime())) {
                    Swal.fire({
                        title: "Fecha no válida",
                        text: "Una o ambas fechas son inválidas. Por favor, ingrese fechas válidas.",
                        icon: "error",
                        timer: 1000
                    });
                    $('#form_responsiva [name="times_requested_responsiva"]').val(''); // Limpiar el campo de tiempo solicitado
                    return;
                }

                // Verificar si la fecha de entrega es mayor a la fecha actual del servidor
                if (fecha_entrega_date <= fecha_inicio) {
                    Swal.fire({
                        title: "Fecha no válida",
                        text: "Esta fecha no es válida, ya pasó. Ingresa una fecha diferente.",
                        icon: "error",
                        timer: 1000
                    });
                    $('#fecha_entrega').val(''); // Limpiar el campo de fecha de entrega
                    $('#form_responsiva [name="times_requested_responsiva"]').val(''); // Limpiar el campo de tiempo solicitado
                } else {
                    // Calcular la diferencia en milisegundos
                    var diferencia_ms = fecha_entrega_date - fecha_inicio;
                    
                    // Convertir la diferencia a días
                    var total_dias = Math.ceil(diferencia_ms / (1000 * 60 * 60 * 24));
                    
                    // Mostrar la diferencia en el campo de tiempo solicitado
                    $('#form_responsiva [name="times_requested_responsiva"]').val(total_dias);
                }
            },
            error: function(xhr, status, error) {
                console.error('Error al obtener la fecha del servidor:', error);
                Swal.fire({
                    title: "Error",
                    text: "Hubo un problema al obtener la fecha del servidor.",
                    icon: "error",
                    timer: 1500
                });
            }
        });
    }
}



// Configuración del canvas
let canvas = document.getElementById('canvas-signature');
let ctx = canvas.getContext('2d');
let drawing = false;
let lastX = 0;
let lastY = 0;
let undoStack = [];

// Configura el contexto
ctx.strokeStyle = 'black';
ctx.lineWidth = 2;
ctx.lineCap = 'round';

// Eventos para dibujar en el canvas
canvas.addEventListener('mousedown', function(e) {
    drawing = true;
    lastX = e.offsetX;
    lastY = e.offsetY;
});

canvas.addEventListener('mousemove', function(e) {
    if (drawing) {
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        lastX = e.offsetX;
        lastY = e.offsetY;
    }
});

canvas.addEventListener('mouseup', function() {
    drawing = false;
    ctx.beginPath();
    undoStack.push(canvas.toDataURL());
});

// Limpiar el canvas
document.getElementById('canvas-signature-btn-clear').addEventListener('click', function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    undoStack = [];
});


document.getElementById('canvas-signature-btn-undo').addEventListener('click', function() {
    if (undoStack.length > 0) {
        const imgData = undoStack.pop();
        const img = new Image();
        img.src = imgData;
        img.onload = function() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        };
    }
});


// Enviar el formulario
document.getElementById('form_responsiva').addEventListener('submit', function(event) {
    event.preventDefault();

    // Obtener datos de la firma del canvas
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixelData = imgData.data;

    // Comprobar si hay al menos un pixel que no sea blanco
    let hasDrawing = false;
    for (let i = 0; i < pixelData.length; i += 4) {
        // Solo revisar el componente alfa (A)
        if (pixelData[i + 3] !== 0) { // Si alfa no es 0, hay un trazo
            hasDrawing = true;
            break;
        }
    }

    if (!hasDrawing) {
        Swal.fire({
            title: "Error",
            text: "Es necesario que el responsable firme, el campo está vacío.",
            icon: "warning",
            timer: 1500
        });
        return; // Detener el envío del formulario
    }

    // Crear FormData para enviar
    const form = $('#form_responsiva')[0]; // Obtener el formulario
    const formData = new FormData(form);

    // Convertir la firma a Blob
    const dataURL = canvas.toDataURL();
    const byteString = atob(dataURL.split(',')[1]);
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
    const ab = new Uint8Array(byteString.length);

    for (let i = 0; i < byteString.length; i++) {
        ab[i] = byteString.charCodeAt(i);
    }

    const blob = new Blob([ab], { type: mimeString });
    formData.append('signature', blob, 'signature.png');

    // Llamar a la función para agregar la responsiva
    add_responsiva(formData);
});



// Función para agregar una responsiva
function add_responsiva(formData) {
    $.ajax({
        url: '/add_responsiva/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_responsiva')[0].reset();
                ctx.clearRect(0, 0, canvas.width, canvas.height); // Limpiar el canvas
                $('#mdl-crud-responsiva').modal('hide'); 
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1000
                });
                $('#table_equipments_tools').DataTable().ajax.reload(); 
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1000
                });
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al guardar la Responsiva:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                timer: 1500
            });
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    });
}

// Función para mostrar el modal de historial
function modal_history(button) {
    var row = $(button).closest('tr');
    var data = $('#table_equipments_tools').DataTable().row(row).data();
    var equipmentId = data.id;

    // Mostrar el modal de historial
    $('#mdl-crud-history').modal('show');

    // Obtener el historial del equipo
    $.ajax({
        url: '/get-equipment-history/', 
        type: 'POST',
        data: {
            equipment_id: equipmentId
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        },
        success: function(response) {
            if (response.success) {
                var tbody = $('#mdl-crud-history .table-history tbody');
                tbody.empty(); // Limpiar la tabla

                console.log(response.data); 

                response.data.forEach(item => {
                    var row = `<tr>
                        <td>${item.id}</td>
                        <td>${item.equipment_name__equipment_name}</td>
                        <td>${item.responsible_equipment__username}</td>
                        <td>${item.date_receipt}</td>
                        <td>${item.status_equipment}</td>
                    </tr>`;
                    tbody.append(row);
                });

                if (response.data.length === 0) {
                    tbody.append(`<tr><td colspan="5">No hay historial disponible</td></tr>`);
                }
            } else {
                Swal.fire({
                    title: "Error",
                    text: response.message,
                    icon: "error",
                    timer: 1500
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Error al obtener el historial:', error);
            Swal.fire({
                title: "Error",
                text: "Hubo un problema al obtener el historial.",
                icon: "error",
                timer: 1500
            });
        }
    });
}




