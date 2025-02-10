document.addEventListener('DOMContentLoaded', function() {
    const qrInfoContainer = document.getElementById('qr-info-container');
    const qrAccessContainer = document.getElementById('qr-access-container');

    // Función para generar QR
    function generateQR(vehicleId, type) {
        console.log(`Intentando generar QR para el vehículo ${vehicleId}, tipo: ${type}`); 
        let url = `/generate_qr/${type}/${vehicleId}/`;
        
        fetch(url)
            .then(response => {
                console.log("Respuesta recibida del servidor:", response);  
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Datos recibidos del servidor:", data); 
                if (data.status === 'success') {
                    const qrImage = document.createElement('img');
                    qrImage.src = data.qr_url;
                    qrImage.alt = 'QR Code';
                    if (type === 'info') {
                        qrInfoContainer.innerHTML = '';
                        qrInfoContainer.appendChild(qrImage);
                    } else if (type === 'access') {
                        qrAccessContainer.innerHTML = '';
                        qrAccessContainer.appendChild(qrImage);
                    }
                    console.log(`QR generado correctamente: ${data.qr_url}`);  
                } else {
                    console.error("Error en la respuesta del servidor:", data.message);  
                }
            })
            .catch(error => {
                console.error("Error al generar el QR:", error);  
            });
    }

    // Función para eliminar QR
    function deleteQR(vehicleId, type) {
        console.log(`Intentando eliminar QR para el vehículo ${vehicleId}, tipo: ${type}`);  
        let url = `/delete_qr/${type}/${vehicleId}/`;
        
        fetch(url)
            .then(response => {
                console.log("Respuesta recibida del servidor:", response); 
                if (!response.ok) {
                    throw new Error(`Error en la solicitud: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Datos recibidos del servidor:", data);  
                if (data.status === 'success') {
                    if (type === 'info') {
                        qrInfoContainer.innerHTML = '';
                    } else if (type === 'access') {
                        qrAccessContainer.innerHTML = '';
                    }
                    console.log(`QR eliminado correctamente: ${type}`); 
                } else {
                    console.error("Error en la respuesta del servidor:", data.message);  
                }
            })
            .catch(error => {
                console.error("Error al eliminar el QR:", error); 
            });
    }

    // Botón para generar QR de información
    document.querySelector('[data-vehicle-qr="qr-info"]').addEventListener('click', function() {
        console.log("Botón 'Generar QR de información' clickeado"); 
        generateQR(vehicle_id, 'info');
    });

    // Botón para eliminar QR de información
    document.querySelector('[data-vehicle-qr="delete-qrinfo"]').addEventListener('click', function() {
        console.log("Botón 'Eliminar QR de información' clickeado");  
        deleteQR(vehicle_id, 'info');
    });

    // Botón para generar QR de acceso
    document.querySelector('[data-vehicle-qr="qr-access"]').addEventListener('click', function() {
        console.log("Botón 'Generar QR de acceso' clickeado"); 
        generateQR(vehicle_id, 'access');
    });

    // Botón para eliminar QR de acceso
    document.querySelector('[data-vehicle-qr="delete-qraccess"]').addEventListener('click', function() {
        console.log("Botón 'Eliminar QR de acceso' clickeado");
        deleteQR(vehicle_id, 'access');
    });
});