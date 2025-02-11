document.addEventListener("DOMContentLoaded", function () {
    const qrInfoContainer = document.getElementById("qr-info-container");
    const qrAccessContainer = document.getElementById("qr-access-container");

    generateQR(vehicle_id, "consulta");
    $('button[data-vehicle-qr="delete-qrinfo"]').hide();
    $('button[data-vehicle-qr="delete-qraccess"]').hide();
    $('button[data-vehicle-qr="qr-info"]').hide();
    $('button[data-vehicle-qr="qr-access"]').hide();
    
    // Función para generar QR
    function generateQR(vehicleId, type) {
        console.log(`Intentando generar QR para el vehículo ${vehicleId}, tipo: ${type}`);
        let url = `/generate_qr/${type}/${vehicleId}/`;

        fetch(url)
            .then((response) => {
                console.log("Respuesta recibida del servidor:", response);
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                console.log("Datos recibidos del servidor:", data);
                if (data.status === "success") {
                    const qrImage = document.createElement("img");
                    qrImage.src = data.qr_url;
                    qrImage.alt = "QR Code";
                    if (type === "info") {
                        qrInfoContainer.innerHTML = "";
                        qrInfoContainer.appendChild(qrImage);
                        $('button[data-vehicle-qr="delete-qrinfo"]').show();
                        $('button[data-vehicle-qr="qr-info"]').hide();
                        $('button[data-vehicle-qr="download-qrinfo"]').show();  
                        $('button[data-vehicle-qr="download-qrinfo"]').attr("data-qr-url", data.qr_url); 
                    } else if (type === "access") {
                        qrAccessContainer.innerHTML = "";
                        qrAccessContainer.appendChild(qrImage);
                        $('button[data-vehicle-qr="delete-qraccess"]').show();
                        $('button[data-vehicle-qr="qr-access"]').hide();
                        $('button[data-vehicle-qr="download-qraccess"]').show();  // Mostrar botón de descarga
                        $('button[data-vehicle-qr="download-qraccess"]').attr("data-qr-url", data.qr_url);
                    }
                    console.log(`QR generado correctamente: ${data.qr_url}`);
                } else if (data.status == "generados") {
                    if (data.qr_url_info != null) {
                        const qrImage_info = document.createElement("img");
                        qrImage_info.src = data.qr_url_info;
                        qrImage_info.alt = "QR Code";
                        qrInfoContainer.innerHTML = "";
                        qrInfoContainer.appendChild(qrImage_info);
                        $('button[data-vehicle-qr="delete-qrinfo"]').show();
                        $('button[data-vehicle-qr="download-qrinfo"]').show();
                    } else {
                        $('button[data-vehicle-qr="download-qrinfo"]').hide();
                        $('button[data-vehicle-qr="qr-info"]').show();
                        

                    }
                    if (data.qr_url_access != null) {
                        const qrImage_access = document.createElement("img");
                        qrImage_access.src = data.qr_url_access;
                        qrImage_access.alt = "QR Code";
                        qrAccessContainer.innerHTML = "";
                        qrAccessContainer.appendChild(qrImage_access);
                        $('button[data-vehicle-qr="delete-qraccess"]').show();
                        $('button[data-vehicle-qr="download-qraccess"]').show();

                    } else {
                        $('button[data-vehicle-qr="download-qraccess"]').hide();
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

    // Función para eliminar QR
    function deleteQR(vehicleId, type) {
        console.log(`Intentando eliminar QR para el vehículo ${vehicleId}, tipo: ${type}`);
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
                console.log("Datos recibidos del servidor:", data);
                if (data.status === "success") {
                    if (type === "info") {
                        qrInfoContainer.innerHTML = "";
                        $('button[data-vehicle-qr="delete-qrinfo"]').hide();
                        $('button[data-vehicle-qr="download-qrinfo"]').hide();  
                        $('button[data-vehicle-qr="qr-info"]').show();
                    } else if (type === "access") {
                        qrAccessContainer.innerHTML = "";
                        $('button[data-vehicle-qr="delete-qraccess"]').hide();
                        $('button[data-vehicle-qr="download-qraccess"]').hide();
                        $('button[data-vehicle-qr="qr-access"]').show();
                    }
                    console.log(`QR eliminado correctamente: ${type}`);
                } else {
                    console.error("Error en la respuesta del servidor:", data.message);
                }
            })
            .catch((error) => {
                console.error("Error al eliminar el QR:", error);
            });
    }

    // Botón para generar QR de información
    document.querySelector('[data-vehicle-qr="qr-info"]').addEventListener("click", function () {
        console.log("Botón 'Generar QR de información' clickeado");
        generateQR(vehicle_id, "info");
    });

    // Botón para eliminar QR de información
    document
        .querySelector('[data-vehicle-qr="delete-qrinfo"]')
        .addEventListener("click", function () {
            console.log("Botón 'Eliminar QR de información' clickeado");
            deleteQR(vehicle_id, "info");
        });

    // Botón para generar QR de acceso
    document.querySelector('[data-vehicle-qr="qr-access"]').addEventListener("click", function () {
        console.log("Botón 'Generar QR de acceso' clickeado");
        generateQR(vehicle_id, "access");
    });

    // Botón para eliminar QR de acceso
    document
        .querySelector('[data-vehicle-qr="delete-qraccess"]')
        .addEventListener("click", function () {
            console.log("Botón 'Eliminar QR de acceso' clickeado");
            deleteQR(vehicle_id, "access");
     });

// Función para manejar la descarga de los Qr
document.querySelectorAll('[data-vehicle-qr^="download-qr"]').forEach((button) => {
    button.addEventListener("click", function () {
        const qrUrl = this.getAttribute("data-qr-url");  
        const a = document.createElement("a");
        a.href = qrUrl;
        a.download = qrUrl.split('/').pop();  
        a.click();  
    });
});



});
