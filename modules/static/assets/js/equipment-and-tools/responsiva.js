$(document).ready(function () {
    get_responsiva();
    validar_fecha();
    console.log("===== RESPONSIVA.JS CARGADO =====");
    // Manejar el cambio en el estado del equipo
    $("#status_equipment").change(function () {
        var status = $(this).val();
        console.log("Estado seleccionado:", status);

        // comentarios
        $("#comments_group").removeClass("d-none");

        $("#comments").prop("required", true);

        // ocultar y limpiar los campos
        $("#return_amount_group").addClass("d-none");
        $("#details_to_deactivate_group").addClass("d-none");
        $("#return_amount").val("");
        $("#details_to_deactivate").empty();

        // estado Regresado
        if (status === "0") {
            console.log("Estado: regresado");
            $("#comments").prop("required", false);
        }

        // Incompleto
        else if (status === "1") {
            console.log("Estado: Incompleto");
            // Mostrar cantidad a devolver
            $("#return_amount_group").removeClass("d-none");
            $("#details_to_deactivate_group").removeClass("d-none");
            $("#comments").prop("required", true);
            // Cargar los equipos asignados a la responsiva
            var responsivaId = $('#form_status_responsiva input[name="id"]').val();
            loadDetailsToDeactivate(responsivaId);
        }

        // dañado
        else if (status === "2") {
            console.log("Estado: Dañado");

            $("#return_amount_group").removeClass("d-none");
            $("#details_to_deactivate_group").removeClass("d-none");
            $("#comments_group").prop("required", true);

            var responsivaId = $('#form_status_responsiva input[name="id"]').val();
            loadDetailsToDeactivate(responsivaId);
        }

        // no devuelto
        else if (status === "3") {
            console.log("Estado: No devuelto");
            $("#comments").prop("required", true);
        }
    });
});

//tabla de responsivas
function get_responsiva() {
    $("#table_responsiva").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_responsiva/",
            type: "GET",
            dataSrc: "data",

            data: function (d) {
                const params = new URLSearchParams(window.location.search);
                const responsivaId = params.get("responsiva_id");
                d.responsiva_id = responsivaId;
            },

            error: function (xhr, error, thrown) {
                console.log("Error en la solicitud AJAX:", thrown);
                alert("No se pudo cargar la información de las responsivas.");
            },
        },
        columns: [
            {
                title: "ID",
                data: "id",
                className: "text-center toggleable",
            },
            {
                title: "Nombre del equipo",
                data: "equipment_name__equipment_name",
                className: "text-center toggleable",
            },
            {
                title: "Responsable del equipo",
                data: "responsible_equipment__username",
                className: "text-center toggleable",
            },
            {
                title: "Cantidad",
                data: "amount",
                className: "text-center toggleable",
            },
            {
                title: "Estado del equipo",
                data: "status_equipment",
                render: function (data) {
                    return data;
                },
                orderable: false,
            },
            {
                title: "Fecha Inicio",
                data: "fecha_inicio",
                className: "text-center toggleable",
            },
            {
                title: "Fecha Entrega",
                data: "fecha_entrega",
                className: "text-center toggleable",
            },
            {
                title: "Fecha Registro",
                data: "fecha_registro",
                className: "text-center toggleable",
                render: function (data, type, row) {
                    if (!data) {
                        return "";
                    }

                    return data.split("T")[0];
                },
            },
            {
                title: "Tiempo solicitado",
                data: "times_requested_responsiva",
                className: "text-center toggleable",
            },
            {
                title: "Fecha de recibido",
                data: "date_receipt",
                className: "text-center toggleable",
            },
            {
                title: "Responsable de almacen",
                data: "status_modified_by__username",
                className: "text-center toggleable",
            },
            {
                title: "Responsiva del equipo",
                data: "id",
                render: function (data, type, row) {
                    if (row.status_equipment.includes("Cancelado")) {
                        return "";
                    } else {
                        return (
                            '<button class="btn btn-primary-light btn-sm" onclick="generatePdf(' +
                            row.id +
                            ')"><i class="fa-solid fa-file-pdf"></i> Generar PDF</button>'
                        );
                    }
                },
                orderable: false,
            },
            {
                title: "Comentarios",
                data: "comments",
                className: "text-center toggleable",
            },
            {
                title: "Acciones",
                data: "btn_action",
                orderable: false,
            },
        ],
        order: [[7, "desc"]],

        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10,
    });
}

// Función para obtener el valor del estado a partir del nombre
function getStatusValue(statusName) {
    const statusMap = {
        Regresado: "0",
        Incompleto: "1",
        Dañado: "2",
        "No devuelto": "3",
        Aceptado: "4",
        Solicitado: "5",
        Cancelado: "6",
        Atrasado: "7",
    };
    return statusMap[statusName] || "";
}

// Función para aprobar la responsiva del usuario
function approve_button(button) {
    const row = $(button).closest("tr");
    const data = $("#table_responsiva").DataTable().row(row).data();

    if (data.status_modified) {
        Swal.fire({
            title: "¡Error!",
            text: "La responsiva ya fue aprobada, no puede ser aprobada de nuevo.",
            icon: "error",
        });
        return;
    }

    Swal.fire({
        title: "¿Estás seguro que deseas aceptar la responsiva?",
        text: "¡Esta acción no se puede deshacer!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, aceptar responsiva!",
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: "Aprobando responsiva...",
                text: "La plataforma está procesando la información. Por favor, espera.",
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            $.ajax({
                url: "/approve_responsiva/",
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
                            title: "¡Responsiva Aceptada!",
                            text: "La responsiva fue aceptada correctamente.",
                            icon: "success",
                            timer: 1500,
                        }).then(() => {
                            $("#table_responsiva").DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Error al aceptar la responsiva:", error);
                    Swal.fire("Error", "Hubo un error al aceptar la responsiva", "error");
                },
            });
        }
    });
}

// Función para cancelar la responsiva del usuario
function cancel_button(button) {
    const row = $(button).closest("tr");
    const data = $("#table_responsiva").DataTable().row(row).data();

    if (data.status_modified) {
        Swal.fire({
            title: "¡Error!",
            text: "La responsiva ya ha sido cancelada y no se puede cancelar de nuevo.",
            icon: "error",
        });
        return;
    }

    Swal.fire({
        title: "¿Estás seguro que deseas cancelar la responsiva del equipo?",
        text: "¡Esta acción no se puede deshacer!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, cancelar responsiva!",
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: "Cancelando responsiva...",
                text: "La plataforma está procesando la información. Por favor, espera.",
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            $.ajax({
                url: "/cancel_responsiva/",
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
                            title: "¡Responsiva cancelada!",
                            text: response.message,
                            icon: "success",
                            timer: 1500,
                        }).then(() => {
                            $("#table_responsiva").DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Error al cancelar la responsiva:", error);
                    Swal.fire("Error", "Hubo un error al cancelar la responsiva", "error");
                },
            });
        }
    });
}

// Función para mostrar el formulario de estado del equipo
function chek_responsiva_button(button) {
    var row = $(button).closest("tr");
    var data = $("#table_responsiva").DataTable().row(row).data();

    // Obtener el estado como texto
    var estadoText = $("<div>").html(data.status_equipment).text().trim();

    // Verificar si está cancelada
    if (estadoText === "Cancelado") {
        Swal.fire({
            title: "¡Error!",
            text: "Su responsiva fue cancelada anteriormente, no puedes hacer más cambios.",
            icon: "error",
        });
        return;
    }

    // Solo se puede modificar cuando está aceptada
    if (estadoText !== "Aceptado") {
        Swal.fire({
            title: "¡Error!",
            text: "La responsiva no está en estado aceptado, no puedes modificarla.",
            icon: "error",
        });
        return;
    }

    var obj_modal = $("#mdl-crud-status-responsiva");

    $('#form_status_responsiva input[name="id"]').val(data.id);

    // Limpiar formulario
    $("#status_equipment").val("").trigger("change");
    $("#return_amount").val("");
    $("#details_to_deactivate").val(null).trigger("change");
    $("#selected_details_to_deactivate").empty();
    $("#comments").val("");

    // Reiniciar variables del flujo de baja
    window.currentResponsivaId = data.id;

    // Ocultar campos
    $("#return_amount_group").addClass("d-none");
    $("#details_to_deactivate_group").addClass("d-none");
    $("#comments_group").addClass("d-none");

    // Cargar los equipos asignados a la responsiva
    loadDetailsToDeactivate(data.id);

    // Mostrar modal
    obj_modal.modal("show");
}

// Validar return_amount solo si el estado es "Incompleto"
$("#status_equipment").change(function () {
    var status = $(this).val();

    console.log("==========================================");
    console.log("ESTADO SELECCIONADO:", status);
    console.log("==========================================");

    // Ocultar selección de detalles inicialmente
    $("#return_amount_group").addClass("d-none");
    $("#details_to_deactivate_group").addClass("d-none");
    $("#return_amount").val("");
    $("#details_to_deactivate").val(null).trigger("change");
    $("#selected_details_to_deactivate").empty();
    $("#comments_group").removeClass("d-none");
    $("#comments").prop("required", true);

    // Regresado
    if (status === "Regresado") {
        console.log("Estado: REGRESADO");
        console.log("Se tomarán TODOS los detalles.");
        $("#comments").prop("required", false);
    } else if (status === "Incompleto") {
        console.log("Estado: INCOMPLETO");
        console.log("Se deben seleccionar los detalles.");
        $("#return_amount_group").removeClass("d-none");
        $("#details_to_deactivate_group").removeClass("d-none");
        $("#comments").prop("required", true);
        var responsivaId = $("#form_status_responsiva input[name='id']").val();
        loadDetailsToDeactivate(responsivaId);
    }
    // Dañado
    else if (status === "Dañado") {
        console.log("Estado: DAÑADO");
        console.log("Se deben seleccionar los detalles.");
        $("#details_to_deactivate_group").removeClass("d-none");
        $("#comments").prop("required", true);
        var responsivaId = $("#form_status_responsiva input[name='id']").val();
        loadDetailsToDeactivate(responsivaId);
    }
    // no devuelto
    else if (status === "No devuelto") {
        console.log("Estado: NO DEVUELTO");
        console.log("Se tomarán TODOS los detalles.");
        $("#comments").prop("required", true);
    }
});

// Variables para la firma del almacén
let canvasAlmacen = document.getElementById("canvas-signature-almacen");
let ctxAlmacen = canvasAlmacen.getContext("2d");
let drawingAlmacen = false;
let lastXAlmacen = 0;
let lastYAlmacen = 0;

// Configura el contexto para la firma del almacén
ctxAlmacen.strokeStyle = "black";
ctxAlmacen.lineWidth = 2;
ctxAlmacen.lineCap = "round";

// Eventos para dibujar en el canvas de almacén
canvasAlmacen.addEventListener("mousedown", function (e) {
    drawingAlmacen = true;
    lastXAlmacen = e.offsetX;
    lastYAlmacen = e.offsetY;
});

canvasAlmacen.addEventListener("mousemove", function (e) {
    if (drawingAlmacen) {
        ctxAlmacen.beginPath();
        ctxAlmacen.moveTo(lastXAlmacen, lastYAlmacen);
        ctxAlmacen.lineTo(e.offsetX, e.offsetY);
        ctxAlmacen.stroke();
        lastXAlmacen = e.offsetX;
        lastYAlmacen = e.offsetY;
    }
});

canvasAlmacen.addEventListener("mouseup", function () {
    drawingAlmacen = false;
    ctxAlmacen.beginPath();
});

// Limpiar el canvas de la firma del almacén
document
    .getElementById("canvas-signature-btn-clear-almacen")
    .addEventListener("click", function () {
        ctxAlmacen.clearRect(0, 0, canvasAlmacen.width, canvasAlmacen.height);
        undoStack = [];
    });

// Deshacer en el canvas de la firma del almacén
document
    .getElementById("canvas-signature-btn-undo-almacen")
    .addEventListener("click", function () {});

function status_responsiva() {
    var form = $("#form_status_responsiva")[0];
    var formData = new FormData(form);
    let hasDrawing = false;

    const statusValue = formData.get("status_equipment");
    const return_amount = formData.get("return_amount");
    const totalAmount = $("#details_to_deactivate option").filter(function () {
        return $(this).val() !== "";
    }).length;
    const comentario = formData.get("comments");

    const statusName =
        {
            0: "Regresado",
            1: "Incompleto",
            2: "Dañado",
            3: "No devuelto",
        }[statusValue] || statusValue;

    if (!statusValue) {
        Swal.fire({
            title: "¡Error!",
            text: "Por favor selecciona el estado del equipo.",
            icon: "error",
        });
        return;
    }

    if (statusName !== "Regresado" && !formData.get("comments")) {
        Swal.fire({
            title: "¡Error!",
            text: "Por favor agrega los comentarios.",
            icon: "error",
        });
        return;
    }
    // Estado incompleto
    if (statusName === "Incompleto") {
        const returnAmount = parseInt(formData.get("return_amount"), 10);

        const configuredIds = (window.detailsConfiguredForDisable || []).map(String);

        // Validar cantidad devuelta
        if (isNaN(returnAmount) || returnAmount <= 0) {
            Swal.fire({
                title: "¡Error!",
                text: "Debes indicar la cantidad de equipos que regresan.",
                icon: "error",
            });
            return;
        }

        // Validar total
        if (isNaN(totalAmount) || totalAmount <= 0) {
            Swal.fire({
                title: "¡Error!",
                text: "No fue posible obtener la cantidad total de equipos de la responsiva.",
                icon: "error",
            });
            return;
        }

        // No puede regresar más de los prestados
        if (returnAmount >= totalAmount) {
            Swal.fire({
                title: "¡Error!",
                text:
                    "En una responsiva incompleta debe regresar menos de " +
                    totalAmount +
                    " equipo(s).",
                icon: "error",
            });
            return;
        }

        // Calcular equipos que NO regresaron
        const amountToDeactivate = totalAmount - returnAmount;

        window.maxDetailsToDeactivate = amountToDeactivate;

        // se deben configurar exactamente los que NO regresaron
        if (configuredIds.length !== amountToDeactivate) {
            Swal.fire({
                title: "Configuración incompleta",
                text:
                    "Debes configurar exactamente " +
                    amountToDeactivate +
                    " equipo(s) que no regresaron. " +
                    "Actualmente hay " +
                    configuredIds.length +
                    " configurado(s).",
                icon: "warning",
            });

            return;
        }

        // Agregar equipos a FormData
        formData.delete("details_to_deactivate");

        configuredIds.forEach(function (detailId) {
            formData.append("details_to_deactivate", detailId);
        });
    }

    // DAÑADO
    else if (statusName === "Dañado") {
        const configuredIds = (window.detailsConfiguredForDisable || []).map(String);

        // Debe seleccionar al menos un equipo
        if (configuredIds.length === 0) {
            Swal.fire({
                title: "¡Error!",
                text: "Debes seleccionar al menos un equipo dañado.",
                icon: "error",
            });

            return;
        }

        // Para Dañado se pueden seleccionar TODOS
        if (configuredIds.length > totalAmount) {
            Swal.fire({
                title: "¡Error!",
                text: "No puedes seleccionar más de " + totalAmount + " equipo(s).",
                icon: "error",
            });

            return;
        }

        // Agregar equipos dañados
        formData.delete("details_to_deactivate");

        configuredIds.forEach(function (detailId) {
            formData.append("details_to_deactivate", detailId);
        });
    }

    //regresado
    else if (statusName === "Regresado") {
        console.log("Regresado: backend procesará todos los detalles.");
        formData.delete("details_to_deactivate");
    }

    //No devuelto
    else if (statusName === "No devuelto") {
        console.log("No devuelto: backend procesará todos los detalles.");
        formData.delete("details_to_deactivate");
    }

    // Verificar si hay firma
    try {
        const imgData = ctxAlmacen.getImageData(0, 0, canvasAlmacen.width, canvasAlmacen.height);
        const pixelData = imgData.data;

        for (let i = 0; i < pixelData.length; i += 4) {
            if (pixelData[i + 3] !== 0) {
                // Comprobar el componente alfa
                hasDrawing = true;
                break;
            }
        }
    } catch (error) {
        console.error("Error al obtener datos del canvas:", error);
        Swal.fire({
            title: "Error",
            text: "No se pudo obtener la firma. Por favor, inténtalo de nuevo.",
            icon: "error",
        });
        return;
    }

    // Convertir la firma a Blob
    const dataURL = canvasAlmacen.toDataURL();
    const byteString = atob(dataURL.split(",")[1]);
    const mimeString = dataURL.split(",")[0].split(":")[1].split(";")[0];
    const ab = new Uint8Array(byteString.length);

    for (let i = 0; i < byteString.length; i++) {
        ab[i] = byteString.charCodeAt(i);
    }

    const blobAlmacen = new Blob([ab], { type: mimeString });
    formData.append("signature_almacen", blobAlmacen, "signature_almacen.png");

    Swal.fire({
        title: "Actualizando responsiva...",
        text: "La plataforma está procesando la información. Por favor, espera.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/status_responsiva/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_status_responsiva")[0].reset();
                ctxAlmacen.clearRect(0, 0, canvasAlmacen.width, canvasAlmacen.height);
                $("#mdl-crud-status-responsiva").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_responsiva").DataTable().ajax.reload();
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
                text: "Hubo un error al guardar la responsiva.",
                icon: "error",
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// FIRMA DEL ALMACÉN - MODIFICAR FECHA DE ENTREGA
let canvasAlmacen2 = document.getElementById("canvas-signature-almacen2");
let ctxAlmacen2 = canvasAlmacen2.getContext("2d");

let drawingAlmacen2 = false;
let lastXAlmacen2 = 0;
let lastYAlmacen2 = 0;

// Historial de cambios de la firma
let undoStackAlmacen2 = [];

// Configuración
ctxAlmacen2.strokeStyle = "black";
ctxAlmacen2.lineWidth = 2;
ctxAlmacen2.lineCap = "round";
ctxAlmacen2.lineJoin = "round";

//iniciar un trazo
canvasAlmacen2.addEventListener("mousedown", function (e) {
    drawingAlmacen2 = true;

    lastXAlmacen2 = e.offsetX;
    lastYAlmacen2 = e.offsetY;

    // Guardar el estado actual ANTES de comenzar el nuevo trazo
    undoStackAlmacen2.push(
        ctxAlmacen2.getImageData(0, 0, canvasAlmacen2.width, canvasAlmacen2.height)
    );
});

// dibujar la firma
canvasAlmacen2.addEventListener("mousemove", function (e) {
    if (!drawingAlmacen2) {
        return;
    }

    ctxAlmacen2.beginPath();

    ctxAlmacen2.moveTo(lastXAlmacen2, lastYAlmacen2);

    ctxAlmacen2.lineTo(e.offsetX, e.offsetY);

    ctxAlmacen2.stroke();

    lastXAlmacen2 = e.offsetX;
    lastYAlmacen2 = e.offsetY;
});

// terminar trazo
canvasAlmacen2.addEventListener("mouseup", function () {
    drawingAlmacen2 = false;

    ctxAlmacen2.beginPath();
});

canvasAlmacen2.addEventListener("mouseleave", function () {
    drawingAlmacen2 = false;

    ctxAlmacen2.beginPath();
});

// Limpiar campo
document
    .getElementById("canvas-signature-btn-clear-almacen2")
    .addEventListener("click", function () {
        ctxAlmacen2.clearRect(0, 0, canvasAlmacen2.width, canvasAlmacen2.height);

        undoStackAlmacen2 = [];

        drawingAlmacen2 = false;
    });

//regresar un cambio
document
    .getElementById("canvas-signature-btn-undo-almacen2")
    .addEventListener("click", function () {
        // Si no hay cambios anteriores
        if (undoStackAlmacen2.length === 0) {
            return;
        }

        // Obtener el último estado guardado
        const previousState = undoStackAlmacen2.pop();

        // Restaurar el canvas
        ctxAlmacen2.putImageData(previousState, 0, 0);
    });

// Función para mostrar el formulario para editar la fecha de regreso del equipo o herramienta.
function edit_date(button) {
    var row = $(button).closest("tr");
    var data = $("#table_responsiva").DataTable().row(row).data();
    var obj_modal = $("#mdl-crud-edit-responsiva");

    $('#form_edit_responsiva input[name="id"]').val(data.id);
    $('#form_edit_responsiva input[name="fecha_edit"]').val(data.fecha_entrega);

    // Muestra el modal
    obj_modal.modal("show");
}

//Dar clic al botón de editar
$(document).on("submit", "#form_edit_responsiva", function (e) {
    e.preventDefault();
    edit_date_responsiva();
});

// Función para actualizar una fecha de entrega
function edit_date_responsiva() {
    var form = $("#form_edit_responsiva")[0];
    var formData = new FormData(form);

    var fecha_entrega = formData.get("fecha_edit");
    console.log("esto contiene la fecha de entrega", fecha_entrega);

    var fecha_actual = new Date().toISOString().split("T")[0];
    console.log("esto contiene la fecha actual", fecha_actual);

    if (!fecha_entrega) {
        Swal.fire({
            title: "¡Error!",
            text: "Por favor selecciona la nueva fecha de entrega.",
            icon: "error",
        });
        return;
    }

    if (fecha_entrega <= fecha_actual) {
        Swal.fire({
            title: "¡Error!",
            text: "La fecha de entrega debe ser mayor a la fecha actual.",
            icon: "error",
        });
        return;
    }

    //validar motivo
    var motivo = formData.get("reason_date_change");

    if (!motivo || !motivo.trim()) {
        Swal.fire({
            title: "¡Error!",
            text: "Por favor agrega el motivo del cambio de fecha.",
            icon: "error",
        });
        return;
    }

    //validar firma
    let hasDrawing = false;
    try {
        const imgData = ctxAlmacen2.getImageData(0, 0, canvasAlmacen2.width, canvasAlmacen2.height);
        const pixelData = imgData.data;
        for (let i = 0; i < pixelData.length; i += 4) {
            if (pixelData[i + 3] !== 0) {
                hasDrawing = true;
                break;
            }
        }
    } catch (error) {
        console.error("Error al obtener datos del canvas:", error);
        Swal.fire({
            title: "Error",
            text: "No se pudo obtener la firma. Por favor, inténtalo de nuevo.",
            icon: "error",
        });
        return;
    }
    //si no existe la firma
    if (!hasDrawing) {
        Swal.fire({
            title: "¡Firma requerida!",
            text: "Debes ingresar la firma del usuario",
            icon: "warning",
        });
        return;
    }

    //convertir firma
    const dataURL = canvasAlmacen2.toDataURL();
    const byteString = atob(dataURL.split(",")[1]);
    const mimeString = dataURL.split(",")[0].split(":")[1].split(";")[0];
    const ab = new Uint8Array(byteString.length);
    for (let i = 0; i < byteString.length; i++) {
        ab[i] = byteString.charCodeAt(i);
    }

    const blobAlmacen = new Blob([ab], { type: mimeString });
    formData.append("signature_almacen", blobAlmacen, "signature_almacen.png");

    $.ajax({
        url: "/edit_date_responsiva/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_edit_responsiva")[0].reset();

                ctxAlmacen2.clearRect(0, 0, canvasAlmacen2.width, canvasAlmacen2.height);

                $("#mdl-crud-edit-responsiva").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_responsiva").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "Error",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al actualizar la fecha de entrega del equipo:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar la nueva fecha.",
                icon: "error",
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

//función para validar si la fecha esta en estado de atrasado
function validar_fecha() {
    $.ajax({
        url: "/validar_fecha/",
        type: "GET",
        success: function (response) {
            if (response.success) {
                console.log(response.message);
            } else {
                console.error(response.message);
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al actualizar los estados:", error);
        },
    });
}

// Función para generar PDF
function generatePdf(responsivaId) {
    Swal.fire({
        title: "Generando PDF...",
        text: "La plataforma está generando el documento. Por favor, espera.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/generate_pdf/" + responsivaId + "/",
        type: "GET",
        xhrFields: {
            responseType: "blob",
        },
        success: function (blob) {
            var url = window.URL.createObjectURL(blob);
            Swal.fire({
                title: "¡Éxito!",
                text: "pdf generado exitosamente",
                icon: "success",
                timer: 1500,
            }).then(() => {
                window.open(url, "_blank");
            });
        },
        error: function (xhr, error, thrown) {
            console.error("Error en la solicitud AJAX:", thrown);
            Swal.fire({
                title: "¡Error!",
                text: "No se pudo generar el PDF.",
                icon: "error",
            });
        },
    });
}

// Cargar los equipos/herramientas asignados a una responsiva
function loadDetailsToDeactivate(responsivaId) {
    $.ajax({
        url: "/get_responsiva_details/",
        type: "GET",
        data: {
            responsiva_id: responsivaId,
        },

        success: function (response) {
            const $select = $("#details_to_deactivate");
            // Limpiar opciones y selección anterior
            $select.empty().val([]);
            if (!response.success || !response.data || response.data.length === 0) {
                console.log("No se encontraron detalles asignados.");

                $select.append(
                    $("<option>", {
                        value: "",
                        text: "No hay equipos asignados",
                    })
                );

                // Actualizar Select2 si está inicializado
                if ($select.hasClass("select2-hidden-accessible")) {
                    $select.trigger("change.select2");
                }

                return;
            }

            // Cargar equipos
            response.data.forEach(function (detail) {
                $select.append(
                    $("<option>", {
                        value: detail.id,
                        text: detail.identifier,
                    })
                );
            });

            console.log("Equipos cargados:", response.data.length);

            // Actualizar Select2
            if ($select.hasClass("select2-hidden-accessible")) {
                $select.trigger("change.select2");
            }
        },

        error: function (xhr) {
            console.error("Error al cargar los detalles:", xhr.responseText);
            const $select = $("#details_to_deactivate");
            $select.empty().val([]);
            Swal.fire({
                title: "Error",
                text: "No fue posible cargar los equipos asignados.",
                icon: "error",
            });
        },
    });
}

// Validar el máximo de equipos seleccionados
$(document).on("change", "#details_to_deactivate", function () {
    var selectedIds = ($(this).val() || []).map(String);

    const statusValue = $("#status_equipment").val();

    const statusName =
        {
            0: "Regresado",
            1: "Incompleto",
            2: "Dañado",
            3: "No devuelto",
        }[statusValue] || statusValue;

    // determinar el máximo permitido
    let maxAllowed = 0;

    if (statusName === "Dañado") {
        // dañado pueden ser todos los equipos
        maxAllowed = $("#details_to_deactivate option").filter(function () {
            return $(this).val() !== "";
        }).length;
    } else {
        // incompleto, se mantiene el máximo
        maxAllowed = window.maxDetailsToDeactivate || 0;
    }
    // Validar maximo
    if (selectedIds.length > maxAllowed) {
        const validIds = selectedIds.slice(0, maxAllowed);
        $(this).val(validIds);
        selectedIds = validIds;

        Swal.fire({
            title: "Límite alcanzado",
            text: "Solo puedes seleccionar " + maxAllowed + " equipo(s) para dar de baja.",
            icon: "warning",
        });
    }

    window.detailsSelectedForDisable = selectedIds;

    //deshabilitar opciones
    $("#details_to_deactivate option").each(function () {
        const optionId = String($(this).val());
        if (!optionId) {
            return;
        }

        if (selectedIds.includes(optionId)) {
            // Los seleccionados permanecen habilitados
            $(this).prop("disabled", false);
        } else {
            // DAÑADO:
            // solo bloquear cuando realmente se alcanzó el máximo de equipos disponibles.
            if (statusName === "Dañado") {
                $(this).prop("disabled", selectedIds.length >= maxAllowed);
            } else {
                // INCOMPLETO
                // se mantiene el comportamiento anterior
                $(this).prop("disabled", selectedIds.length >= maxAllowed);
            }
        }
    });

    // Mostrar equipos seleccionados
    var container = $("#selected_details_to_deactivate");

    container.empty();

    selectedIds.forEach(function (detailId) {
        var identifier = $("#details_to_deactivate option[value='" + detailId + "']").text();

        var row = `
            <div class="d-flex align-items-center justify-content-between border rounded p-2 mb-2">

                <div>
                    <i class="fas fa-tools me-2"></i>
                    <strong>${identifier}</strong>
                </div>

                <button
                    type="button"
                    class="btn btn-danger btn-sm btn-configure-detail-disable"
                    data-id="${detailId}"
                    data-identifier="${identifier}">

                    <i class="fas fa-ban me-1"></i>
                    Configurar baja
                </button>

            </div>
        `;

        container.append(row);
    });
});

// Actualizar cantidad máxima de detalles que pueden darse de baja
$(document).on("input", "#return_amount", function () {
    const returnAmount = parseInt($(this).val(), 10);

    const totalAmount = $("#details_to_deactivate option").filter(function () {
        return $(this).val() !== "";
    }).length;

    // cantidad no valida válida
    if (isNaN(returnAmount) || returnAmount <= 0) {
        window.maxDetailsToDeactivate = 0;
        console.log("Cantidad inválida");
        return;
    }

    // No puede regresar más equipos de los asignados
    if (returnAmount > totalAmount) {
        window.maxDetailsToDeactivate = 0;

        console.log("Cantidad mayor al total. Máximo para baja: 0");

        return;
    }

    // Calcular cuántos deben configurarse para baja
    const amountToDeactivate = totalAmount - returnAmount;

    window.maxDetailsToDeactivate = amountToDeactivate;
});

//abrir el modal para dar de baja un equipo seleccionado
$(document).on("click", ".btn-configure-detail-disable", function () {
    const id = String($(this).data("id"));
    const identifier = $(this).data("identifier");

    window.currentDisableDetailFromResponsiva = id;
    window.disableDetailFromResponsiva = true;

    $("#formdisable").data("data-from-responsiva", true);
    console.log("FORMULARIO DESDE RESPONSIVA:", $("#formdisable").attr("data-from-responsiva"));
    $("#formdisable").data("responsiva-id", window.currentResponsivaId);

    $.ajax({
        url: "/modal_equipment_tool_detail/",
        type: "GET",

        data: {
            id: id,
        },

        success: function (response) {
            console.log("Respuesta modal baja:", response);

            if (!response.success) {
                Swal.fire(
                    "Error",
                    response.message || "No se pudo obtener la información.",
                    "error"
                );

                return;
            }

            // Cargar el detalle real
            $("#disable_detail_id").val(response.data.id);
            $("#disable_identifier").val(response.data.identifier);

            // Limpiar información anterior
            $("#disable_reason").val("");
            $("#disable_description").val("");

            $("#evidence1").val("");
            $("#evidence2").val("");

            $("#image_preview1").attr("src", "").hide();

            $("#image_preview2").attr("src", "").hide();

            $("#mdl-crud-enable").modal("show");
        },

        error: function (xhr) {
            console.error("Error:", xhr.responseText);

            Swal.fire("Error", "No se pudo obtener la información del equipo.", "error");
        },
    });
});

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

// LLAMAR A LA FUNCION PARA DESHABILITAR EQUIPO
$(document).on("submit", "#formdisable", function (e) {
    e.preventDefault();
    disable_equipment_tool_detail();
});
