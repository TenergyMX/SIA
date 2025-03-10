document.addEventListener("DOMContentLoaded", function () {
    console.log("testing reset");
    const qrInfoContainer = document.getElementById("qr-info-container");
    const qrAccessContainer = document.getElementById("qr-access-container");

    generateQR(vehicle_id, "consulta");
    $('button[data-vehicle-qr="delete-qrinfo"]').hide();
    $('button[data-vehicle-qr="delete-qraccess"]').hide();
    $('button[data-vehicle-qr="qr-info"]').hide();
    $('button[data-vehicle-qr="qr-access"]').hide();

    // Función para generar QR
    function generateQR(vehicleId, type) {
        let url = `/generate_qr/${type}/${vehicleId}/`;

        fetch(url)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data.status === "success") {
                    const qrImage = document.createElement("img");
                    qrImage.src = data.qr_url;
                    qrImage.alt = "QR Code";
                    if (type === "info") {
                        qrInfoContainer.innerHTML = "";
                        qrInfoContainer.appendChild(qrImage);
                        $('button[data-vehicle-qr="delete-qrinfo"]').show();
                        $('button[data-vehicle-qr="qr-info"]').hide();
                        $('button[data-vehicle-qr="descargar-qr-info"]').show();
                    } else if (type === "access") {
                        qrAccessContainer.innerHTML = "";
                        qrAccessContainer.appendChild(qrImage);
                        $('button[data-vehicle-qr="delete-qraccess"]').show();
                        $('button[data-vehicle-qr="qr-access"]').hide();
                        $('button[data-vehicle-qr="descargar-qr-access"]').show(); // Mostrar botón de descarga
                    }
                } else if (data.status == "generados") {
                    if (data.qr_url_info != null) {
                        const qrImage_info = document.createElement("img");
                        qrImage_info.src = data.qr_url_info;
                        qrImage_info.alt = "QR Code";
                        qrInfoContainer.innerHTML = "";
                        qrInfoContainer.appendChild(qrImage_info);
                        $('button[data-vehicle-qr="delete-qrinfo"]').show();
                        $('button[data-vehicle-qr="descargar-qr-info"]').show();
                    } else {
                        $('button[data-vehicle-qr="dscargar-qr-info"]').hide();
                        $('button[data-vehicle-qr="qr-info"]').show();
                    }
                    if (data.qr_url_access != null) {
                        const qrImage_access = document.createElement("img");
                        qrImage_access.src = data.qr_url_access;
                        qrImage_access.alt = "QR Code";
                        qrAccessContainer.innerHTML = "";
                        qrAccessContainer.appendChild(qrImage_access);
                        $('button[data-vehicle-qr="delete-qraccess"]').show();
                        $('button[data-vehicle-qr="descargar-qr-access"]').show();
                    } else {
                        $('button[data-vehicle-qr="descargar-qr-access"]').hide();
                        $('button[data-vehicle-qr="qr-access"]').show();
                    }
                } else {
                    console.error("Error en la respuesta del servidor:", data.message);
                }
            })
            .catch((error) => {
                console.error("Error al generar el QR:", error);
            });
    }

    function descargar_qr(tipo) {
        var tipo_qr = tipo;
        $.ajax({
            type: "GET",
            url: "/descargar_qr/",
            data: {
                tipo_qr: tipo_qr,
                id_vehicle: vehicle_id,
            },
            success: function (data) {
                var url_vehicle = data.url_vehicle;
                if (url_vehicle) {
                    var a = document.createElement("a");
                    a.href = url_vehicle;
                    a.download = url_vehicle.substring(url_vehicle.lastIndexOf("/") + 1);
                    console.log(url_vehicle.substring(url_vehicle.lastIndexOf("/") + 1));
                    a.style.display = "none";
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                } else {
                    console.error("Received an invalid or empty URL from the server.");
                }
            },
            error: function (xhr, status, error) {
                console.error("An error occurred while trying to download the QR: ", status, error);
            },
        });
    }

    // Función para eliminar QR
    function deleteQR(vehicleId, type) {
        let url = `/delete_qr/${type}/${vehicleId}/`;

        fetch(url)
            .then((response) => {
                console.log("Respuesta recibida del servidor:", response);
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data.status === "success") {
                    if (type === "info") {
                        qrInfoContainer.innerHTML = "";
                        $('button[data-vehicle-qr="delete-qrinfo"]').hide();
                        $('button[data-vehicle-qr="descargar-qr-info"]').hide();
                        $('button[data-vehicle-qr="qr-info"]').show();
                    } else if (type === "access") {
                        qrAccessContainer.innerHTML = "";
                        $('button[data-vehicle-qr="delete-qraccess"]').hide();
                        $('button[data-vehicle-qr="descargar-qr-access"]').hide();
                        $('button[data-vehicle-qr="qr-access"]').show();
                    }
                } else {
                    console.error("Error en la respuesta del servidor:", data.message);
                }
            })
            .catch((error) => {
                console.error("Error al eliminar el QR:", error);
            });
    }

    // Botón para generar QR de información
    // Botón para generar QR de información
    document.querySelector('[data-vehicle-qr="qr-info"]').addEventListener("click", function () {
        Swal.fire({
            title: "Generando QR...",
            text: "Por favor, espera mientras se crea el código de información.",
            icon: "info",
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        // Simular la generación del QR (ajusta esto según tu lógica real)
        setTimeout(() => {
            generateQR(vehicle_id, "info");

            Swal.fire(
                "¡QR generado!",
                "El código QR de información se ha creado correctamente.",
                "success"
            );
        }, 2000); // Simula un retraso de 2 segundos
    });

    // Botón para descargar QR de información
    document
        .querySelector('[data-vehicle-qr="descargar-qr-info"]')
        .addEventListener("click", function () {
            Swal.fire({
                title: "Descargando QR...",
                text: "Por favor, espera mientras se descarga el código de información.",
                icon: "info",
                allowOutsideClick: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            // Simular la descarga (ajusta esto según tu lógica real)
            setTimeout(() => {
                descargar_qr("info");

                Swal.fire(
                    "¡Descarga completa!",
                    "El código QR de información se ha descargado correctamente.",
                    "success"
                );
            }, 1000); // Espera de 1 segundo antes de mostrar la confirmación
        });

    // Botón para eliminar QR de información
    document
        .querySelector('[data-vehicle-qr="delete-qrinfo"]')
        .addEventListener("click", function () {
            Swal.fire({
                title: "¿Estás seguro?",
                text: "Esta acción eliminará el QR de información.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar",
            }).then((result) => {
                if (result.isConfirmed) {
                    deleteQR(vehicle_id, "info");
                    Swal.fire("Eliminado", "El QR de información ha sido eliminado.", "success");
                }
            });
        });

    // Botón para generar QR de acceso
    document.querySelector('[data-vehicle-qr="qr-access"]').addEventListener("click", function () {
        Swal.fire({
            title: "Generando QR...",
            text: "Por favor, espera mientras se crea el código de acceso.",
            icon: "info",
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            },
        });

        // Simular la generación del QR (ajusta esto según tu lógica real)
        setTimeout(() => {
            generateQR(vehicle_id, "access");

            Swal.fire(
                "¡QR generado!",
                "El código QR de acceso se ha creado correctamente.",
                "success"
            );
        }, 2000); // Simula un retraso de 2 segundos
    });

    // Botón para descargar QR de acceso
    document
        .querySelector('[data-vehicle-qr="descargar-qr-access"]')
        .addEventListener("click", function () {
            Swal.fire({
                title: "Descargando QR...",
                text: "Por favor, espera mientras se descarga el código de acceso.",
                icon: "info",
                allowOutsideClick: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            // Simular la descarga (ajusta esto según tu lógica real)
            setTimeout(() => {
                descargar_qr("access");

                Swal.fire(
                    "¡Descarga completa!",
                    "El código QR de acceso se ha descargado correctamente.",
                    "success"
                );
            }, 1000); // Simula un retraso de 2 segundos
        });

    // Botón para eliminar QR de acceso
    document
        .querySelector('[data-vehicle-qr="delete-qraccess"]')
        .addEventListener("click", function () {
            Swal.fire({
                title: "¿Estás seguro?",
                text: "Esta acción eliminará el QR de entradas y salidas.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar",
            }).then((result) => {
                if (result.isConfirmed) {
                    deleteQR(vehicle_id, "access");
                    Swal.fire("Eliminado", "El QR de información ha sido eliminado.", "success");
                }
            });
        });
});
