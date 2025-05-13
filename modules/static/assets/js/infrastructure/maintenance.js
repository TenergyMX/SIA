$(document).ready(function () {
    $("select-field-infraestructure").select2();
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
            { data: "id" },
            {
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
function get_identifier() {
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
        },
        error: function (error) {
            console.error("Error al cargar los identificadores:", error);
            alert("Hubo un error al cargar los identificadores.");
        },
    });
}

//Función para cargar los nombres de los proveedores han sido registrados
function get_items_providers(selectedProviderId) {
    console.log("se cargan los proveedores");
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
    console.log("Obteniendo acciones de mantenimiento...");
    $.ajax({
        url: "/get_maintenance_actions/",
        type: "GET",
        success: function (response) {
            console.log("Respuesta:", response);

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
                        `<option value="${item.id}" ${selected}>${item.descripcion}</option>`
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
    const data = {
        id: form.find('[name="id"]').val(),
        identifier_id: form.find('[name="identifier_id"]').val(),
        type: form.find('[name="type"]').val(),
        date: form.find('[name="date"]').val(),
        is_new_register: form.find('[name="is_new_register"]').val(),
        provider_id: form.find('[name="provider_id"]').val(),
        cost: form.find('[name="cost"]').val(),
        general_notes: form.find('[name="general_notes"]').val(),
        actions: form.find('[name="actions[]"]').val(),
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

    $.ajax({
        url: "/add_or_update_infrastructure_maintenance/",
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
                item - maintenance - table();
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
