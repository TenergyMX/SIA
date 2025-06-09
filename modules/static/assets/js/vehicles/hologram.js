function table_hologram_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log("vehicle_id recibido para mostrar la información del holograma:", vehicle_id);

    $("#table_hologram_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_hologram_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Fecha", data: "date_hologram", className: "toggleable" },
            { title: "Ver holograma", data: "btn_view", className: "toggleable" },
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

$(document).on("click", '[data-vehicle-hologram="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_hologram_vehicle(vehicle_id);
});

function add_hologram_vehicle(vehicle_id = null) {
    var obj_modal = $("#mdl_crud_vehicle_hologram");
    obj_modal.modal("show");

    get_vehicles_hologram(vehicle_id);

    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_hologram .modal-title").text("Agregar holograma de Vehículo Eléctrico");
    $("#form_add_hologram").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles_hologram(selectedId = null) {
    $.ajax({
        url: "/get_vehicles_hologram/",
        type: "GET",
        success: function (response) {
            var select = $("#vehiculo_hologram");
            select.empty();
            select.append("<option value='' disabled>Seleccione un vehiculo</option>");

            $.each(response.data, function (index, value) {
                console.log("Comparando:", value.id, selectedId);

                const selected = String(value.id) === String(selectedId) ? "selected" : "";
                console.log("¿Selected?:", selected);
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (error) {
            console.error("Error al cargar los vehículos:", error);
            alert("Hubo un error al cargar los vehículos.");
        },
    });
}

// Función para agregar una carta de factura
function add_hologram() {
    var form = $("#form_add_hologram")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_hologram");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_hologram/";
    } else if (action === "update") {
        url = "/edit_hologram/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_hologram")[0].reset();
                $("#mdl_crud_vehicle_hologram").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_hologram_vehicles").DataTable().ajax.reload();
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
            console.error("Error al guardar el holograma :", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                showConfirmButton: false,
                timer: 1500,
            });
        },
    });
}

// Evento para el botón de editar
$(document).on("click", "[data-vehicle-hologram='update-hologram']", function () {
    var hologramId = $(this).data("id");
    console.log("ID del holograma a editar:", hologramId);
    edit_hologram(hologramId);
});

function edit_hologram(hologramId) {
    $.ajax({
        url: "/edit_hologram/",
        type: "GET",
        data: { id: hologramId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_hologram");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar holograma de Vehículo");

                // Cargar datos en el formulario
                form.find('[name="id"]').val(data.id);
                form.find('[name="date_hologram"]').val(data.date_hologram);
                get_vehicles_hologram(data.vehiculo_id);

                form.attr("data-acction", "update");
                modal.modal("show");
            } else {
                Swal.fire("Error", response.message, "error");
            }
        },
        error: function () {
            Swal.fire("Error", "No se pudo obtener el contrato", "error");
        },
    });
}

//boton para eliminar contratos
$(document).on("click", "[data-vehicle-hologram='delete-hologram']", function () {
    delete_hologram(this);
});

//funcion para eliminar holograma
function delete_hologram(boton) {
    var table = $("#table_hologram_vehicles").DataTable();
    var row = $(boton).closest("tr");
    var data = table.row(row).data();

    console.log("Datos de la fila:", data);
    if (!data || !data.id) {
        console.error("No se pudo obtener el ID de la carta.");
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
                url: "/delete_hologram/",
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
                    console.error("Error al eliminar el holograma:", error);
                    Swal.fire("Error", "Hubo un error al eliminar el contrato.", "error");
                },
            });
        }
    });
}
