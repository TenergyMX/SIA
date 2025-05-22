$(document).ready(function () {
    $(".select-field-infraestructure").select2();
    table_item_maintenance();
});

function table_item_maintenance() {
    $("#item-maintenance-table").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_item_maintenance/",
            type: "GET",
            dataSrc: "data",
        },
        columns: [
            { title: "Id", data: "id", className: "toggleable" },
            { title: "Identificador", data: "identifier__identifier", className: "toggleable" },
            { title: "Nombre", data: "identifier__item__name", className: "toggleable" },
            { title: "Tipo de Mantenimiento", data: "type_maintenance", className: "toggleable" },
            { title: "Fecha", data: "date", className: "toggleable" },
            { title: "Costo", data: "cost", className: "toggleable" },
            { title: "Proveedor", data: "provider__name", className: "toggleable" },
            {
                title: "Status",
                data: "status",
                render: function (data, type, row) {
                    // Verificar si la fecha ya pasó y el estado no es "Proceso" o "Finalizado"
                    var currentDate = new Date();
                    var maintenanceDate = new Date(row.date);
                    var status = data;

                    // Si la fecha ya pasó y el estado no es "Proceso" o "Finalizado", marcar como "Retrasado"
                    if (
                        maintenanceDate < currentDate &&
                        status !== "Proceso" &&
                        status !== "Finalizado"
                    ) {
                        status = "Retrasado"; // Marcamos como Retrasado
                    }

                    // Generar el select con el estado actual y la clase 'status-mantenance'
                    return `
                        <select class="form-select form-select-sm d-inline-block float-end action-item status-mantenance" data-id="${
                            row.id
                        }">
                            <option value="Nuevo" ${
                                status === "Nuevo" ? "selected" : ""
                            }>Nuevo</option>
                            <option value="Programado" ${
                                status === "Programado" ? "selected" : ""
                            }>Programado</option>
                            <option value="Proceso" ${
                                status === "Proceso" ? "selected" : ""
                            }>Proceso</option>
                            <option value="Reagendado" ${
                                status === "Reagendado" ? "selected" : ""
                            }>Reagendado</option>
                            <option value="Finalizado" ${
                                status === "Finalizado" ? "selected" : ""
                            }>Finalizado</option>
                            <option value="Retrasado" ${
                                status === "Retrasado" ? "selected" : ""
                            }>Retrasado</option>
                        </select>
                    `;
                },
            },

            {
                title: "Acciones",
                data: "btn_action",
                render: function (data, type, row) {
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

// Función para cargar los identificadores en el select
function get_identifier(selectedId = null) {
    $.ajax({
        url: "/get_identifier/",
        type: "GET",
        success: function (response) {
            var select = $("#identifier_id");
            select.html(null);
            select.append(
                "<option value='' disabled selected>Seleccione un identificador</option>"
            );
            $.each(response.data, function (index, value) {
                var selected = "";
                select.append(
                    `<option value="${value.id}" ${selected}>${value.identifier}</option>`
                );
            });

            if (selectedId) {
                select.val(selectedId).trigger("change");
            }
        },
        error: function (error) {
            console.error("Error al cargar los identificadores:", error);
            alert("Hubo un error al cargar los identificadores.");
        },
    });
}

//Función para cargar los nombres de los proveedores han sido registrados
function get_items_providers(selectedProviderId) {
    $.ajax({
        url: "/get_items_providers/",
        type: "GET",
        success: function (response) {
            var select = $("#provider_id");
            select.html("<option value='' disabled selected>Seleccione proveedor</option>");
            $.each(response.data, function (index, provider) {
                var selected = provider.id == selectedProviderId ? "selected" : "";
                select.append(
                    `<option value="${provider.id}" ${selected}>${provider.name}</option>`
                );
            });
            select.val(selectedProviderId);
        },
        error: function (error) {
            console.error("Error al cargar los proveedores:", error);
            alert("Hubo un error al cargar los proveedores.");
        },
    });
}

// Función para mostrar el modal para agregar mantenimientos
function add_item_maintenance(button) {
    var obj_modal = $("#mdl-crud-infrastructure-maintenance");
    const formulario = document.getElementById("form-crud-infrastructure-maintenance");
    formulario.setAttribute("data-acction", "create");

    obj_modal.modal("show");

    var row = $(button).closest("tr");
    // var data = $('#item-maintenance-table').DataTable().row(row).data();

    get_identifier();
    get_items_providers();

    // Tipo de mantenimiento
    $('select[name="type"]')
        .off("change")
        .on("change", function () {
            const tipoSeleccionado = $(this).val();
            get_maintenance_actions(tipoSeleccionado);
        });

    // Cargar las acciones del tipo por defecto (al abrir el modal)
    const tipoInicial = $('select[name="type"]').val();

    get_maintenance_actions(tipoInicial);
    obj_modal.find("[name='action[]']").select2();
}

function get_maintenance_actions(tipoSeleccionado) {
    $.ajax({
        url: "/get_maintenance_actions/",
        type: "GET",
        success: function (response) {
            const select = $("#select-field-infraestructure");
            const previouslySelected = select.val() || [];
            // Limpiar opciones actuales
            select.empty();
            if (!response.data || response.data.length === 0) {
                select.append(`<option disabled selected>No hay acciones disponibles</option>`);
                return;
            }

            let itemsToDisplay = [];

            // Si hay tipo seleccionado, filtrar por él
            if (tipoSeleccionado) {
                const grupo = response.data.find((item) => item.tipo === tipoSeleccionado);
                if (grupo && grupo.items) {
                    itemsToDisplay = grupo.items;
                }
            } else {
                // Si no hay tipo seleccionado, mostrar todos los items de todos los grupos
                response.data.forEach((grupo) => {
                    if (grupo.items) {
                        itemsToDisplay = itemsToDisplay.concat(grupo.items);
                    }
                });
            }

            // Agregar opciones al select
            if (itemsToDisplay.length > 0) {
                itemsToDisplay.forEach((item) => {
                    const selected = previouslySelected.includes(item.id.toString())
                        ? "selected"
                        : "";
                    select.append(
                        `<option value="${item.descripcion}" ${selected}>${item.descripcion}</option>`
                    );
                });
            } else {
                select.append(`<option disabled selected>No hay acciones para mostrar</option>`);
            }

            // Agregar opción para "nuevo"
            select.append(`<option value="new">Agregar nuevo mantenimiento</option>`);

            // Aplicar las selecciones anteriores
            select.val(previouslySelected).trigger("change");

            // Manejar la selección de "nuevo"
            select.off("change").on("change", function () {
                const selectedValues = $(this).val();
                if (selectedValues && selectedValues.includes("new")) {
                    $("#mdl-crud-option-maintenance-item").modal("show");
                    // Eliminar "new" de las seleccionadas
                    const cleanedValues = selectedValues.filter((v) => v !== "new");
                    $(this).val(cleanedValues).trigger("change");
                }
            });

            select.select2({
                placeholder: "Seleccione acciones",
                width: "100%",
                dropdownParent: $("#mdl-crud-infrastructure-maintenance"),

                search: true,
                closeOnSelect: false,
            });

            select.on("change", function (e) {
                setTimeout(() => {
                    $(
                        ".select2-container--default .select2-selection--multiple .select2-selection__choice"
                    ).css({
                        "background-color": "var(--primary-color)",
                        border: "1px solid var(--primary-color)",
                        color: "#fff",
                    });
                }, 0);
            });
        },

        error: function (error) {
            console.error("Error al cargar acciones de mantenimiento:", error);
        },
    });
}

$("#form_option_maintenance").on("submit", function (e) {
    e.preventDefault();

    const optionName = $("#option_maintenance_name").val();
    const tipoSeleccionado = $('select[name="type"]').val();

    if (!optionName.trim()) {
        Swal.fire({
            title: "¡Advertencia!",
            text: "Debe ingresar un nombre válido.",
            icon: "warning",
            timer: 1500,
        });
        return;
    }

    $.ajax({
        url: "/add_new_maintenance_option/",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            option_maintenance_name: optionName,
            maintenance_type: tipoSeleccionado,
        }),
        headers: {
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            if (response.status === "success") {
                $("#form_option_maintenance")[0].reset();
                $("#mdl-crud-option-maintenance-item").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                // Recargar las opciones del tipo de mantenimiento actualizado
                get_maintenance_actions(tipoSeleccionado);
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    showConfirmButton: false,
                });
            }
        },
        error: function (xhr) {
            Swal.fire({
                title: "¡Error!",
                text: "Error al guardar la nueva opción.",
                icon: "error",
                showConfirmButton: false,
            });
            console.error(xhr);
        },
    });
});

$("#mdl-crud-infrastructure-maintenance form").on("submit", function (e) {
    e.preventDefault();

    const form = $(this);

    actions2 = {};
    form.find('[name="actions[]"]')
        .val()
        .forEach((opcion) => {
            actions2[opcion] = "MALO";
        });

    const data = {
        id: form.find('[name="id"]').val(),
        identifier_id: form.find('[name="identifier_id"]').val(),
        type: form.find('[name="type"]').val(),
        date: form.find('[name="date"]').val(),
        is_new_register: form.find('[name="is_new_register"]').val(),
        provider_id: form.find('[name="provider_id"]').val(),
        cost: form.find('[name="cost"]').val(),
        general_notes: form.find('[name="general_notes"]').val(),
        actions: actions2,
    };
    if (!data.identifier_id || !data.type || !data.date || !data.provider_id || !data.cost) {
        Swal.fire({
            title: "¡Advertencia!",
            text: "Por favor complete todos los campos obligatorios.",
            icon: "warning",
            timer: 1800,
        });
        return;
    }
    const formulario = document.getElementById("form-crud-infrastructure-maintenance");
    const action = formulario.getAttribute("data-acction");
    if (action === "create") {
        url = "/add_infrastructure_maintenance/";
    } else if (action === "update") {
        url = "/update_infrastructure_maintenance/";
    }
    $.ajax({
        url: url,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),
        headers: {
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (response) {
            if (response.status === "success") {
                form[0].reset();
                $("#mdl-crud-infrastructure-maintenance").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#item-maintenance-table").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr) {
            Swal.fire({
                title: "¡Error!",
                text: "Ocurrió un error al guardar el mantenimiento.",
                icon: "error",
            });
            console.error(xhr);
        },
    });
});

$(document).on("click", "[data-maintenance-action='update-maintenance']", function () {
    var maintenanceId = $(this).data("id");
    edit_item_maintenance(maintenanceId);
});

function edit_item_maintenance(maintenanceId) {
    $.ajax({
        url: "/get_infrastructure_maintenance_detail/",
        type: "GET",
        data: { id: maintenanceId },

        success: function (response) {
            if (response.status === "success") {
                const data = response.data;
                const modal = $("#mdl-crud-infrastructure-maintenance");
                const form = modal.find("form");

                // Cargar datos en el formulario
                modal.find('[name="id"]').val(data.id);
                form.find('[name="id"]').val(data.id);
                form.find('[name="date"]').val(data.date);
                form.find('[name="cost"]').val(data.cost);
                form.find('[name="general_notes"]').val(data.general_notes);

                // Cargar datos relacionados
                get_identifier(data.identifier_id);
                get_items_providers(data.provider_id);

                form.find('[name="type"]').val(data.type_maintenance).trigger("change");
                get_maintenance_actions(data.type_maintenance);

                setTimeout(function () {
                    $("#select-field-infraestructure").val(data.actions).trigger("change");
                }, 500);

                const formulario = document.getElementById("form-crud-infrastructure-maintenance");
                formulario.setAttribute("data-acction", "update");

                modal.modal("show");
            } else {
                Swal.fire("Error", response.message, "error");
            }
        },

        error: function () {
            Swal.fire("Error", "No se pudo obtener el mantenimiento", "error");
        },
    });
}

$(document).on("click", "[data-maintenance-action='delete-maintenance']", function () {
    delete_maintenance_infraestructure(this);
});

// Función para eliminar un registro de mantenimiento
function delete_maintenance_infraestructure(boton) {
    var row = $(boton).closest("tr");
    var data = $("#item-maintenance-table").DataTable().row(row).data();
    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, elimínalo!",
    }).then((result) => {
        if (result.isConfirmed) {
            // Si el usuario confirma la eliminación, hacer la solicitud AJAX
            $.ajax({
                url: "/delete_maintenance_infraestructure/",
                type: "POST",
                data: {
                    id: data.id,
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
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500,
                        }).then(() => {
                            // Recargar la tabla después de la eliminación exitosa
                            $("#item-maintenance-table").DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function (error) {
                    console.error("Error al eliminar la categoría:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la categoría.", "error");
                },
            });
        }
    });
}

// $(document).on("click", "[data-maintenance-action='view-maintenance']", function () {
//     let id = $(this).data("id");

//     $.ajax({
//         url: `/get_maintenance_detail/${id}/`,
//         type: "GET",
//         success: function (response) {
//             if (response.success) {
//                 mostrarDetallesInfraestructura(response.data);
//             }
//         },
//         error: function () {
//             alert("Error al obtener los detalles del mantenimiento.");
//         },
//     });
// });

// Manejar el cambio de estado en el select con la clase 'status-mantenance'
$(document).on("change", ".status-mantenance", function () {
    var newStatus = $(this).val();
    var id = $(this).data("id");

    // Mostrar el SweetAlert para confirmar el cambio
    Swal.fire({
        title: "¿Estás seguro?",
        text: `Estás a punto de cambiar el estado a "${newStatus}".`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, cambiar",
        cancelButtonText: "Cancelar",
    }).then((result) => {
        if (result.isConfirmed) {
            // Llamar a la función para actualizar el estado
            update_status_mantenance(id, newStatus);
        } else {
            // Restaurar el valor anterior si se cancela
            var currentStatus = $(this).find("option:selected").text();
            $(this).val(currentStatus);
        }
    });
});

// Función para enviar la solicitud AJAX y actualizar el estado
function update_status_mantenance(id, newStatus) {
    $.ajax({
        url: "/update_status_mantenance/",
        method: "POST",
        data: {
            id: id,
            status: newStatus,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
        },
        success: function (response) {
            // Aquí puedes manejar la respuesta si es necesario
            Swal.fire("Actualizado", `El estado ha sido cambiado a "${newStatus}".`, "success");
            // Recargar la tabla o actualizar la fila según sea necesario
            $("#example").DataTable().ajax.reload();
        },
        error: function (xhr, status, error) {
            // Manejar error en caso de que la solicitud falle
            Swal.fire("Error", "Ocurrió un error al intentar actualizar el estado.", "error");
        },
    });
}

//boton de regresar
$(document).on("click", '[data-sia-infraestructure-maintenance="show-info"]', function () {
    hideShow("#v-deliverie-pane .info-details", "#v-deliverie-pane .info");
});

// Mostrar detalles de mantenimiento al hacer clic en el botón "Ver Mantenimiento"
$(document).on("click", '[data-maintenance-action="view-maintenance"]', function () {
    const maintenanceId = $(this).data("id");
    $.get(`/ajax/infra-info-by-maintenance/${maintenanceId}/`, function (response) {
        if (response.detail_html && response.maintenance_html) {
            // Cargar info en los bloques correspondientes
            $(".info-details .col-md-4").html(response.detail_html);
            $(".info-details .col-md-8").find(".card.mb-3").next().remove(); // Limpia mantenimiento anterior
            $(".info-details .col-md-8").append(response.maintenance_html);
            hideShow("#v-deliverie-pane .info", "#v-deliverie-pane .info-details");
        } else {
            alert("No se pudo cargar la información del mantenimiento.");
        }
    });
});

function update_status_man() {
    var url = "/update_infraestructure_status_man/";
    var datos = new FormData($("#form_maintenance_infraestructure_info")[0]);
    datos.append("csrfmiddlewaretoken", $('input[name="csrfmiddlewaretoken"]').val());
    Swal.fire({
        title: "Estás seguro?",
        text: "Solo se podra guardar cambios una sola vez",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Si, adelante",
    }).then((result) => {
        if (!result.isConfirmed) return;
        let actionsformat2 = { action: [] };
        $("#form_maintenance_infraestructure_info .action-item").each(function () {
            let name = $(this).attr("name");
            let value = $(this).val();
            actionsformat2["action"].push({ name: name, value: value });
        });
        datos.append("actions", JSON.stringify(actionsformat2));
        $.ajax({
            type: "POST",
            url: url,
            data: datos,
            processData: false,
            contentType: false,
            success: function (response) {
                var message = response.message || "Ocurrió un error inesperado";
                if (response.status == "error") {
                    Swal.fire("Error", response.message, "error");
                    return;
                } else if (response.status == "warning") {
                    Swal.fire("Advertencia", response.message, "warning");
                    return;
                } else if (response.status != "success") {
                    Swal.fire("Oops", message, "error");
                    return;
                }
                message = response.message || "Se han guardado los datos con éxito";
                Swal.fire("Éxito", message, "success");
                $("#form_maintenance_infraestructure_info .action-item").attr("disabled", true);
            },
            error: function (xhr, status, error) {
                let errorMessage = "Ocurrió un error inesperado";
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }
                Swal.fire("Error", errorMessage, "error");
            },
        });
    });
}

function handleFileChange(input) {
    const files = input.files;
    if (files.length > 0) {
        const file = files[0];

        // Validar si es una imagen
        if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = function (e) {
                $("#preview_comprobante").attr("src", e.target.result).show();
            };
            reader.readAsDataURL(file);
        } else {
            $("#preview_comprobante").hide().attr("src", "");
            alert("Por favor selecciona un archivo de imagen válido.");
        }
        $("#form_maintenance_infraestructure_info .action-item").removeAttr("disabled");
    } else {
        $("#form_maintenance_infraestructure_info .action-item").each(function () {
            $(this).find("option:first").prop("selected", true);
        });
        $("#form_maintenance_infraestructure_info .action-item").attr("disabled", true);
    }
}
