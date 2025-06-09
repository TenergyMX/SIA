function table_carnet_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log("vehicle_id recibido para mostrar la información del carnet:", vehicle_id);

    $("#table_carnet_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_carnet_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Fecha", data: "date_carnet", className: "toggleable" },
            { title: "Ver caarnet", data: "btn_view", className: "toggleable" },
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

$(document).on("click", '[data-vehicle-carnet="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_carnet_vehicle(vehicle_id);
});

function add_carnet_vehicle(vehicle_id = null) {
    var obj_modal = $("#mdl_crud_vehicle_carnet");
    obj_modal.modal("show");

    get_vehicles_carnet(vehicle_id);

    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_carnet .modal-title").text("Agregar Carnet de Vehículo");
    $("#form_add_carnet").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles_carnet(selectedId = null) {
    $.ajax({
        url: "/get_vehicles_carnet/",
        type: "GET",
        success: function (response) {
            var select = $("#vehiculo_carnet");
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
function add_carnet() {
    var form = $("#form_add_carnet")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_carnet");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_carnet/";
    } else if (action === "update") {
        url = "/edit_carnet/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_carnet")[0].reset();
                $("#mdl_crud_vehicle_carnet").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_carnet_vehicles").DataTable().ajax.reload();
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
            console.error("Error al guardar el carnet :", error);
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
$(document).on("click", "[data-vehicle-carnet='update-carnet']", function () {
    var carnetId = $(this).data("id");
    console.log("ID del carnet a editar:", carnetId);
    edit_carnet(carnetId);
});

function edit_carnet(carnetId) {
    $.ajax({
        url: "/edit_carnet/",
        type: "GET",
        data: { id: carnetId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_carnet");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar Carnet de Servicios de Vehículo");

                // Cargar datos en el formulario
                form.find('[name="id"]').val(data.id);
                form.find('[name="date_carnet"]').val(data.date_carnet);
                get_vehicles_carnet(data.vehiculo_id);

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

//boton para eliminar carnet
$(document).on("click", "[data-vehicle-carnet='delete-carnet']", function () {
    delete_carnet(this);
});

//funcion para eliminar carnet
function delete_carnet(boton) {
    var table = $("#table_carnet_vehicles").DataTable();
    var row = $(boton).closest("tr");
    var data = table.row(row).data();

    console.log("Datos de la fila:", data);
    if (!data || !data.id) {
        console.error("No se pudo obtener el ID del carnet.");
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
                url: "/delete_carnet/",
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
                    console.error("Error al eliminar el carnet:", error);
                    Swal.fire("Error", "Hubo un error al eliminar el carnet.", "error");
                },
            });
        }
    });
}
