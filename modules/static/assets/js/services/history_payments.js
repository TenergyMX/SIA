$(document).ready(function() {

});


//Función para mostrar la tabla del historial de pagos de servicios 
function show_history_payments(button) {
    console.log('Botón presionado:', button);
    var row = $(button).closest('tr');
    console.log("fila seleccionada:",row);
    var data = $('#table_services').DataTable().row(row).data();
    console.log("datos recuperados de la fila:",data); 
    if (!data || !data.id) {
        console.error('No se pudo obtener datos o el ID del servicio no está disponible.');
        return;  // Termina la ejecución de la función si no hay datos válidos
    }
    var serviceId = data.id; 
    console.log('ID del servicio:', serviceId);                           

    $.ajax({
        url: '/get_payment_history/' + serviceId + '/',
        method: 'GET',
        success: function(response) {
            console.log("Respuesta recibida:", response);
            var tbody = $('#table-history-payments tbody');
            tbody.empty(); 

            if (response.length > 0) {
                response.forEach(function(payment) {
                    var actionButton = '';
                    

                    if (!payment.proof_payment) {
                        actionButton = `
                            <button class="btn btn-primary" onclick="uploadDocument(${payment.id})">
                                <i class="fa-solid fa-upload"></i> Cargar Comprobante
                            </button>
                        `; 
                    } else if (payment.status_payment) {
                        actionButton = `
                            <a href="/${payment.proof_payment}" target="_blank" class="btn btn-info">
                                <i class="fa-solid fa-eye"></i> Ver Comprobante
                            </a>
                        `;
                    }
                    
                     // Determinar el texto que se debe mostrar para el estado de pago
                     var statusText = '';
                     switch(payment.status_payment) {
                         case 'pending':
                             statusText = 'Pendiente';
                             badgeClass = 'bg-outline-info'; 
                             break;
                         case 'upcoming':
                             statusText = 'Próximo';
                             badgeClass = 'bg-outline-warning';
                             break; 
                         case 'unpaid':
                             statusText = 'No Pagado';
                             badgeClass = 'bg-outline-danger';
                             break;
                         case 'paid':
                             statusText = 'Pagado';
                             badgeClass = 'bg-outline-success';
                             break;
                         default:
                             statusText = 'Desconocido';
                             badgeClass = 'bg-outline-secondary';
                             break;
                     }
                     statusText = `<span class="badge ${badgeClass}">${statusText}</span>`;

                    tbody.append(
                        `<tr>
                            <td>${payment.id}</td>
                            <td>${payment.name_service_payment__name_service || 'Nombre no disponible'}</td>
                            <td>${actionButton}</td>
                            <td>${payment.total_payment}</td>
                            <td>${payment.next_date_payment}</td>
                            <td>${statusText}</td>
                        </tr>`
                    );
                    console.log("Botón de acción generado:", actionButton); 
                });
            } else {
                tbody.html('<tr><td colspan="6">No hay historial de pagos.</td></tr>');
            }
        },
        error: function() {
            console.error('Error al obtener el historial de pagos.');
        }
    });

    $('#table_services').closest('.card').hide();
    $('#table-history-payments').show();
}

function uploadDocument(paymentId) {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'application/pdf, image/*'; 

    fileInput.onchange = function() {
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('proof_payment', file);

            $.ajax({
                url: '/upload-payment-proof/' + paymentId + '/',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Éxito!",
                            text: "Comprobante subido correctamente.",
                            icon: "success",
                            timer: 1500
                        });

                        // Actualizar el botón directamente en la tabla
                        const row = $('#table-history-payments tbody tr').filter(function() {
                            return $(this).find('td').first().text() == paymentId; 
                        });

                        // Cambiar el contenido del enlace del botón temporalmente
                        const loadingHtml = `<button class="btn btn-secondary" disabled>Procesando...</button>`;
                        row.find('td:eq(2)').html(loadingHtml); 

                        // Validar el enlace del comprobante después de un breve retraso
                        setTimeout(function() {
                            validatePaymentLink(paymentId);
                        }, 2000); 

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
                error: function() {
                    alert('Error al subir el comprobante.');
                    Swal.fire({
                        title: "¡Error!",
                        text: "Error al subir el comprobante.",
                        icon: "error",
                        showConfirmButton: false,
                        timer: 1500
                    });
                }
            });
        } else {
            Swal.fire({
                title: "¡Error!",
                text: "No se seleccionó ningún archivo.",
                icon: "error",
                showConfirmButton: false,
                timer: 1500
            });
        }
    };

    fileInput.click();
}

function validatePaymentLink(paymentId) {
    $.ajax({
        url: '/get-proof-payment/' + paymentId + '/',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                // Actualizar el botón con el enlace correcto
                const row = $('#table-history-payments tbody tr').filter(function() {
                    return $(this).find('td').first().text() == paymentId; 
                });

                const linkHtml = `
                    <a href="${response.proof_payment}" target="_blank" class="btn btn-info">
                        <i class="fa-solid fa-eye"></i> Ver Comprobante
                    </a>
                `;
                row.find('td:eq(2)').html(linkHtml); 
                row.find('td:eq(5)').text('Pagado');
            } else {
                console.error('El comprobante aún no está disponible.');
            }
        },
        error: function() {
            console.error('Error al validar el enlace del comprobante.');
        }
    });
}


//funcion para el boton de regresar
function show_services_table() {
    // Ocultar la sección del historial de pagos
    $('#table-history-payments').hide();

    // Mostrar la tabla de servicios
    $('#table_services').closest('.card').show();

    // Recargar la tabla de servicios, si es necesario
    $('#table_services').DataTable().ajax.reload();
}


function exportToExcel() {
    console.log("Función exportToExcel llamada");
    const table = document.getElementById('table-history-payments');

    // Crear un libro de trabajo
    const wb = XLSX.utils.table_to_book(table, { sheet: "Historial de Pagos" });
    const ws = wb.Sheets[wb.SheetNames[0]];

    // Aplicar formato a los encabezados
    const range = XLSX.utils.decode_range(ws['!ref']);
    for (let col = range.s.c; col <= range.e.c; col++) {
        const cell = ws[XLSX.utils.encode_cell({ r: 0, c: col })]; 
        if (cell) {
            cell.s = {
                fill: {
                    fgColor: { rgb: "FFFF00" } // Color de fondo amarillo
                },
                font: {
                    bold: true,
                    color: { rgb: "000000" }, // Color de fuente negro
                    sz: 12, // Tamaño de fuente
                    name: "Arial" // Tipo de fuente
                },
                alignment: {
                    horizontal: "center",
                    vertical: "center"
                },
                border: {
                    top: { style: "thin", color: { rgb: "000000" } },
                    bottom: { style: "thin", color: { rgb: "000000" } },
                    left: { style: "thin", color: { rgb: "000000" } },
                    right: { style: "thin", color: { rgb: "000000" } }
                }
            };
        }
    }

    // Ajustar el ancho de las columnas
    ws['!cols'] = [
        { wpx: 80 },   // Id de pago
        { wpx: 150 },  // Nombre del servicio
        { wpx: 120 },  // Comprobante de Pago
        { wpx: 80 },   // Costo total
        { wpx: 100 },  // Fecha de pago
        { wpx: 100 }   // Estado de pago
    ];

    // Escribir el archivo
    XLSX.writeFile(wb, 'historial_pagos.xlsx');
}



