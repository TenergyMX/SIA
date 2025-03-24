$(document).on("click", "[data-infrastructure-item='qr_code']", function () { 
    let itemId = $(this).data("id");  
    console.log("Entramos al QR del item de infraestructura, el ID es:", itemId);

    if (itemId) {
        $("#infra-item-id").val(itemId); // Guardar ID en el input oculto
        $("#qr-item-id").text(`ID del ítem: ${itemId}`);
        $("#mdl-crud-qr").modal("show");

        // Verificar si el QR ya está generado
        $.ajax({
            type: "GET",
            url: `/check_qr_infraestructure/${itemId}/`,
            success: function(data) {
                console.log("Esto contiene data:", data);

                if (data.status === "success" && data.qr_url_info) {
                    const qrUrl = data.qr_url_info;
                    console.log("QR URL:", qrUrl);

                    const qrImage = $('<img>').attr('src', qrUrl).attr('alt', 'QR Code');
                    $("#qr-info-infraestructure-container").empty().append(qrImage);

                    $('button[data-infraestructure-qr="delete-qrinfo"]').show();
                    $('button[data-infraestructure-qr="qr-info"]').hide();
                    $('button[data-infraestructure-qr="descargar-qr-info"]').show();
                } else {
                    console.log("No se generó el QR, status:", data.status);
                    $("#qr-info-infraestructure-container").empty();

                    setTimeout(function() {
                        $('button[data-infraestructure-qr="qr-info"]').show();
                    }, 100);

                    $('button[data-infraestructure-qr="delete-qrinfo"]').hide();
                    $('button[data-infraestructure-qr="descargar-qr-info"]').hide();
                }
            },
            error: function(xhr, status, error) {
                console.error("Error al verificar el QR:", error);
            }
        });
    } else {
        console.error("Error: No se encontró el ID del ítem.");
    }
});


$(document).on("click", "[data-infraestructure-qr='qr-info']", function () {
    const itemId = $("#infra-item-id").val(); 
    console.log("Este es el ID de la infraestructura:", itemId);

    if (!itemId) {
        console.error("El ID de la infraestructura no está definido.");
        return;
    }

    generate_qr_infraestructure(itemId, "info"); 
});


function generate_qr_infraestructure(itemId, type) {
    $.ajax({
        type: "GET",
        url: `/generate_qr_infraestructure/${type}/${itemId}/`,
        data: { type: type, itemId: itemId },
        success: function(data) {
            console.log("Respuesta del servidor:", data);
            let qrUrl = data.qr_url_info || data.qr_url;
            console.log("data.qr_url:", qrUrl);
            if (data.status === "success" || data.status === "generados") {
                $("#qr-info-infraestructure-container").empty();

                var qrImage = document.createElement("img");
                qrImage.src = qrUrl;
                qrImage.alt = "QR Code";


                if (qrImage.src) {

                    qrImage.onerror = function () {
                        console.error('Error al cargar la imagen QR:', qrImage.src);
                    };
                    $("#qr-info-infraestructure-container").append(qrImage);

                    $('button[data-infraestructure-qr="delete-qrinfo"]').show();
                    $('button[data-infraestructure-qr="qr-info"]').hide();
                    $('button[data-infraestructure-qr="descargar-qr-info"]').show();

                    console.log(`QR cargado correctamente: ${qrImage.src}`);
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


// Evento click para el botón de descargar 
$(document).on("click", '[data-infraestructure-qr="descargar-qr-info"]', function () {
    const itemId = $("#infra-item-id").val(); 
    console.log("voy a descargar el qr del id:", itemId);
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

    descargar_qr_infraestructure(itemId, "info");
});


function descargar_qr_infraestructure(itemId, type) {
    console.log("este es el id que se esta descarga", itemId);

    $.ajax({
        type: "GET",
        url: "/descargar_qr_infraestructure/",
        data: {
            type: type,
            itemId: itemId
            
        },
        success: function(data) {
            var url_infraestructure = data.url_infraestructure;
            if (url_infraestructure) {
                var a = document.createElement("a");
                a.href = url_infraestructure;
                a.download = url_infraestructure.substring(url_infraestructure.lastIndexOf("/") + 1); 
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


$(document).on("click", '[data-infraestructure-qr="delete-qrinfo"]', function () {
    const itemId = $("#infra-item-id").val(); 
    console.log("este es el qr a eliminar:", itemId);
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
            delete_qr_infraestructure(itemId, "info");
        }
    });
});

function delete_qr_infraestructure(itemId, type) {
    if (!itemId) {
        console.error("El ID de la computadora no está definido.");
        return;
    }

    $.ajax({
        url: `/delete_qr_infraestructure/${type}/${itemId}/`,
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
                    $('button[data-infraestructure-qr="delete-qrinfo"]').hide();
                    $('button[data-infraestructure-qr="descargar-qr-info"]').hide();
                    $('button[data-infraestructure-qr="qr-info"]').show();
                    $("#qr-info-infraestructure-container").empty();
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
