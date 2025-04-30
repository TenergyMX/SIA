$(document).ready(function () {});

//Función para mostrar la tabla del historial de pagos de servicios
// Función para mostrar la tabla del historial de pagos de servicios
function show_history_payments(serviceIdOrButton) {
    var serviceId;

    // Determinar si el parámetro es un botón (elemento DOM) o un ID directo
    if (typeof serviceIdOrButton === "object" && serviceIdOrButton.nodeType === 1) {
        // Es un elemento DOM (botón)
        var row = $(serviceIdOrButton).closest("tr");
        var data = $("#table_services").DataTable().row(row).data();
        if (!data || !data.id) {
            console.error("No se pudo obtener datos o el ID del servicio no está disponible.");
            return;
        }
        serviceId = data.id;
    } else {
        // Asumimos que es el serviceId directamente
        serviceId = serviceIdOrButton;
    }

    $.ajax({
        url: "/get_payment_history/" + serviceId + "/",
        method: "GET",
        success: function (response) {
            var tbody = $("#table-history-payments tbody");
            tbody.empty();

            // Guardar el serviceId en la tabla para usarlo luego en editPayment
            $("#table-history-payments").data("service-id", serviceId);

            if (response.length > 0) {
                response.forEach(function (payment) {
                    // Determinar el texto que se debe mostrar para el estado de pago
                    var statusText = "";
                    var badgeClass = "";
                    switch (payment.status_payment) {
                        case "pending":
                            statusText = "Pendiente";
                            badgeClass = "bg-outline-info";
                            break;
                        case "upcoming":
                            statusText = "Próximo";
                            badgeClass = "bg-outline-warning";
                            break;
                        case "unpaid":
                            statusText = "No Pagado";
                            badgeClass = "bg-outline-danger";
                            break;
                        case "paid":
                            statusText = "Pagado";
                            badgeClass = "bg-outline-success";
                            break;
                        default:
                            statusText = "Desconocido";
                            badgeClass = "bg-outline-secondary";
                            break;
                    }
                    statusText = `<span class="badge ${badgeClass}">${statusText}</span>`;

                    // Botón para ver comprobante si existe
                    var proofButton = payment.proof_payment
                        ? `<a href="${payment.proof_payment}" target="_blank" class="btn btn-info btn-sm">
                                <i class="fa-solid fa-eye"></i> Ver
                            </a>`
                        : '<span class="text-muted">Sin comprobante</span>';

                    tbody.append(
                        `<tr>
                            <td>${payment.id}</td>
                            <td>${
                                payment.name_service_payment__name_service || "Nombre no disponible"
                            }</td>
                            <td>${proofButton}</td>
                            <td>${payment.total_payment}</td>
                            <td>${payment.next_date_payment}</td>
                            <td>${statusText}</td>
                            <td>
                                <button class="btn btn-warning btn-sm" onclick="editPayment(${
                                    payment.id
                                }, ${serviceId})">  <!-- Pasamos serviceId aquí -->
                                <i class="fa-solid fa-pen-to-square"></i> Editar
                                </button>
                            </td>
                        </tr>`
                    );
                });
            } else {
                tbody.html('<tr><td colspan="7">No hay historial de pagos.</td></tr>');
            }
        },
        error: function () {
            console.error("Error al obtener el historial de pagos.");
        },
    });

    $("#table_services").closest(".card").hide();
    $("#table-history-payments").show();
}

// Función para editar el pago (modificada para aceptar serviceId)
function editPayment(paymentId, serviceId) {
    Swal.fire({
        title: "Editar Pago",
        html: `
            <div class="mb-3">
                <label for="edit-total" class="form-label">Costo total</label>
                <input type="number" step="0.01" class="form-control" id="edit-total" placeholder="Ingrese el costo">
            </div>
            <div class="mb-3">
                <label for="edit-proof" class="form-label">Comprobante de pago</label>
                <input type="file" class="form-control" id="edit-proof" accept="application/pdf, image/*">
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: "Guardar",
        cancelButtonText: "Cancelar",
        preConfirm: () => {
            const total = document.getElementById("edit-total").value;
            const fileInput = document.getElementById("edit-proof");
            const file = fileInput.files[0];

            if (!total && !file) {
                Swal.showValidationMessage("Debe ingresar al menos un valor a actualizar");
                return false;
            }

            const formData = new FormData();
            if (total) formData.append("total_payment", total);
            if (file) formData.append("proof_payment", file);

            return fetch(`/update-payment/${paymentId}/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(response.statusText);
                    }
                    return response.json();
                })
                .catch((error) => {
                    Swal.showValidationMessage(`Error: ${error}`);
                });
        },
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: "¡Éxito!",
                text: "Pago actualizado correctamente",
                icon: "success",
                timer: 1500,
            }).then(() => {
                // Recargar la tabla usando el serviceId que recibimos como parámetro
                show_history_payments(serviceId);
            });
        }
    });
}

// Función para editar el pago (costo y documento)
function editPayment(paymentId, serviceId) {
    Swal.fire({
        title: "Editar Pago",
        html: `
            <div class="mb-3">
                <label for="edit-total" class="form-label">Costo total</label>
                <input type="number" step="0.01" class="form-control" id="edit-total" placeholder="Ingrese el costo">
            </div>
            <div class="mb-3">
                <label for="edit-proof" class="form-label">Comprobante de pago</label>
                <input type="file" class="form-control" id="edit-proof" accept="application/pdf, image/*">
            </div>
        `,
        showCancelButton: true,
        confirmButtonText: "Guardar",
        cancelButtonText: "Cancelar",
        preConfirm: () => {
            const total = document.getElementById("edit-total").value;
            const fileInput = document.getElementById("edit-proof");
            const file = fileInput.files[0];

            if (!total && !file) {
                Swal.showValidationMessage("Debe ingresar al menos un valor a actualizar");
                return false;
            }

            const formData = new FormData();
            if (total) formData.append("total_payment", total);
            if (file) formData.append("proof_payment", file);

            return fetch(`/update-payment/${paymentId}/`, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(response.statusText);
                    }
                    return response.json();
                })
                .catch((error) => {
                    Swal.showValidationMessage(`Error: ${error}`);
                });
        },
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: "¡Éxito!",
                text: "Pago actualizado correctamente",
                icon: "success",
                timer: 1500,
            }).then(() => {
                // Refrescar la tabla después de editar
                show_history_payments(serviceId);
            });
        }
    });
}

// Función auxiliar para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//funcion para el boton de regresar
function show_services_table() {
    $("#table-history-payments").hide();
    $("#table_services").closest(".card").show();
    $("#table_services").DataTable().ajax.reload();
}

function exportToExcel() {
    const table = document.getElementById("table-history-payments");
    const wb = XLSX.utils.table_to_book(table, { sheet: "Historial de Pagos" });
    XLSX.writeFile(wb, "historial_pagos.xlsx");
}
