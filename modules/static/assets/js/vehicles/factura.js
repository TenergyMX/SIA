function table_factura_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log("vehicle_id recibido para mostrar la información de la factura:", vehicle_id);

    $("#table_factura_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_factura_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Numero o folio", data: "number", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Fecha de Vencimiento ", data: "fecha_vencimiento", className: "toggleable" },
            { title: "Ver documento", data: "btn_view", className: "toggleable" },
            {
                title: "Estado",
                data: "status",
                render: function (data, type, row) {
                    var status = (data || "").toLowerCase();

                    if (status === "original") {
                        return '<span class="badge bg-success">Original</span>';
                    } else if (status === "refacturación" || status === "refacturacion") {
                        return '<span class="badge bg-danger">Refacturación</span>';
                    } else {
                        return `<span class="badge bg-secondary">${data}</span>`;
                    }
                },
                className: "toggleable",
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

$(document).on("click", '[data-vehicle-factura="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_factura_vehicle(vehicle_id);
});

function add_factura_vehicle(vehicle_id = null) {
    console.log("estamos en la funcion de agregar factura de vehiculo");
    var obj_modal = $("#mdl_crud_vehicle_factura");
    obj_modal.modal("show");

    get_vehicles(vehicle_id);
    get_users();
    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_factura .modal-title").text("Agregar Factura");
    $("#form_add_factura").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles(selectedId = null) {
    $.ajax({
        url: "/get_vehicles/",
        type: "GET",
        success: function (response) {
            var select = $("#vehiculo");
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

// Función para cargar los usuarios en el select
function get_users(selectedUserId) {
    console.log("Cargando usuarios para el select de factura de vehículo");
    console.log("estos son los usuarios:");
    $.ajax({
        url: "/get_users/",
        type: "GET",
        success: function (response) {
            var select = $("#name_user");
            select.html("<option value='' disabled selected>Seleccione un usuario</option>");
            $.each(response.data, function (index, user) {
                var selected = user.id == selectedUserId ? "selected" : "";
                var fullName = user.first_name + " " + user.last_name;
                select.append(`<option value="${user.id}" ${selected}>${fullName}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);
            alert("Hubo un error al cargar los usuarios.");
        },
    });
}

// Función para agregar una factura
function add_factura() {
    var form = $("#form_add_factura")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_factura");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_factura/";
    } else if (action === "update") {
        url = "/edit_factura/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_factura")[0].reset();
                $("#mdl_crud_vehicle_factura").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_factura_vehicles").DataTable().ajax.reload();
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
            console.error("Error al guardar la factura:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                showConfirmButton: false,
            });
        },
    });
}

// Evento para el botón de editar
$(document).on("click", "[data-vehicle-factura='update-factura']", function () {
    var facturaId = $(this).data("id");
    console.log("ID de la factura a editar:", facturaId);
    edit_factura(facturaId);
});

function edit_factura(facturaId) {
    $.ajax({
        url: "/edit_factura/",
        type: "GET",
        data: { id: facturaId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_factura");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar Factura de Vehículo");

                // Cargar datos en el formulario
                modal.find('[name="id"]').val(data.id);

                form.find('[name="id"]').val(data.id);
                form.find('[name="number"]').val(data.number);
                form.find('[name="status"]').val(data.status);
                form.find('[name="vehiculo"]').val(data.vehiculo_id);
                form.find('[name="fecha_vencimiento"]').val(data.fecha_vencimiento);

                get_vehicles(data.vehiculo_id);

                form.attr("data-acction", "update");
                modal.modal("show");
            } else {
                Swal.fire("Error", response.message, "error");
            }
        },
        error: function () {
            Swal.fire("Error", "No se pudo obtener la factura", "error");
        },
    });
}

//boton para eliminar factura
$(document).on("click", "[data-vehicle-factura='delete-factura']", function () {
    delete_factura(this);
});

//funcion para eliminar factura
function delete_factura(boton) {
    var table = $("#table_factura_vehicles").DataTable();
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
                url: "/delete_factura/",
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
                    console.error("Error al eliminar la factura:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la factura.", "error");
                },
            });
        }
    });
}
