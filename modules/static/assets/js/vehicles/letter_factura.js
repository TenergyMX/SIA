function table_letter_factura_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log(
        "vehicle_id recibido para mostrar la información de la carta de factura:",
        vehicle_id
    );

    $("#table_letter_factura_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_letter_factura_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Fecha", data: "date", className: "toggleable" },
            { title: "Ver carta de factura", data: "btn_view", className: "toggleable" },
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

$(document).on("click", '[data-vehicle-letter-factura="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_letter_factura_vehicle(vehicle_id);
});

function add_letter_factura_vehicle(vehicle_id = null) {
    console.log("estamos en la funcion de agregar carta de factura de vehiculo");
    var obj_modal = $("#mdl_crud_vehicle_letter_factura");
    obj_modal.modal("show");

    get_vehicles_letter_factura(vehicle_id);

    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_letter_factura .modal-title").text("Agregar Carta de factura de Vehículo");
    $("#form_add_letter_factura").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles_letter_factura(selectedId = null) {
    console.log("Cargando vehículos para el select de carta de factura de vehículo");
    console.log(
        "Vehículo seleccionado para mostrar en el select de carta de facturacion:",
        selectedId
    );
    $.ajax({
        url: "/get_vehicles_letter_factura/",
        type: "GET",
        success: function (response) {
            var select = $("#vehiculo_letter_factura");
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
function add_letter_factura() {
    var form = $("#form_add_letter_factura")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_letter_factura");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_letter_factura/";
    } else if (action === "update") {
        url = "/edit_letter_factura/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_letter_factura")[0].reset();
                $("#mdl_crud_vehicle_letter_factura").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_letter_factura_vehicles").DataTable().ajax.reload();
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
            console.error("Error al guardar la carta de factura :", error);
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
$(document).on("click", "[data-vehicle-letter-factura='update-letter-factura']", function () {
    var letterFacturaId = $(this).data("id");
    console.log("ID de la carta a editar:", letterFacturaId);
    edit_letter_factura(letterFacturaId);
});

function edit_letter_factura(letterFacturaId) {
    $.ajax({
        url: "/edit_letter_factura/",
        type: "GET",
        data: { id: letterFacturaId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_letter_factura");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar Carta de factura de Vehículo");

                // Cargar datos en el formulario
                form.find('[name="id"]').val(data.id);
                form.find('[name="date"]').val(data.date);
                get_vehicles_letter_factura(data.vehiculo_id);

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
$(document).on("click", "[data-vehicle-letter-factura='delete-letter-factura']", function () {
    delete_letter_factura(this);
});

//funcion para eliminar contrato
function delete_letter_factura(boton) {
    var table = $("#table_letter_factura_vehicles").DataTable();
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
                url: "/delete_letter_factura/",
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
                    console.error("Error al eliminar la carta de factura:", error);
                    Swal.fire("Error", "Hubo un error al eliminar el contrato.", "error");
                },
            });
        }
    });
}
