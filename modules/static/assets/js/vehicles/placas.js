// function table_placa_vehicles() {
//     $("#table_placa_vehicles").DataTable({
//         destroy: true,
//         processing: true,
//         ajax: {
//             url: "/table_placa_vehicles/",
//             type: "GET",
//             dataSrc: "data",
//         },
//         columns: [
//             { title: "Id", data: "id", className: "toggleable" },
//             { title: "Placa", data: "plate", className: "toggleable" },
//             { title: "Tipo de placa", data: "type_plate", className: "toggleable" },
//             { title: "Vehiculo", data: "vehiculo", className: "toggleable" },
//             { title: "Fecha de emision", data: "fecha_emision", className: "toggleable" },
//             { title: "Fecha de fin", data: "fecha_vencimiento", className: "toggleable" },
//             { title: "Entidad Emisora", data: "entidad_emisora", className: "toggleable" },
//             { title: "Comentarios", data: "comments", className: "toggleable" },
//             { title: "Ver documento", data: "btn_view", className: "toggleable" },
//             {
//                 title: "Status",
//                 data: "status",
//                 render: function (data, type, row) {
//                     // Verificar si la fecha de vencimiento de la placa ya pasó y el estado no es "Vencido"
//                     var currentDate = new Date();
//                     var placaDate = new Date(row.fecha_vencimiento);
//                     var status = (data || "").toLowerCase(); // Normaliza

//                     // Si la fecha ya pasó y el estado no es "Vigente", marcar como "vencido"
//                     if (placaDate < currentDate && status !== "vigente") {
//                         status = "vencido"; // Marcar  como vencido
//                     }

//                     // Generar el select con el estado actual y la clase 'status-placa'
//                     return `
//                         <select class="form-select form-select-sm d-inline-block float-end action-item status-placa" data-id="${
//                             row.id
//                         }">
//                             <option value="Nuevo" ${
//                                 status === "Nuevo" ? "selected" : ""
//                             }>Nuevo</option>
//                             <option value="Vigente" ${
//                                 status === "vigente" ? "selected" : ""
//                             }>Vigente</option>
//                             <option value="Vencido" ${
//                                 status === "Vencido" ? "selected" : ""
//                             }>Vencida </option>
//                             <option value="Baja" ${
//                                 status === "Baja" ? "selected" : ""
//                             }>Dar de baja</option>
//                         </select>
//                     `;
//                 },
//             },

//             {
//                 title: "Acciones",
//                 data: "btn_action",
//                 render: function (data, type, row) {
//                     return data;
//                 },
//             },
//         ],
//         language: {
//             url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
//         },
//         pageLength: 10,
//     });
// }

function table_placa_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log("vehicle_id recibido para mostrar la información de placa:", vehicle_id);

    $("#table_placa_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_placa_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Placa", data: "plate", className: "toggleable" },
            { title: "Tipo de placa", data: "type_plate", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Fecha de emisión", data: "fecha_emision", className: "toggleable" },
            { title: "Fecha de fin", data: "fecha_vencimiento", className: "toggleable" },
            { title: "Entidad Emisora", data: "entidad_emisora", className: "toggleable" },
            { title: "Comentarios", data: "comments", className: "toggleable" },
            { title: "Ver documento", data: "btn_view", className: "toggleable" },
            {
                title: "Status",
                data: "status",
                render: function (data, type, row) {
                    var currentDate = new Date();
                    var placaDate = new Date(row.fecha_vencimiento);
                    var status = (data || "").toLowerCase();

                    if (placaDate < currentDate && status !== "vigente") {
                        status = "vencido";
                    }

                    return `
                        <select class="form-select form-select-sm d-inline-block float-end action-item status-placa" data-id="${
                            row.id
                        }">
                            <option value="Nuevo" ${
                                status === "nuevo" ? "selected" : ""
                            }>Nuevo</option>
                            <option value="Vigente" ${
                                status === "vigente" ? "selected" : ""
                            }>Vigente</option>
                            <option value="Vencido" ${
                                status === "vencido" ? "selected" : ""
                            }>Vencida</option>
                            <option value="Baja" ${
                                status === "baja" ? "selected" : ""
                            }>Dar de baja</option>
                        </select>
                    `;
                },
            },
            {
                title: "Acciones",
                data: "btn_action",
                render: function (data) {
                    return data;
                },
            },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10,
    });
}

$(document).on("click", '[data-vehicle-placa="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_placa_vehicle(vehicle_id);
});

function add_placa_vehicle(vehicle_id = null) {
    console.log("estamos en la funcion de agregar placa");
    var obj_modal = $("#mdl_crud_vehicle_placa");
    obj_modal.modal("show");

    get_vehicles_placa(vehicle_id);

    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_placa .modal-title").text("Agregar Placa");
    $("#form_add_placa").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles_placa(selectedId = null) {
    $.ajax({
        url: "/get_vehicles_placa/",
        type: "GET",
        success: function (response) {
            var select = $("#fuel_vehicle_id");
            select.empty();
            select.append("<option value='' disabled>Seleccione un vehiculo</option>");

            $.each(response.data, function (index, value) {
                const selected = value.id === selectedId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });

            if (selectedId) {
                select.val(selectedId).trigger("change");
            }
        },
        error: function (error) {
            console.error("Error al cargar los vehículos:", error);
            alert("Hubo un error al cargar los vehículos.");
        },
    });
}

// Función para agregar una placa
function add_placa() {
    var form = $("#form_add_placa")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_placa");
    const action = formulario.getAttribute("data-acction");

    if (action === "create") {
        url = "/add_placa/";
    } else if (action === "update") {
        url = "/edit_placa/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_placa")[0].reset();
                $("#mdl_crud_vehicle_placa").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_placa_vehicles").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    showConfirmButton: false,
                });
            }
        },
        error: function (error) {
            console.error("Error al guardar la placa:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                showConfirmButton: false,
            });
        },
    });
}

// Manejar el cambio de estado en el select con la clase 'status-placa'
$(document).on("change", ".status-placa", function () {
    var newStatus = $(this).val();
    var id = $(this).data("id");

    Swal.fire({
        title: "¿Estás seguro?",
        text: `Estás a punto de cambiar el estado a "${newStatus}".`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, cambiar",
        cancelButtonText: "Cancelar",
    }).then((result) => {
        if (result.isConfirmed) {
            update_status_placa(id, newStatus);
        } else {
            // Restaurar el valor anterior si se cancela
            var currentStatus = $(this).find("option:selected").text();
            $(this).val(currentStatus);
        }
    });
});

// Función para enviar la solicitud AJAX y actualizar el estado
function update_status_placa(id, newStatus) {
    $.ajax({
        url: "/update_status_placa/",
        method: "POST",
        data: {
            id: id,
            status: newStatus,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
        },
        success: function (response) {
            Swal.fire("Actualizado", `El estado ha sido cambiado a "${newStatus}".`, "success");
            // Recargar la tabla o actualizar la fila según sea necesario
            $("#example").DataTable().ajax.reload();
        },
        error: function (xhr, status, error) {
            Swal.fire("Error", "Ocurrió un error al intentar actualizar el estado.", "error");
        },
    });
}

// Evento para el botón de editar
$(document).on("click", "[data-vehicle-placa='update-placa']", function () {
    var placaId = $(this).data("id");
    console.log("ID de la placa a editar:", placaId);
    edit_placa(placaId);
});

function edit_placa(placaId) {
    $.ajax({
        url: "/edit_placa/",
        type: "GET",
        data: { id: placaId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_placa");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar Placa de Vehículo");

                // Cargar datos en el formulario
                modal.find('[name="id"]').val(data.id);

                form.find('[name="id"]').val(data.id);
                form.find('[name="placa_vehicle"]').val(data.plate);
                form.find('[name="plate_type"]').val(data.type_plate);
                form.find('[name="start_date"]').val(data.fecha_emision);
                form.find('[name="end_date"]').val(data.fecha_vencimiento);
                form.find('[name="entity_plate"]').val(data.entidad_emisora);
                form.find('[name="comments"]').val(data.comments);
                console.log("Vehículo ID a seleccionar:", data.vehiculo_id);

                get_vehicles_placa(data.vehiculo_id);

                form.attr("data-acction", "update");
                modal.modal("show");
            } else {
                Swal.fire("Error", response.message, "error");
            }
        },
        error: function () {
            Swal.fire("Error", "No se pudo obtener la placa", "error");
        },
    });
}

//boton para eliminar placas
$(document).on("click", "[data-vehicle-placa='delete-placa']", function () {
    delete_placa(this);
});

//funcion para eliminar placas
function delete_placa(boton) {
    var table = $("#table_placa_vehicles").DataTable();
    var row = $(boton).closest("tr");
    var data = table.row(row).data();

    console.log("Datos de la fila:", data);
    if (!data || !data.id) {
        console.error("No se pudo obtener el ID de la placa.");
        return;
    }

    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, eliminar",
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/delete_placa/",
                type: "POST",
                data: { id: data.id },
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
                        });

                        setTimeout(function () {
                            table.ajax.reload();
                        }, 1500);
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function (error) {
                    console.error("Error al eliminar la placa:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la placa.", "error");
                },
            });
        }
    });
}
