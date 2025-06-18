function table_contract_vehicle(config) {
    const vehicle_id = config?.vehicle?.id;

    if (!vehicle_id) {
        console.warn("No se recibió vehicle_id válido. Se cancela la carga de la tabla.");
        return;
    }

    console.log(
        "vehicle_id recibido para mostrar la información en la tabla de la contrato:",
        vehicle_id
    );

    $("#table_contract_vehicles").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/table_contract_vehicle/",
            type: "GET",
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Vehículo", data: "vehiculo", className: "toggleable" },
            { title: "Tipo de contrato", data: "type_contract", className: "toggleable" },
            { title: "Fecha de contrato", data: "fecha_contract", className: "toggleable" },
            { title: "Ver contrato", data: "btn_view_contract", className: "toggleable" },
            { title: "Fecha finiquito", data: "fecha_finiquito", className: "toggleable" },
            { title: "Carta finiquito", data: "btn_view_letter", className: "toggleable" },
            {
                title: "¿Liquidado?",
                data: "status_modified",
                render: function (data) {
                    return data ? "Sí" : "No";
                },
                className: "toggleable",
            },
            {
                title: "Acciones finiquito",
                data: "btn_status_action",
                orderable: false,
                searchable: false,
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

$(document).on("click", '[data-vehicle-contract="add-item"]', function () {
    let vehicle_id = $(this).data("vehicle-id");
    add_contract_vehicle(vehicle_id);
});

function add_contract_vehicle(vehicle_id = null) {
    console.log("estamos en la funcion de agregar contrato de vehiculo");
    var obj_modal = $("#mdl_crud_vehicle_contract");
    obj_modal.modal("show");

    get_vehicles_contract(vehicle_id);

    // Configurar el modal para agregar
    $("#mdl_crud_vehicle_contract .modal-title").text("Agregar Contrato de Vehículo");
    $("#form_add_contract").attr("data-acction", "create");
}

// Función para cargar los vehiculos en el select
function get_vehicles_contract(selectedId = null) {
    console.log("Cargando vehículos para el select de contrato de vehículo");
    console.log("Vehículo seleccionado para mostrar en el selectde contrato:", selectedId);
    $.ajax({
        url: "/get_vehicles_contract/",
        type: "GET",
        success: function (response) {
            var select = $("#vehiculo_contract");
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

// Función para agregar una tarjeta
function add_contract() {
    var form = $("#form_add_contract")[0];
    var formData = new FormData(form);

    const formulario = document.getElementById("form_add_contract");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_contract/";
    } else if (action === "update") {
        url = "/edit_contract/";
    }

    $.ajax({
        url: url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_contract")[0].reset();
                $("#mdl_crud_vehicle_contract").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#table_contract_vehicles").DataTable().ajax.reload();
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
            console.error("Error al guardar el contrato :", error);
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
$(document).on("click", "[data-vehicle-contract='update-contract']", function () {
    var contractId = $(this).data("id");
    console.log("ID del contrato a editar:", contractId);
    edit_contract(contractId);
});

function edit_contract(contractId) {
    $.ajax({
        url: "/edit_contract/",
        type: "GET",
        data: { id: contractId },
        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl_crud_vehicle_contract");
                const form = modal.find("form");

                modal.find(".modal-title").text("Editar Contrato de Vehículo");

                // Cargar datos en el formulario
                form.find('[name="id"]').val(data.id);
                form.find('[name="type_contract"]').val(data.type_contract);
                form.find('[name="fecha_contract"]').val(data.fecha_contract);
                form.find('[name="fecha_finiquito"]').val(data.fecha_finiquito);

                get_vehicles_contract(data.vehiculo_id);

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
$(document).on("click", "[data-vehicle-contract='delete-contract']", function () {
    delete_contract(this);
});

//funcion para eliminar contrato
function delete_contract(boton) {
    var table = $("#table_contract_vehicles").DataTable();
    var row = $(boton).closest("tr");
    var data = table.row(row).data();

    console.log("Datos de la fila:", data);
    if (!data || !data.id) {
        console.error("No se pudo obtener el ID del contrato.");
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
                url: "/delete_contract/",
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
                    Swal.fire("Error", "Hubo un error al eliminar el contrato.", "error");
                },
            });
        }
    });
}

// Evento para mostrar SweetAlert antes de subir carta finiquito
$(document).on("click", '[data-vehicle-contract="accept"]', function () {
    const contractId = $(this).data("id");

    Swal.fire({
        title: "¿Estás seguro de aceptar este finiquito?",
        text: "Se subirá una carta finiquito y se marcará como liquidado.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, continuar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
    }).then((result) => {
        if (result.isConfirmed) {
            // Abre el modal
            $("#mdl_crud_upload_letter_finiquito").modal("show");
            // Asigna el ID del contrato al input hidden
            $("#form_add_letter_finiquito input[name='id']").val(contractId);
        }
    });
});

function add_letter_finiquito() {
    const form = document.getElementById("form_add_letter_finiquito");
    const formData = new FormData(form);

    $.ajax({
        url: "/upload_letter_finiquito/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
        success: function (response) {
            if (response.success) {
                Swal.fire({
                    title: "¡Guardado!",
                    text: "Carta finiquito registrada correctamente.",
                    icon: "success",
                    timer: 1500,
                });

                $("#mdl_crud_upload_letter_finiquito").modal("hide");
                $("#form_add_letter_finiquito")[0].reset();
                $("#table_contract_vehicles").DataTable().ajax.reload();
            } else {
                Swal.fire("Error", response.message || "No se pudo guardar", "error");
            }
        },
        error: function () {
            Swal.fire("Error", "Error al enviar la carta finiquito", "error");
        },
    });
}

// Evento para cancelar contrato
$(document).on("click", '[data-vehicle-contract="cancel"]', function () {
    const contractId = $(this).data("id");

    Swal.fire({
        title: "¿Estás seguro de cancelar este contrato?",
        text: "Esta acción no se puede deshacer.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, cancelar contrato",
        cancelButtonText: "No, volver",
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/cancel_contract_vehicle/",
                type: "POST",
                data: {
                    id: contractId,
                },
                beforeSend: function (xhr) {
                    xhr.setRequestHeader(
                        "X-CSRFToken",
                        $('input[name="csrfmiddlewaretoken"]').val()
                    );
                },
                success: function (response) {
                    if (response.success) {
                        Swal.fire({
                            title: "Contrato cancelado",
                            text: "El contrato fue cancelado correctamente.",
                            icon: "success",
                            timer: 1500,
                        });

                        $("#table_contract_vehicles").DataTable().ajax.reload();
                    } else {
                        Swal.fire(
                            "Error",
                            response.message || "No se pudo cancelar el contrato",
                            "error"
                        );
                    }
                },
                error: function () {
                    Swal.fire("Error", "Hubo un error al cancelar el contrato", "error");
                },
            });
        }
    });
});
