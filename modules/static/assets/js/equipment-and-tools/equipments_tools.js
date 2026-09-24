$(document).ready(function () {
    load_table_equi();
});

function load_table_equi() {
    $("#table_equipments_tools").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_equipments_tools/",
            type: "GET",
            dataSrc: "data",

            error: function (xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de los equipos.");
            },
        },
        columns: [
            { title: "Id", data: "id" },
            { title: "Categoría", data: "equipment_category__name" },
            { title: "Nombre", data: "equipment_name" },
            { title: "Tipo", data: "equipment_type" },
            { title: "Marca", data: "equipment_brand" },
            { title: "Descripción", data: "equipment_description" },
            { title: "Costo", data: "cost" },
            { title: "Cantidad", data: "amount" },
            { title: "Área", data: "equipment_area__name" },
            { title: "Responsable", data: "equipment_responsible__username" },
            { title: "Ubicación", data: "equipment_location__location_name" },
            { title: "Comentarios", data: "comments" },

            {
                title: "Fotografía",
                data: "btn_equipment_image",
                orderable: false,
                searchable: false,
                className: "text-center",
            },
            {
                title: "Ficha técnica",
                data: "btn_equipment_technical_sheet",
                orderable: false,
                className: "text-center",
            },
            {
                title: "Factura",
                data: "btn_document_factura_equipment",
                orderable: false,
                className: "text-center",
            },
            {
                title: "Desglose de equipo",
                data: "btn_equipment_breakdown",
                orderable: false,
                searchable: false,
                className: "text-center",
            },

            {
                title: "Acciones",
                data: "btn_action",
                orderable: false,
                defaultContent: "",
            },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10,
    });
}

// Función para cargar las categorías en el select
function get_equipment_categories(selectedCategoryId) {
    $.ajax({
        url: "/get_equipment_categories/",
        type: "GET",
        success: function (response) {
            var select = $("#categoria_id");
            select.html(null); // Limpiar las opciones existentes
            select.append("<option value='' disabled selected>Seleccione una categoría</option>");
            $.each(response.data, function (index, value) {
                var selected = value.id == selectedCategoryId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar categorías:", error);
            alert("Hubo un error al cargar las categorías.");
        },
    });
}

// Función para cargar las areas en el select
function get_equipment_areas(selectedAreaId) {
    $.ajax({
        url: "/get_equipment_areas/",
        type: "GET",
        success: function (response) {
            var select = $("#equipment_area");
            select.html(null); // Limpiar las opciones existentes
            select.append(
                "<option value='' disabled selected>Seleccione una de las areas existentes</option>"
            );
            $.each(response.data, function (index, value) {
                var selected = value.id == selectedAreaId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las areas existentes:", error);
            alert("Hubo un error al cargar las areas existentes.");
        },
    });
}

//Función para cargar los nombres de los usuarios que ya han sido registrados para agregar un equipo o herramienta
function get_responsible_users(selectedUserId) {
    $.ajax({
        url: "/get_responsible_users/",
        type: "GET",
        success: function (response) {
            var select = $("#responsible_equipment");
            select.html(
                "<option value='' disabled selected>Seleccione responsable temporal</option>"
            );
            $.each(response.data, function (index, user) {
                var selected = user.id == selectedUserId ? "selected" : "";
                select.append(`<option value="${user.id}" ${selected}>${user.username}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);
            alert("Hubo un error al cargar los usuarios.");
        },
    });
}

// Función para cargar las ubicaciones que ya han sido registrados
function get_locations(selectedLocationId) {
    $.ajax({
        url: "/get_locations/",
        type: "GET",
        success: function (response) {
            const select = $("#equipment_location");
            select.html(
                "<option value='' disabled selected>Seleccione una de las ubicaciones existentes</option>"
            );
            $.each(response.data, function (index, location) {
                const selected = location.id == selectedLocationId ? "selected" : "";
                select.append(
                    `<option value="${location.id}" ${selected}>${location.location_name}</option>`
                );
            });
            // opción para agregar una nueva ubicación
            select.append('<option value="add_new">Agregar otra ubicación no existente</option>');
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las ubicaciones:", error);
            alert("Hubo un error al cargar las ubicaciones. Inténtelo de nuevo más tarde.");
        },
    });
}

//funcion para mostrar las empresas en el select al momento de cargar el modal para agregar una nueva responsiva
function get_company(selectedCompanyId) {
    $.ajax({
        url: "/get_company/",
        type: "GET",
        success: function (response) {
            var select = $("#location_company");
            select.html(null); // Limpiar las opciones existentes
            select.append(
                "<option value='' disabled selected>Seleccione una de las empresas existentes</option>"
            );
            $.each(response.data, function (index, value) {
                var selected = value.id == selectedCompanyId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las empresas existentes:", error);
            alert("Hubo un error al cargar las empresas existentes.");
        },
    });
}

//fucion para mostrar el modal de una nueva ubicacion
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("equipment_location").addEventListener("change", function () {
        if (this.value === "add_new") {
            var locationModal = new bootstrap.Modal(document.getElementById("mdl-crud-location"));
            locationModal.show();
            this.value = "";
            get_company();
        }
    });
});

// Función para agregar una nueva ubicación
function add_location() {
    var form = $("#form_location")[0]; // Obtén el formulario
    var formData = new FormData(form); // Crea un FormData del formulario

    $.ajax({
        url: "/add_location/",
        type: "POST",
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            // Verifica la respuesta
            if (response.success) {
                $("#form_location")[0].reset(); // Resetea el formulario
                $("#mdl-crud-location").modal("hide"); // Cierra el modal

                // Actualiza el select de ubicaciones
                var select = $("#equipment_location");
                var newOption = new Option(response.new_location.name, response.new_location.id);
                select.append(newOption);

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al guardar la ubicación:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar la ubicación. Intenta nuevamente.",
                icon: "error",
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// Función para mostrar el formulario
function add_equipment() {
    var obj_modal = $("#mdl-crud-equipments-tools");
    obj_modal.modal("show");
    get_equipment_categories();
    get_equipment_areas();
    get_responsible_users();
    get_locations();
}

// Función para agregar un equipo o herramienta
function add_equipment_tool() {
    var form = $("#form_add_equipments_tools")[0];
    var formData = new FormData(form);

    $.ajax({
        url: "/add_equipment_tools/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.status == "success") {
                clear_equipment_tool_form();
                $("#mdl-crud-equipments-tools").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_equipments_tools").DataTable().ajax.reload();
            } else {
                // Si la respuesta no es exitosa
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            // Manejo de errores AJAX
            console.error("Error al guardar el equipo:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar el equipo. Intenta nuevamente.",
                icon: "error",
            });
        },
        beforeSend: function (xhr) {
            // Configura el token CSRF
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

function edit_button(boton) {
    var row = $(boton).closest("tr");
    var data = $("#table_equipments_tools").DataTable().row(row).data();

    console.log("esto contiene el data", data);
    // Mostrar el modal de edición
    $("#mdl-crud-equipments-tools").modal("show");
    $("#mdl-crud-equipments-tools .modal-title").text("Editar equipo");

    // Rellenar el formulario con los datos del equipo
    $("#equipment_tool_id").val(data.id);
    $('#form_add_equipments_tools [name="equipment_name"]').val(data.equipment_name);
    $('#form_add_equipments_tools [name="equipment_type"]').val(data.equipment_type);
    $('#form_add_equipments_tools [name="equipment_brand"]').val(data.equipment_brand);
    $('#form_add_equipments_tools [name="equipment_description"]').val(data.equipment_description);
    $('#form_add_equipments_tools [name="cost"]').val(data.cost);
    $('#form_add_equipments_tools [name="amount"]').val(data.amount);
    $('#form_add_equipments_tools [name="equipment_area"]').val(data.equipment_area);
    $('#form_add_equipments_tools [name="equipment_responsible"]').val(data.equipment_responsible);
    $('#form_add_equipments_tools [name="comments"]').val(data.comments);
    $('#form_add_equipments_tools [name="has_serial_number"]').prop(
        "checked",
        data.has_serial_number
    );
    // Cargar categorías y seleccionar la categoría actual
    get_equipment_categories(data.equipment_category__id);

    // Cargar categorías y seleccionar la categoría actual
    get_equipment_areas(data.equipment_area__id);

    get_responsible_users(data.equipment_responsible__id);

    get_locations(data.equipment_location__id);
    // Cambiar la acción del formulario a la de edición
    $("#form_add_equipments_tools").attr("onsubmit", "edit_equipments_tools(); return false");
}

//funcion para editar los equipos o herramientas
function edit_equipments_tools() {
    var form = $("#form_add_equipments_tools")[0];
    var formData = new FormData(form);

    $.ajax({
        url: "/edit_equipments_tools/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_equipments_tools")[0].reset();
                $("#mdl-crud-equipments-tools").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_equipments_tools").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al actualizar el equipo:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al actualizar el equipo.",
                icon: "error",
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// Función para eliminar/desactivar los datos
function delete_equipment_tool(boton) {
    var row = $(boton).closest("tr");
    var data = $("#table_equipments_tools").DataTable().row(row).data();

    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, elimínalo!",
        cancelButtonText: "Cancelar",
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/delete_equipment_tool/",
                type: "POST",

                data: {
                    id: data.id,
                },

                beforeSend: function (xhr) {
                    xhr.setRequestHeader(
                        "X-CSRFToken",
                        $('input[name="csrfmiddlewaretoken"]').val()
                    );
                },

                success: function (response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500,
                            showConfirmButton: false,
                        }).then(() => {
                            $("#table_equipments_tools").DataTable().ajax.reload(null, false);
                        });
                    } else {
                        Swal.fire({
                            title: "No se puede eliminar",
                            text: response.message,
                            icon: "warning",
                            confirmButtonText: "Aceptar",
                        });
                    }
                },

                error: function (xhr, status, error) {
                    console.error("Error al eliminar el equipo:", xhr.responseJSON);

                    let mensaje = "Hubo un error al eliminar el equipo.";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        mensaje = xhr.responseJSON.message;
                    }
                    Swal.fire({
                        title: "No se puede eliminar",
                        text: mensaje,
                        icon: "warning",
                        confirmButtonText: "Aceptar",
                    });
                },
            });
        }
    });
}

// Función para limpiar completamente el formulario de equipos y herramientas
function clear_equipment_tool_form() {
    const form = $("#form_add_equipments_tools")[0];
    form.reset();
    $("#equipment_tool_id").val("");

    $('#form_add_equipments_tools [name="equipment_category"]').val("");
    $('#form_add_equipments_tools [name="equipment_area"]').val("");
    $('#form_add_equipments_tools [name="equipment_responsible"]').val("");
    $('#form_add_equipments_tools [name="equipment_location"]').val("");

    $('#form_add_equipments_tools [name="equipment_category"]').val(null).trigger("change");
    $('#form_add_equipments_tools [name="equipment_area"]').val(null).trigger("change");
    $('#form_add_equipments_tools [name="equipment_responsible"]').val(null).trigger("change");
    $('#form_add_equipments_tools [name="equipment_location"]').val(null).trigger("change");

    $('#form_add_equipments_tools [name="has_serial_number"]').prop("checked", false);
    $("#mdl-crud-equipments-tools .modal-title").text("Agregar equipo");
    $("#form_add_equipments_tools").attr("onsubmit", "add_equipment_tool(); return false");
}

//Función para cargar los nombres de los usuarios para agregar una nueva responsiva
function get_responsible_user(selectedUserId) {
    $.ajax({
        url: "/get_responsible_user/",
        type: "GET",
        success: function (response) {
            var select = $("#equipment_responsible");
            select.html(""); // Limpiar las opciones existentes

            // Agregar opciones
            if (response.data.length > 0) {
                $.each(response.data, function (index, user) {
                    var selected = user.id == selectedUserId ? "selected" : "";
                    select.append(
                        `<option value="${user.id}" ${selected}>${user.username}</option>`
                    );
                });

                // Si no se pasó un ID seleccionado, seleccionar el primer usuario
                if (!selectedUserId) {
                    select.val(response.data[0].id); // Selecciona el primer usuario
                }
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);
            alert("Hubo un error al cargar los usuarios.");
        },
    });
}

// Función para mostrar el modal de responsiva
function modal_responsiva(button) {
    var obj_modal = $("#mdl-crud-responsiva");
    obj_modal.modal("show");

    var row = $(button).closest("tr");
    var data = $("#table_equipments_tools").DataTable().row(row).data();
    $('#form_responsiva [name="equipment_name"]').val(data.equipment_name);

    // Cargar los responsables
    get_responsible_user();

    // Mostrar u ocultar el campo de fecha de inicio
    var tipo_user = "{{ tipo_user }}";

    //  calcular la diferencia de fechas
    $("#fecha_inicio, #fecha_entrega").on("change", function () {
        calcularDiferencia();
        verificarFechaEntrega();
    });

    // Deshabilitar fechas pasadas si no hay fecha de inicio
    verificarFechaEntrega();
}

// Función para calcular la diferencia de días entre la fecha de inicio y la fecha de entrega
function calcularDiferencia() {
    var fecha_entrega = $("#fecha_entrega").val();
    var fecha_inicio = $("#fecha_inicio").val();

    if (fecha_entrega) {
        $.ajax({
            url: "/get_server_date/",
            type: "GET",
            success: function (response) {
                var server_date = new Date(response.server_date);

                var fecha_inicio_date = fecha_inicio ? new Date(fecha_inicio) : server_date;

                // Validar fechas
                if (
                    isNaN(fecha_inicio_date.getTime()) ||
                    isNaN(new Date(fecha_entrega).getTime())
                ) {
                    Swal.fire({
                        title: "Fecha no válida",
                        text: "Una o ambas fechas son inválidas. Por favor, ingrese fechas válidas.",
                        icon: "error",
                    });
                    $('#form_responsiva [name="times_requested_responsiva"]').val("");
                    return;
                }

                // Comprobar si la fecha de entrega es mayor a la de inicio
                var fecha_entrega_date = new Date(fecha_entrega);
                if (fecha_entrega_date <= fecha_inicio_date) {
                    Swal.fire({
                        title: "Fecha no válida",
                        text: "La fecha de entrega debe ser mayor a la fecha de inicio.",
                        icon: "error",
                    });
                    return;
                }

                var diferencia_ms = fecha_entrega_date - fecha_inicio_date;
                var total_dias = Math.ceil(diferencia_ms / (1000 * 60 * 60 * 24)) + 1;
                $('#form_responsiva [name="times_requested_responsiva"]').val(total_dias);
            },
            error: function (xhr, status, error) {
                // Manejar errores de obtención de fecha del servidor
                console.error("Error al obtener la fecha del servidor:", error);
                Swal.fire({
                    title: "Error",
                    text: "Hubo un problema al obtener la fecha del servidor.",
                    icon: "error",
                });
            },
        });
    }
}

// Función para verificar y establecer restricciones en la fecha de entrega
function verificarFechaEntrega() {
    $.ajax({
        url: "/get_server_date/",
        type: "GET",
        success: function (response) {
            var server_date = response.server_date;
            var today = new Date(server_date);
            today.setHours(0, 0, 0, 0);

            var fecha_inicio = $("#fecha_inicio").val();
            if (!fecha_inicio) {
                $("#fecha_entrega").attr("min", server_date);
            } else {
                $("#fecha_entrega").removeAttr("min");
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al obtener la fecha del servidor:", error);
        },
    });
}

// Configuración del canvas
let canvas = document.getElementById("canvas-signature");
let ctx = canvas.getContext("2d");
let drawing = false;
let lastX = 0;
let lastY = 0;
let undoStack = [];

// Configura el contexto
ctx.strokeStyle = "black";
ctx.lineWidth = 2;
ctx.lineCap = "round";

// Eventos para dibujar en el canvas
canvas.addEventListener("mousedown", function (e) {
    drawing = true;
    lastX = e.offsetX;
    lastY = e.offsetY;
});

canvas.addEventListener("mousemove", function (e) {
    if (drawing) {
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
        lastX = e.offsetX;
        lastY = e.offsetY;
    }
});

canvas.addEventListener("mouseup", function () {
    drawing = false;
    ctx.beginPath();
    undoStack.push(canvas.toDataURL());
});

// Limpiar el canvas
document.getElementById("canvas-signature-btn-clear").addEventListener("click", function () {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    undoStack = [];
});

document.getElementById("canvas-signature-btn-undo").addEventListener("click", function () {
    if (undoStack.length > 0) {
        const imgData = undoStack.pop();
        const img = new Image();
        img.src = imgData;
        img.onload = function () {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        };
    }
});

// Enviar el formulario
document.getElementById("form_responsiva").addEventListener("submit", function (event) {
    event.preventDefault();

    // Obtener datos de la firma del canvas
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixelData = imgData.data;

    // Comprobar si hay al menos un pixel que no sea blanco
    let hasDrawing = false;
    for (let i = 0; i < pixelData.length; i += 4) {
        // Solo revisar el componente alfa (A)
        if (pixelData[i + 3] !== 0) {
            // Si alfa no es 0, hay un trazo
            hasDrawing = true;
            break;
        }
    }

    // Crear FormData para enviar
    const form = $("#form_responsiva")[0]; // Obtener el formulario
    const formData = new FormData(form);

    // Convertir la firma a Blob
    const dataURL = canvas.toDataURL();
    const byteString = atob(dataURL.split(",")[1]);
    const mimeString = dataURL.split(",")[0].split(":")[1].split(";")[0];
    const ab = new Uint8Array(byteString.length);

    for (let i = 0; i < byteString.length; i++) {
        ab[i] = byteString.charCodeAt(i);
    }

    const blob = new Blob([ab], { type: mimeString });
    formData.append("signature", blob, "signature.png");

    // Llamar a la función para agregar la responsiva
    add_responsiva(formData);
});

// Función para agregar una responsiva
function add_responsiva(formData) {
    Swal.fire({
        title: "Guardando responsiva...",
        text: "La plataforma está procesando la información. Por favor, espera.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/add_responsiva/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_responsiva")[0].reset();
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                $("#mdl-crud-responsiva").modal("hide");

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1000,
                });

                $("#table_equipments_tools").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al guardar la Responsiva:", error);
            Swal.fire({
                title: "¡Error!",
                text: xhr.responseJSON.message || "Error inesperado.",
                icon: "error",
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// Función para mostrar el modal de historial
function modal_history(button) {
    var row = $(button).closest("tr");
    var data = $("#table_equipments_tools").DataTable().row(row).data();
    var equipmentId = data.id;

    // Mostrar el modal de historial
    $("#mdl-crud-history").modal("show");

    // Obtener el historial del equipo
    $.ajax({
        url: "/get-equipment-history/",
        type: "POST",
        data: {
            equipment_id: equipmentId,
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
        success: function (response) {
            if (response.success) {
                var tbody = $("#mdl-crud-history .table-history tbody");
                tbody.empty();

                response.data.forEach((item) => {
                    //fecha
                    var dateReceipt = item.date_receipt;
                    if (!dateReceipt) {
                        dateReceipt = "Sin fecha de actualización";
                    }

                    //estado
                    var status = item.status_equipment;
                    if (status === "Aceptado") {
                        status = "En uso";
                    }

                    //pdf
                    var pdfButton =
                        '<button class="btn btn-primary-light btn-sm btn-generate-responsiva-pdf" ' +
                        'data-responsiva-id="' +
                        item.id +
                        '">' +
                        '<i class="fa-solid fa-file-pdf"></i> Generar PDF' +
                        "</button>";

                    var row = `<tr>
                        <td>${item.id}</td>
                        <td>${item.equipment_name__equipment_name}</td>
                        <td>${item.responsible_equipment__username}</td>
                        <td>${dateReceipt}</td>
                        <td>${status}</td>
                        <td>${pdfButton}</td>
                    </tr>`;
                    tbody.append(row);
                });

                if (response.data.length === 0) {
                    tbody.append(`<tr><td colspan="6">No hay historial disponible</td></tr>`);
                }
            } else {
                Swal.fire({
                    title: "Error",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al obtener el historial:", error);
            Swal.fire({
                title: "Error",
                text: "Hubo un problema al obtener el historial.",
                icon: "error",
            });
        },
    });
}
//generar pdf
$(document).on("click", ".btn-generate-responsiva-pdf", function () {
    const responsivaId = $(this).data("responsiva-id");

    $.ajax({
        url: "/generate_pdf/" + responsivaId + "/",
        type: "GET",
        xhrFields: {
            responseType: "blob",
        },

        success: function (blob) {
            const url = window.URL.createObjectURL(blob);

            Swal.fire({
                title: "¡Éxito!",
                text: "PDF generado exitosamente",
                icon: "success",
                timer: 1500,
            }).then(() => {
                window.open(url, "_blank");
            });
        },

        error: function (xhr, error, thrown) {
            console.error("Error al generar PDF:", thrown);

            Swal.fire({
                title: "¡Error!",
                text: "No se pudo generar el PDF.",
                icon: "error",
            });
        },
    });
});

// clic en la lista de información
$(document).on("click", "button[data-equipments-tools='view-identifiers']", function () {
    const itemId = $(this).data("id");
    verDesgloseEquipmentTool(itemId);
});

// CARGAR / RECARGAR DESGLOSE DE EQUIPO O HERRAMIENTA
function verDesgloseEquipmentTool(itemId) {
    window.currentEquipmentToolId = itemId;

    $.ajax({
        url: "/get_equipment_tools_details/",
        method: "GET",
        data: {
            id: itemId,
        },
        success: function (response) {
            if (!response.success) {
                alert("No se pudieron obtener los detalles.");
                return;
            }

            const container = $("#equipment-tools-detail-container");
            const hasSerialNumber = response.has_serial_number === true;

            container.empty();

            const table = $(`
                <table
                    class="table table-bordered table-hover w-100"
                    id="equipment_tool-detail-table">

                    <thead>

                        <tr>
                            <th>Id</th>
                            <th>Identificador</th>
                            <th>Estado</th>
                            <th>Responsable</th>
                            <th>Fotografía</th>
                            <th>Fecha de asignación</th>
                            ${hasSerialNumber ? "<th>Número de serie</th>" : ""}
                            <th>Ubicación</th>
                            <th>Acciones</th>
                        </tr>

                    </thead>

                    <tbody></tbody>

                </table>
            `);

            container.append(table);

            const tbody = table.find("tbody");

            response.data.forEach(function (item) {
                const responsableHTML = item.tiene_responsable
                    ? `
                            <span>
                                ${item.responsable}
                            </span>

                            <button
                                type="button"
                                class="btn btn-sm btn-warning ms-2 assign-responsible"
                                data-id="${item.id}"
                                data-responsable-id="${item.responsable_id}"
                                title="Editar responsable">

                                <i class="fas fa-user-edit"></i>

                            </button>
                        `
                    : `
                            <button
                                type="button"
                                class="btn btn-sm btn-primary assign-responsible"
                                data-id="${item.id}"
                                title="Asignar responsable">

                                <i class="fas fa-user-plus"></i>

                            </button>
                        `;

                const fechaHTML = item.fecha_asignacion
                    ? item.fecha_asignacion
                    : `
                            <span class="text-muted">
                                Sin fecha de asignación
                            </span>
                        `;

                const fotografiaHTML = item.fotografia
                    ? `
                        <div class="d-flex align-items-center gap-2">
                            ${item.fotografia}

                            <button
                                type="button"
                                class="btn btn-sm btn-outline-primary add-photo"
                                data-id="${item.id}"
                                title="Editar fotografía">

                                <i class="fas fa-camera"></i>
                            </button>
                        </div>
                    `
                    : `
                        <button
                            type="button"
                            class="btn btn-sm btn-outline-primary add-photo"
                            data-id="${item.id}"
                            title="Agregar fotografía">

                            <i class="fa-solid fa-upload"></i>
                        </button>
                    `;

                let serialHTML = "";

                if (hasSerialNumber) {
                    if (item.serial_number && item.serial_number.trim() !== "") {
                        serialHTML = `
                            <span>
                                ${item.serial_number}
                            </span>
                        
                        `;

                        if (item.is_active) {
                            serialHTML += `
                                <button
                                    type="button"
                                    class="btn btn-sm btn-outline-primary edit-serial-number"
                                    data-id="${item.id}"
                                    data-serial-number="${item.serial_number}"
                                    title="Editar número de serie">

                                    <i class="fas fa-edit"></i>

                                </button>
                            `;
                        }
                    } else {
                        if (item.is_active) {
                            serialHTML = `
                                <button
                                    type="button"
                                    class="btn btn-sm btn-outline-primary add-serial-number"
                                    data-id="${item.id}"
                                    data-serial-number=""
                                    title="Agregar número de serie">

                                    <i class="fas fa-edit"></i>

                                </button>
                            `;
                        } else {
                            // Deshabilitado y sin número de serie
                            serialHTML = `
                                <span class="text-muted">
                                    Sin número de serie
                                </span>
                            `;
                        }
                    }
                }

                const serialTD = hasSerialNumber ? `<td>${serialHTML}</td>` : "";

                const locationHTML =
                    item.equipment_location && item.equipment_location !== "Sin ubicación"
                        ? item.equipment_location
                        : `
                            <span class="text-muted">
                                Sin ubicación
                            </span>
                        `;

                let actionHTML = "";

                if (item.is_active) {
                    // ACTIVO → DESHABILITAR
                    actionHTML = `
                        <button
                            type="button"
                            class="btn btn-icon btn-sm btn-danger-light toggle-equipment-detail"
                            data-id="${item.id}"
                            data-action="disable"
                            title="Deshabilitar">

                            <i class="fa-solid fa-ban"></i>

                        </button>
                    `;
                } else {
                    // DESHABILITADO → HABILITAR
                    actionHTML = `
                        <button
                            type="button"
                            class="btn btn-icon btn-sm btn-success-light toggle-equipment-detail"
                            data-id="${item.id}"
                            data-action="enable"
                            title="Habilitar">

                            <i class="fa-solid fa-check"></i>
                        </button>
                    `;
                }

                tbody.append(`

                    <tr>

                        <td>
                            ${item.id}
                        </td>
                        <td>
                            ${item.identificador}
                        </td>
                        <td>
                            ${item.state}
                        </td>
                        <td>
                            ${responsableHTML}
                        </td>
                        <td>
                            ${fotografiaHTML}
                        </td>
                        <td>
                            ${fechaHTML}
                        </td>
                        ${serialTD}
                        <td>
                            ${locationHTML}
                        </td>
                        <td class="text-center">
                            ${actionHTML}
                        </td>
                    </tr>
                `);
            });

            table.DataTable({
                destroy: true,
                responsive: true,
                autoWidth: false,
                pageLength: 10,

                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
            });

            $("#info_equipment_tool").modal("show");
        },

        error: function (xhr, status, error) {
            alert("Ocurrió un error al obtener los detalles.");
        },
    });
}

// Agregar / editar número de serie
$(document).on("click", ".add-serial-number, .edit-serial-number, .add-photo", function () {
    const button = $(this);
    const modal = $("#mdl-crud-numero-serie");
    const id = $(this).data("id");
    const inputId = $("#detalle_id");
    const inputFile = $("#individual_photo_equipments_tools");
    const inputSerial = $("#serial_number");

    // limpiar
    inputSerial.val("");
    inputId.val("");
    inputFile.val("");
    // Cargar ID
    inputId.val(id);

    if (button.hasClass("add-photo")) {
        $("#serial_number").removeAttr("required");
        $(".placeholder-serial-number").addClass("d-none");
        $("#modalAsignarNumeroSerie").html("Asignar Fotografía");
        $("#individual_photo_equipments_tools").attr("required", true);
        $(".placeholder-photo").removeClass("d-none");
        modal.modal("show");
        return;
    } else {
        $("#individual_photo_equipments_tools").removeAttr("required");
        $(".placeholder-photo").addClass("d-none");
        $("#modalAsignarNumeroSerie").html("Asignar Número de serie");
        $("#serial_number").attr("required", true);
        $(".placeholder-serial-number").removeClass("d-none");
    }

    const numeroSerie = $(this).attr("data-serial-number") || "";

    const titulo = $("#modalAsignarNumeroSerie");

    // EDITAR
    if (numeroSerie.trim() !== "") {
        inputSerial.val(numeroSerie);
        titulo.text("Editar Número de Serie");
    }
    // AGREGAR
    else {
        inputSerial.val("");
        titulo.text("Asignar Número de Serie");
    }
    // Mostrar modal
    modal.modal("show");
});

// agregar numero de serie
$("#mdl-crud-numero-serie form").on("submit", function (e) {
    e.preventDefault();

    const form = this;
    const obj_modal = $("#mdl-crud-numero-serie");
    const inputSerial = $("#serial_number");
    const inputId = $("#detalle_id");
    const datos = new FormData(form);

    $.ajax({
        type: "POST",
        url: "/save_equipment_tool_serial_number/",
        data: datos,
        processData: false,
        contentType: false,

        success: function (response) {
            if (!response.success && response.error) {
                Swal.fire("Error", response.error["message"], "error");
                return;
            }

            if (!response.success && response.warning) {
                Swal.fire("Advertencia", response.warning["message"], "warning");
                return;
            }

            if (!response.success) {
                Swal.fire("Error", response.message || "Ocurrió un error inesperado", "error");
                return;
            }

            inputSerial.val("");
            inputId.val("");

            form.reset();

            // Cerrar modal
            const modalElement = document.getElementById("mdl-crud-numero-serie");
            const modalInstance = bootstrap.Modal.getInstance(modalElement);

            if (modalInstance) {
                modalInstance.hide();
            }

            if (window.currentEquipmentToolId) {
                verDesgloseEquipmentTool(window.currentEquipmentToolId);
            }

            Swal.fire({
                title: "Éxito",
                text: response.message,
                icon: "success",
            });
        },

        error: function (xhr, status, error) {
            console.error("Error del servidor:", error);
            console.error(xhr.responseText);

            Swal.fire(
                "Error del servidor",
                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                "error"
            );
        },
    });
});

// HABILITAR O DESHABILITAR UN EQUIPO O HERRAMIENTA (MOSTRAR EL FORMULARIO)
$(document).on("click", ".toggle-equipment-detail", function () {
    const id = $(this).data("id");
    const action = $(this).data("action");

    // DESHABILITAR
    if (action === "disable") {
        $.ajax({
            url: "/modal_equipment_tool_detail/",
            type: "GET",

            data: {
                id: id,
            },
            success: function (response) {
                if (!response.success) {
                    Swal.fire(
                        "Error",
                        response.message || "No se pudo obtener la información.",
                        "error"
                    );
                    return;
                }

                // CARGAR DATOS DEL EQUIPO EN EL MODAL
                $("#disable_detail_id").val(response.data.id);
                $("#disable_identifier").val(response.data.identifier);
                $("#disable_reason").val("");
                $("#disable_description").val("");
                $("#disable_equipment_image").val("");

                // Mostrar modal
                $("#mdl-crud-enable").modal("show");
            },

            error: function (xhr) {
                console.error("Error:", xhr.responseText);

                Swal.fire("Error", "No se pudo obtener la información del equipo.", "error");
            },
        });

        return;
    }

    // HABILITAR
    if (action === "enable") {
        Swal.fire({
            title: "¿Habilitar equipo o herramienta?",
            text: "El equipo volverá a estar disponible.",
            icon: "question",
            showCancelButton: true,
            confirmButtonText: "Sí, habilitar",
            cancelButtonText: "Cancelar",
            reverseButtons: true,
        }).then(function (result) {
            if (!result.isConfirmed) {
                return;
            }
            cambiarEstadoEquipmentTool(id, "enable");
        });
    }
});

// LLAMAR A LA FUNCION PARA DESHABILITAR
$(document).on("submit", "#formdisable", function (e) {
    e.preventDefault();

    disable_equipment_tool_detail();
});

// DAR DE BAJA EQUIPO O HERRAMIENTA
function disable_equipment_tool_detail() {
    var form = $("#formdisable")[0];
    var formData = new FormData(form);

    formData.set("action", "disable");

    $.ajax({
        url: "/disable_equipment_tool_detail/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,

        success: function (response) {
            if (response.success) {
                const detailId = $("#disable_detail_id").val();

                // RESPONSIVA
                if (window.disableDetailFromResponsiva) {
                    if (!window.detailsConfiguredForDisable) {
                        window.detailsConfiguredForDisable = [];
                    }

                    // Guardar el detalle configurado
                    if (!window.detailsConfiguredForDisable.includes(String(detailId))) {
                        window.detailsConfiguredForDisable.push(String(detailId));
                    }

                    // Limpiar formulario de baja
                    form.reset();

                    $("#disable_detail_id").val("");
                    $("#disable_identifier").val("");
                    $("#disable_reason").val("");
                    $("#disable_description").val("");

                    $("#evidence1").val("");
                    $("#evidence2").val("");

                    $("#image_preview1").attr("src", "").hide();
                    $("#image_preview2").attr("src", "").hide();

                    $("#mdl-crud-enable").modal("hide");

                    setTimeout(function () {
                        const configuredIds = window.detailsConfiguredForDisable || [];

                        const statusValue = $("#status_equipment").val();

                        const statusName =
                            {
                                0: "Regresado",
                                1: "Incompleto",
                                2: "Dañado",
                                3: "No devuelto",
                            }[statusValue] || statusValue;

                        // INCOMPLETO
                        if (statusName === "Incompleto") {
                            const pending = window.pendingIncompleteResponsiva;

                            if (!pending) {
                                console.error("No existe información pendiente de Incompleto.");
                                return;
                            }

                            const requiredAmount = parseInt(pending.amountToDeactivate, 10);

                            // aún faltan equipos por configurar
                            if (configuredIds.length < requiredAmount) {
                                $("#mdl-crud-status-responsiva").modal("show");

                                renderConfiguredDetails();

                                return;
                            }

                            // Ya se configuraron todos los necesarios
                            $("#mdl-crud-status-responsiva").modal("show");

                            setTimeout(function () {
                                continuarBajasResponsiva();
                            }, 300);

                            return;
                        }

                        // DAÑADO
                        if (statusName === "Dañado") {
                            $("#mdl-crud-status-responsiva").modal("show");

                            // Mostrar los equipos que ya fueron configurados
                            renderConfiguredDetails();

                            return;
                        }

                        // otro estado
                        $("#mdl-crud-status-responsiva").modal("show");
                    }, 300);

                    return;
                }

                form.reset();

                $("#disable_detail_id").val("");
                $("#disable_identifier").val("");
                $("#disable_reason").val("");
                $("#disable_description").val("");

                $("#evidence1").val("");
                $("#evidence2").val("");

                $("#image_preview1").attr("src", "").hide();

                $("#image_preview2").attr("src", "").hide();

                $("#mdl-crud-enable").modal("hide");

                if (window.currentEquipmentToolId) {
                    verDesgloseEquipmentTool(window.currentEquipmentToolId);
                }

                if ($.fn.DataTable.isDataTable("#table_equipments_tools")) {
                    $("#table_equipments_tools").DataTable().ajax.reload(null, false);
                }

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },

        error: function (xhr, status, error) {
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al dar de baja el equipo. Intenta nuevamente.",
                icon: "error",
            });
        },

        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// PREVISUALIZACIÓN EVIDENCIA 1
document.getElementById("evidence1").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview1");

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = "none";
    }
});

// PREVISUALIZACIÓN EVIDENCIA 2
document.getElementById("evidence2").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview2");

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = "none";
    }
});

// HABILITAR EQUIPO O HERRAMIENTA
function cambiarEstadoEquipmentTool(id, action) {
    console.log("Cambiando estado del detalle:", id);
    console.log("Acción:", action);
    $.ajax({
        url: "/disable_equipment_tool_detail/",
        type: "POST",
        data: {
            detail_id: id,
            action: action,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').first().val(),
        },
        success: function (response) {
            console.log("Respuesta al habilitar:", response);
            if (response.success) {
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });

                // Recargar el desglose
                if (window.currentEquipmentToolId) {
                    verDesgloseEquipmentTool(window.currentEquipmentToolId);
                }

                if ($.fn.DataTable.isDataTable("#table_equipments_tools")) {
                    $("#table_equipments_tools").DataTable().ajax.reload(null, false);
                }
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message || "No se pudo habilitar el equipo.",
                    icon: "error",
                });
            }
        },

        error: function (xhr, status, error) {
            console.error("Error al habilitar:", xhr.responseText);

            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al habilitar el equipo. Intenta nuevamente.",
                icon: "error",
            });
        },
    });
}

// HABILITAR EQUIPO O HERRAMIENTA
function cambiarEstadoEquipmentTool(id, action) {
    console.log("Cambiando estado del detalle:", id);
    console.log("Acción:", action);
    $.ajax({
        url: "/disable_equipment_tool_detail/",
        type: "POST",
        data: {
            detail_id: id,
            action: action,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').first().val(),
        },
        success: function (response) {
            console.log("Respuesta al habilitar:", response);
            if (response.success) {
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message || "No se pudo habilitar el equipo.",
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al habilitar:", xhr.responseText);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al habilitar el equipo. Intenta nuevamente.",
                icon: "error",
            });
        },
    });
}
// PREVISUALIZACIÓN IMAGEN
document.getElementById("image").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview");

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = "none";
    }
});
