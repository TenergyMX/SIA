$(document).ready(function () {
    get_responsiva();
    validar_fecha();

    // Manejar el cambio en el estado del equipo
    $("#status_equipment").change(function () {
        var status = $(this).val();
        // Siempre mostrar el campo de comentarios
        $("#comments").removeClass("d-none");

        // Mostrar/Ocultar otros campos basados en el estado
        if (status === "1") {
            // Incompleto
            $("#return_amount_group").removeClass("d-none");
        } else {
            $("#return_amount_group").addClass("d-none");
            $("#return_amount").val("");
        }
    });

    // Al abrir el modal
    $("#mdl-crud-status-responsiva").on("show.bs.modal", function () {
        $("#form_status_responsiva")[0].reset();
        ctxAlmacen.clearRect(0, 0, canvasAlmacen.width, canvasAlmacen.height); // Limpiar el canvas
        $("#comments").addClass("d-none"); // Ocultar el campo de comentarios al abrir
        $("#return_amount_group").addClass("d-none"); // Ocultar el campo de cantidad al abrir
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
            error: function (xhr, error, thrown) {
                console.log("Error en la solicitud AJAX:", thrown);
                alert("No se pudo cargar la información de las responsivas.");
            },
        },
        columns: [
            { data: "id" },
            { data: "equipment_name__equipment_name" },
            { data: "responsible_equipment__username" },
            { data: "amount" },
            {
                data: "status_equipment", // Esta columna mostrará los badges
                render: function (data) {
                    return data;
                },
                orderable: false, // No permitir ordenamiento en esta columna
            },
            { data: "fecha_inicio" },
            { data: "fecha_entrega" },
            { data: "times_requested_responsiva" },
            { data: "date_receipt" },
            {
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
            { data: "comments" },
            {
                data: "btn_action",
                orderable: false,
            },
        ],
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

// Función para mostrar el formulario de estado del equipo.
function chek_responsiva_button(button) {
    var row = $(button).closest("tr");
    var data = $("#table_responsiva").DataTable().row(row).data();

    // Obtener el estado como texto
    var estadoText = $(data.status_equipment).text().trim(); // Extraer solo el texto

    console.log("Estado de la responsiva:", estadoText);

    // Verificar si el estado es "Cancelado"
    if (estadoText === "Cancelado") {
        Swal.fire({
            title: "¡Error!",
            text: "Su responsiva fue cancelada anteriormente, no puedes hacer más cambios.",
            icon: "error",
        });
        return;
    }

    // Verificar si el estado es "Aceptado"
    if (estadoText === "Aceptado") {
        var obj_modal = $("#mdl-crud-status-responsiva");

        // Rellenar el formulario con los datos de la responsiva
        $('#form_status_responsiva input[name="id"]').val(data.id);
        $('#form_status_responsiva input[name="comments"]').val(data.comments);
        $("#status_equipment").val(getStatusValue(estadoText));
        $("#return_amount").val("");

        // Mostrar el modal
        obj_modal.modal("show");
    } else {
        // Si el estado no es "Aceptado", mostramos el mensaje de error
        Swal.fire({
            title: "¡Error!",
            text: "La responsiva no está en estado aceptado, no puedes modificarla.",
            icon: "error",
        });
    }
}

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
document.getElementById("canvas-signature-btn-undo-almacen").addEventListener("click", function () {
    // Implementar funcionalidad de deshacer si es necesario
});

function status_responsiva() {
    var form = $("#form_status_responsiva")[0];
    var formData = new FormData(form);
    let hasDrawing = false;

    // Verificar si todos los campos obligatorios están llenos
    if (!formData.get("comments") || !formData.get("status_equipment")) {
        Swal.fire({
            title: "¡Error!",
            text: "Por favor, completa todos los campos obligatorios.",
            icon: "error",
        });
        return;
    }

    // Validar return_amount solo si el estado es "Incompleto"
    if (formData.get("status_equipment") === "Incompleto") {
        const returnAmount = formData.get("return_amount");
        if (!returnAmount || isNaN(returnAmount) || returnAmount <= 0) {
            Swal.fire({
                title: "¡Error!",
                text: "La cantidad a devolver es obligatoria y debe ser un número válido.",
                icon: "error",
            });
            return;
        }
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

    // if (!hasDrawing) {
    //     Swal.fire({
    //         title: "Error",
    //         text: "Es necesario que el responsable firme, el campo está vacío.",
    //         icon: "warning",
    //         timer: 1500,
    //     });
    //     return;
    // }

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

// Función para actualizar una fecha de entrega
function edit_date_responsiva() {
    var form = $("#form_edit_responsiva")[0];
    var formData = new FormData(form);

    var fecha_entrega = formData.get("fecha_edit");
    var fecha_actual = new Date().toISOString().split("T")[0]; // Obtiene la fecha actual en formato YYYY-MM-DD

    if (fecha_entrega <= fecha_actual) {
        Swal.fire({
            title: "¡Error!",
            text: "La fecha de entrega debe ser mayor a la fecha actual.",
            icon: "error",
        });
        return; // Detener la ejecución si la fecha no es válida
    }

    $.ajax({
        url: "/edit_date_responsiva/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_edit_responsiva")[0].reset();
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
    $.ajax({
        url: "/generate_pdf/" + responsivaId + "/",
        type: "GET",
        xhrFields: {
            responseType: "blob", // Important: Receive the response as a blob (binary data)
        },
        //success: function (response) {
        success: function (blob) {
            // Create a URL for the blob data
            var url = window.URL.createObjectURL(blob);
            Swal.fire({
                title: "¡Éxito!",
                text: "pdf generado exitosamente", //response.message,
                icon: "success",
                timer: 1500,
            }).then(() => {
                // Open the PDF in a new tab
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
