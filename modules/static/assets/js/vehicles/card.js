function table_card_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log(
        "vehicle_id recibido para mostrar la información en la tabla de la tarjeta:",
        vehicle_id
    );

    $("#table_card_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_card_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Numero de tarjeta ", data: "number_card", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Tipo de tarjeta", data: "type_card", className: "toggleable" },
            { title: "Fecha de vencimiento ", data: "fecha_vencimiento", className: "toggleable" },
            { title: "Ver documento", data: "btn_view", className: "toggleable" },
            {
                title: "Estado",
                data: "status",
                render: function (data, type, row) {
                    var status = (data || "").toLowerCase();

                    if (status === "vigente") {
                        return '<span class="badge bg-success">Vigente</span>';
                    } else if (status === "por vencer") {
                        return '<span class="badge bg-primary">Por vencer</span>';
                    } else if (status === "vencida") {
                        return '<span class="badge bg-danger">Vencida</span>';
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

$(document).on("click", '[data-vehicle-card="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_card_vehicle(vehicle_id);
});

function add_card_vehicle(vehicle_id = null) {
    console.log("estamos en la funcion de agregar tarjeta  de vehiculo");
    var obj_modal = $("#mdl_crud_vehicle_card");
    obj_modal.modal("show");

    get_vehicles_card(vehicle_id);
    get_users();

    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_card .modal-title").text("Agregar Tarjeta de Vehículo");
    $("#form_add_card").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles_card(selectedId = null) {
    console.log("Cargando vehículos para el select de tarjeta de vehículo");
    console.log("Vehículo seleccionado para mostrar en el selectde tarjeta:", selectedId);
    $.ajax({
        url: "/get_vehicles_card/",
        type: "GET",
        success: function (response) {
            var select = $("#vehiculo_card");
            select.empty();
            select.append("<option value='' disabled>Seleccione un vehiculo</option>");

            $.each(response.data, function (index, value) {
                console.log("Comparando:", value.id, selectedId); // <-- Agrega esto

                const selected = String(value.id) === String(selectedId) ? "selected" : "";
                console.log("¿Selected?:", selected); // <-- Y esto
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
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

// Función para agregar una tarjeta
function add_card() {
    var form = $("#form_add_card")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_card");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_card/";
    } else if (action === "update") {
        url = "/edit_card/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_card")[0].reset();
                $("#mdl_crud_vehicle_card").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_card_vehicles").DataTable().ajax.reload();
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
                timer: 1500,
            });
        },
    });
}

// Evento para el botón de editar
$(document).on("click", "[data-vehicle-card='update-card']", function () {
    var cardId = $(this).data("id");
    console.log("ID de la tarjeta a editar:", cardId);
    edit_card(cardId);
});

function edit_card(cardId) {
    $.ajax({
        url: "/edit_card/",
        type: "GET",
        data: { id: cardId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_card");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar Targeta de Vehículo");

                // Cargar datos en el formulario
                form.find('[name="id"]').val(data.id);
                form.find('[name="number_card"]').val(data.number_card);
                form.find('[name="type_card"]').val(data.type_card);
                form.find('[name="fecha_vencimiento"]').val(data.fecha_vencimiento);

                get_vehicles_card(data.vehiculo_id);
                get_users(data.name_user_id);

                form.attr("data-acction", "update");
                modal.modal("show");
            } else {
                Swal.fire("Error", response.message, "error");
            }
        },
        error: function () {
            Swal.fire("Error", "No se pudo obtener la tarjeta", "error");
        },
    });
}

//boton para eliminar tarjetas
$(document).on("click", "[data-vehicle-card='delete-card']", function () {
    delete_card(this);
});

//funcion para eliminar tarjetas
function delete_card(boton) {
    var table = $("#table_card_vehicles").DataTable();
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
                url: "/delete_card/",
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
                    Swal.fire("Error", "Hubo un error al eliminar la tarjeta.", "error");
                },
            });
        }
    });
}
