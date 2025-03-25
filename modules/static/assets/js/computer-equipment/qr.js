$(document).ready(function () {
    const computerSystemId = $('[data-computer-qr="qr-info"]').data("computersystem_id");


    // Si hay un QR ya generado en la base de datos, mostrarlo directamente
    if (computerSystemId) {
        $.ajax({
            type: "GET",
            url: `/check_qr_computer/${computerSystemId}/`, 
            success: function(data) {
                if (data.status === "success" && data.qr_url_info) {
                    const qrUrl = data.qr_url_info;
                    // Mostrar el QR y los botones de eliminar y descargar
                    const qrImage = $('<img>').attr('src', qrUrl).attr('alt', 'QR Code');
                    $("#qr-info-computer-container").empty().append(qrImage);
                    $('button[data-computer-qr="delete-qrinfo"]').show();
                    $('button[data-computer-qr="qr-info"]').hide();
                    $('button[data-computer-qr="descargar-qr-info"]').show();
                } else {
                    // Si no hay QR, mostrar solo el botón de generar
                    $('button[data-computer-qr="qr-info"]').show();
                    $('button[data-computer-qr="delete-qrinfo"]').hide(); 
                    $('button[data-computer-qr="descargar-qr-info"]').hide(); 
                    $("#qr-info-computer-container").empty(); 
                }
            },
            error: function(xhr, status, error) {
                console.error("Error al comprobar QR:", status, error);
            }
        });
    }
});


$(document).on("click", "[data-computer-qr='qr-info']", function () {
    const qrImage_info = document.getElementById("qr-info-container");
    const computerSystemId = $(this).data("computersystem_id");
    if (!computerSystemId) {
        console.error("El ID de la computadora no está definido.");
        return;
    }
    generate_qr_computer(computerSystemId, "info"); 
});


// Evento click para el botón de descargar 
$(document).on("click", '[data-computer-qr="descargar-qr-info"]', function () {
    const computerSystemId = $('[data-computer-qr="qr-info"]').data("computersystem_id");

    Swal.fire({
        title: 'Descargando...',
        text: 'Por favor espera mientras se descarga el QR.',
        icon: 'info',
        timer: 3000,  
        showConfirmButton: false,
        allowOutsideClick: false, 
        willOpen: () => {
            Swal.showLoading();
              
        }
    });

    descargar_qr_computer(computerSystemId, "info");
});


$(document).on("click", '[data-computer-qr="delete-qrinfo"]', function () {
    const computerSystemId = $('[data-computer-qr="qr-info"]').data("computersystem_id");
    
    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, eliminarlo",
        cancelButtonText: "Cancelar"
    }).then((result) => {
        if (result.isConfirmed) {
            delete_qr_computer(computerSystemId, "info");
        }
    });
});


function generate_qr_computer(computerSystemId, type) {
    $.ajax({
        type: "GET",
        url: `/generate_qr_computer/${type}/${computerSystemId}/`,
        data: { type: type, computerSystemId: computerSystemId },
        success: function(data) {
            let qrUrl = data.qr_url_info || data.qr_url;
            if (data.status === "success" || data.status === "generados") {
                $("#qr-info-computer-container").empty();

                var qrImage = document.createElement("img");
                qrImage.src = qrUrl;
                qrImage.alt = "QR Code";


                if (qrImage.src) {

                    qrImage.onerror = function () {
                        console.error('Error al cargar la imagen QR:', qrImage.src);
                    };
                    $("#qr-info-computer-container").append(qrImage);

                    $('button[data-computer-qr="delete-qrinfo"]').show();
                    $('button[data-computer-qr="qr-info"]').hide();
                    $('button[data-computer-qr="descargar-qr-info"]').show();

                } else {
                    console.error("La URL del QR no es válida:", data);
                }
            } else {
                console.error("Error en la respuesta del servidor:", data.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al generar el QR:", status, error);
        }
    });
}



function descargar_qr_computer(computerSystemId, type) {
    $.ajax({
        type: "GET",
        url: "/descargar_qr_computer/",
        data: {
            type: type,
            computerSystemId: computerSystemId
        },
        success: function(data) {
            var url_computer = data.url_computer;
            if (url_computer) {
                var a = document.createElement("a");
                a.href = url_computer;
                a.download = url_computer.substring(url_computer.lastIndexOf("/") + 1); 
                a.style.display = 'none'; 
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                Swal.fire({
                    title: '¡Descarga Completa!',
                    text: 'El QR se ha descargado exitosamente.',
                    icon: 'success',
                    timer: 1000,  
                    showConfirmButton: false
                });
            } else {
                console.error("Received an invalid or empty URL from the server.");
                Swal.fire("Error", "Hubo un problema al intentar descargar el QR.", "error");
            }
        },
        error: function(xhr, status, error) {
            console.error("An error occurred while trying to download the QR: ", status, error);
            Swal.fire("Error", "Hubo un error al intentar descargar el QR.", "error");
        }
    });
}

function delete_qr_computer(computerSystemId, type) {
    if (!computerSystemId) {
        console.error("El ID de la computadora no está definido.");
        return;
    }

    $.ajax({
        url: `/delete_qr_computer/${type}/${computerSystemId}/`,
        type: "POST",
        data: {
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function(response) {
            if (response.status === "success") {
                Swal.fire({
                    title: "¡Eliminado!",
                    text: "El QR ha sido eliminado.",
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => {
                    $('button[data-computer-qr="delete-qrinfo"]').hide();
                    $('button[data-computer-qr="descargar-qr-info"]').hide();
                    $('button[data-computer-qr="qr-info"]').show();
                    $("#qr-info-computer-container").empty();
                });
            } else {
                console.error("Error al eliminar el QR: ", response.message);
                Swal.fire("Error", response.message, "error");
            }
        },
        error: function(xhr, status, error) {
            console.error("Ocurrió un error al intentar eliminar el QR: ", status, error);
            Swal.fire("Error", "Hubo un error al eliminar el QR.", "error");
        }
    });
}


