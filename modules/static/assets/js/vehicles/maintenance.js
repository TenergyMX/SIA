class VehiclesMaintenance {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            infoCard: {
                id: null,
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: function () {
                        return "/get_vehicles_info/";
                    },
                    data: function () {
                        return {
                            vehicle_id: defaultOptions.info.id || defaultOptions.info.vehicle_id,
                        };
                    },
                    reload: function () {
                        $.ajax({
                            type: "GET",
                            url: "/get_vehicle_info/",
                            data: {
                                vehicle_id: self.infoCard.vehicle.id,
                            },
                            beforeSend: function () {},
                            success: function (response) {
                                var card = $(".card-vehicle-info");
                                $.each(response["data"], function (index, value) {
                                    card.find(`[data-key-value="${index}"]`)
                                        .html(value)
                                        .removeClass();
                                    card.find(`[name='${index}']`).val(value);
                                });
                            },
                            error: function (xhr, status, error) {},
                        });
                    },
                },
            },
            table: {
                id: "#table_maintenance",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_maintenance/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehicle__name" },
                    { title: "Mantenimiento", data: "type" },
                    { title: "Fecha", data: "date" },
                    { title: "Kilometraje", data: "mileage" },
                    { title: "Costos", data: "cost" },
                    { title: "Proveedor", data: "provider__name" },
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

                            // Generar el select con el estado actual y la clase 'status-man'
                            return `
                                <select class="form-select form-select-sm d-inline-block float-end action-item status-man" data-id="${
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
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: {},
            provider: {},
        };

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };

            if (self.table.vehicle.id) {
                self.table.ajax.url = "/get_vehicle_maintenance/";
                self.table.ajax.data = {
                    vehicle_id: self.table.vehicle.id,
                };

                // Buscar el índice del elemento que quieres eliminar
                let indexToRemove = self.table.columns.findIndex(function (column) {
                    return column.title === "Vehiculo" && column.data === "vehicle__name";
                });

                // Si se encontró el índice, eliminar el elemento del array
                if (indexToRemove !== -1) {
                    self.table.columns.splice(indexToRemove, 1);
                }
            }
        }

        if (options.vehicle) {
            self.vehicle = { ...defaultOptions.vehicle, ...options.vehicle };
        }

        if (options.vehicle && options.table) {
            self.vehicle.data.id = self.table.vehicle.id ? self.table.vehicle.id : null;
            self.vehicle.data.vehicle_id = self.table.vehicle.id ? self.table.vehicle.id : null;
        }

        if (options.provider) {
            self.provider = { ...defaultOptions.provider, ...options.provider };
        }

        self.init();
    }

    init() {
        const self = this;
        var obj_modal = $("#mdl_crud_maintenance");

        if (self.table) {
            self.tbl_maintenance = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: self.table.ajax.data,
                },
                columns: self.table.columns,
                order: [
                    [0, "desc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
            });

            delete self.table;
        }

        if (self.vehicle) {
        }

        if (self.vehicle.data.id) {
            $('#mdl_crud_maintenance [name="vehicle_id"]').hide();
            $('#mdl_crud_maintenance [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_maintenance [name="vehicle_id"]').show();
            $('#mdl_crud_maintenance [name="vehicle__name"]').hide();
        }

        self.setupEventHandlers();
        self.loadApi();
        obj_modal.find("[name='actions[]']").select2();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_maintenance");
        var obj_modal_option = $("#mdl-crud-option-maintenance");

        var table_kilometer = $("#table_maintenance_kilometer").DataTable({
            ajax: {
                url: "/get_vehicle_maintenance_kilometer/",
                dataSrc: "data",
                data: {
                    id: self.vehicle.id,
                },
            },
            columns: [
                { data: "kilometer", title: "Kilometraje", orderable: false },
                { data: "acciones", title: "Acciones", orderable: false },
            ],
            order: [],
            language: {
                url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
            },
        });

        var obj_modal_kilometer = $("#mdl_crud_maintenance_kilometer");
        $(document).on("click", "[data-vehicle-maintenance]", function (e) {
            var obj = $(this);
            var option = obj.data("vehicle-maintenance");
            switch (option) {
                case "add-vehicle-kl":
                    obj_modal_kilometer.modal("show");
                    break;
                default:
                    console.log(`opción desconocida ${option}`);
                    break;
            }
        });

        obj_modal_kilometer.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var datos = new FormData(this);
            var id = vehicle_id;
            var url = "/add_vehicle_kilometer/";

            if (submit == "delete") {
                id = $("button[type='submit']:focus", this).attr("data-vehiculo-id");
                url = "/delete_vehicle_kilometer/";
                datos.append("id", id);
                deleteItem(url, datos)
                    .then((message) => {
                        Swal.fire("Exito", message, "success");
                        table_kilometer.ajax.reload();
                    })
                    .catch((error) => {
                        Swal.fire("Error", error, "error");
                    });
                return;
            }

            if (submit == "update") {
                var id = $("button[type='submit']:focus", this).attr("data-vehiculo-id");
                var url = "/update_vehicle_kilometer/";
            }

            if (submit == "add") {
            }

            datos.append("id", id);
            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,
                success: function (response) {
                    table_kilometer.ajax.reload();
                    if (!response.success && response.error) {
                        Swal.fire("Error", response.error["message"], "error");
                        return;
                    } else if (!response.success && response.warning) {
                        Swal.fire("Advertencia", response.warning["message"], "warning");
                        return;
                    } else if (!response.success) {
                        Swal.fire("Error", "Ocurrio un error inesperado", "error");
                        return;
                    }
                    Swal.fire("Exito", "Se han guardado los cambios con exito", "success");
                    $("#mdl_crud_maintenance_kilometer").find("form")[0].reset();
                },
                error: function (xhr, status, error) {
                    Swal.fire(
                        "Error del servidor",
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                        "error"
                    );
                },
            });
        });

        $(document).on("click", "[data-sia-vehicle-maintenance]", function (e) {
            var obj = $(this);
            var option = obj.data("sia-vehicle-maintenance");
            // obj_modal.find("form :input").prop("disabled", false).closest(".col-12").show();

            switch (option) {
                case "refresh-table":
                    self.tbl_maintenance.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar Mantenimiento");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    obj_modal.find("[name='vehicle_id']").val(self.vehicle.data.vehicle_id || null);
                    obj_modal
                        .find("[name='vehicle__name']")
                        .val(self.vehicle.data.vehicle__name || null)
                        .prop("readonly", true);
                    obj_modal
                        .find(".modal-body :input:not([type='hidden'])")
                        .prop("disabled", false)
                        .closest(".col-12")
                        .show();
                    obj_modal.find("[name='type']").trigger("change");
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });

                    try {
                        let jsonString = datos["actions"].replace(/'/g, '"');
                        let objeto = JSON.parse(jsonString);
                        let claves = Object.keys(objeto);
                        obj_modal.find('[name="type"]').trigger("change");
                        obj_modal.find('[name="actions[]"]').val(claves);
                        obj_modal.find('[name="actions[]"]').trigger("change");
                    } catch (error) {
                        console.error(error);
                    }
                    break;
                case "delete-item":
                    var url = "/delete_vehicle_maintenance/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_maintenance.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                case "schedule-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Programar Mantenimiento");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    obj_modal.find("[name='vehicle_id']").show().prop("readonly", false);
                    obj_modal.find("[name='vehicle__name']").hide();

                    obj_modal
                        .find(".modal-body :input:not([type='hidden'])")
                        .prop("disabled", true)
                        .closest(".col-12")
                        .hide();
                    obj_modal.find(".schedule-item").show().find(":input").prop("disabled", false);
                    obj_modal.find('[name="actions[]"]').trigger("change");
                    obj_modal.modal("show");
                    break;
                case "check":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("maintenanceoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    obj_modal.find("[name='vehicle_id']").hide().prop("readonly", true);
                    obj_modal.find("[name='vehicle__name']").show().prop("readonly", true);
                    obj_modal.find("[name='date']").prop("readonly", true);

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    try {
                        let jsonString = datos["actions"].replace(/'/g, '"');
                        let objeto = JSON.parse(jsonString);
                        let claves = Object.keys(objeto);
                        obj_modal.find('[name="actions[]"]').val(claves);
                        obj_modal.find('[name="actions[]"]').trigger("change");
                    } catch (error) {
                        console.error(error);
                    }
                    break;
                case "show-info":
                    hideShow("#v-maintenance-pane .info-details", "#v-maintenance-pane .info");
                    break;
                case "show-info-details":
                    hideShow("#v-maintenance-pane .info", "#v-maintenance-pane .info-details");

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();

                    // Limpiar el contenido del contenedor antes de cargar nuevos datos

                    var obj_div = $("#v-maintenance-pane .info-details");
                    $.each(datos, function (index, value) {
                        var isFileInput = obj_div.find(`[name="${index}"]`).is(":file");

                        if (!isFileInput) {
                            obj_div
                                .find(`[data-key-value="${index}"]`)
                                .html(value || "---")
                                .removeClass();
                            obj_div.find(`[name="${index}"]`).val(value);
                        }
                    });

                    // Lista
                    var jsonString = datos["actions"].replace(/'/g, '"');
                    var objeto = JSON.parse(jsonString);
                    obj_div.find("ol.list-group").html(""); // 15 // "S10" // "preventivo"
                    $.each(objeto, function (index, value) {
                        let li = $("<li>")
                            .addClass("list-group-item list-group-item-action")
                            .appendTo(obj_div.find("ol.list-group"));
                        li.append(`${index}`);
                        let select = $(`
                                <select name="${index}" class="form-select form-select-sm d-inline-block float-end action-item" style="width: auto;" disabled>
                                    <option value="MALO">MALO</option>
                                    <option value="REGULAR">REGULAR</option>
                                    <option value="BUENO">BUENO</option>
                                </select>
                            `);
                        select.find(`option[value="${value}"]`).prop("selected", true);
                        li.append(select);
                    });
                    var lista = [];

                    var actionsKeys = Object.keys(objeto);
                    lista.push(...actionsKeys);

                    verificar_mantenimiento(
                        lista,
                        datos["vehicle_id"],
                        datos["type"],
                        datos["id"],
                        "INTERNO",
                        function (result) {
                            let opciones = result; // Usamos el resultado directamente

                            // Recorrer los <li> dentro de #card_maintenance_info y cambiar su color si su texto está en opciones
                            $(
                                "#card_maintenance_info .list-group-item.list-group-item-action"
                            ).each(function () {
                                // Obtener SOLO el texto principal del <li>, ignorando el contenido de elementos hijos como <select>
                                let textoLi = $(this).clone().children().remove().end().text();

                                if (opciones.includes(textoLi)) {
                                    $(this).attr(
                                        "style",
                                        "background-color:rgb(205,101,101) !important; color: #ffffff !important;border: 1px solid #ffffff !important;"
                                    ); // Resaltar en rojo con !important
                                    // Insertar el ícono con el tooltip
                                    $(this).append(
                                        '<span data-bs-toggle="tooltip" data-bs-placement="top" title="Cambio realizado en mantenimiento anterior">' +
                                            '<i class="fa fa-question-circle" style="cursor: pointer; color: #ffffff; margin-left: 10px;"></i>' +
                                            "</span>"
                                    );
                                    // Inicializar los tooltips de Bootstrap
                                    $('[data-bs-toggle="tooltip"]').tooltip();
                                }
                            });
                        }
                    );

                    // Archivo
                    if (datos["comprobante"]) {
                        $(".comprobante [type='file']").hide();
                        $(".comprobante [type='file']").addClass("d-none");
                        $(".comprobante a.btn").show();
                        $(".comprobante a.btn").attr("href", "/" + datos["comprobante"]);
                        obj_div.find(".form-btn").hide();
                    } else {
                        $(".comprobante [type='file']").show();
                        $(".comprobante [type='file']").removeClass("d-none");
                        $(".comprobante .btn").hide();
                        obj_div.find(".form-btn").show();
                    }

                    let _vehicle = typeof vehicle !== "undefined" ? vehicle : self.vehicle;
                    _vehicle.infoCard.vehicle.id = datos["vehicle_id"];
                    _vehicle.infoCard.ajax.reload();
                    break;
                default:
                    console.log("Opción dezconocida:", option);
                    break;
            }
        });

        obj_modal.find('[name="type"]').on("change", function (e) {
            var tipo = $(this).val().toLowerCase();
            var select = obj_modal.find("[name='actions[]']");
            var optionsHTML = "";
            select.empty();
            optionsHTML = `<option value="Nuevo" id="btn-save-new-option">Nuevo</option>`;

            // Agregar las opciones correspondientes
            $.each(self.dataMaintenance[tipo], function (index, value) {
                optionsHTML += `<option value="${value["descripcion"]}">${value["descripcion"]}</option>`;
            });
            // Actualiza el select con las nuevas opciones
            select.html(optionsHTML);
            // Si estás usando select2, actualiza select2 después de cambiar las opciones
            select.select2({
                search: true,
                closeOnSelect: false,
            });
        });

        // Detectar si seleccionan "Nuevo" y abrir el modal

        obj_modal.on("change", "[name='actions[]']", function () {
            var selectedOption = $(this).val();
            var vehicle_man = $('#mdl_crud_maintenance select[name="vehicle_id"]').val();
            var tipo = $('#mdl_crud_maintenance select[name="type"]').val();
            let id_edit = ""; // Inicializa la variable con un valor por defecto

            if ($('#mdl_crud_maintenance input[name="id"]').val()) {
                id_edit = $('#mdl_crud_maintenance input[name="id"]').val();
            } else {
                id_edit = ""; // Si no hay valor en el campo, asegúrate de que sea una cadena vacía
            }
            verificar_mantenimiento(selectedOption, vehicle_man, tipo, id_edit, "MODAL");
            if (selectedOption.includes("Nuevo")) {
                // Abrir el modal para agregar un nuevo tipo
                $("#mdl-crud-option-maintenance").modal("show");
                $("#mdl-crud-option-maintenance").css("z-index", "1056");

                // Al hacer submit del modal, agregar la nueva opción
                obj_modal_option
                    .find("form")
                    .off("submit")
                    .on("submit", function (e) {
                        e.preventDefault();

                        var optionName = $("#option_maintenance_name").val();
                        optionName = optionName.toUpperCase(); // Obtiene el valor del input
                        var maintenanceType = $('select[name="type"]').val(); // Obtiene el tipo de mantenimiento

                        if (optionName) {
                            $.ajax({
                                url: "/add_option/",
                                method: "POST",
                                contentType: "application/json",
                                data: JSON.stringify({
                                    option_maintenance_name: optionName,
                                    maintenance_type: maintenanceType,
                                }),
                                success: function (data) {
                                    // Agregar la nueva opción al array de seleccionados
                                    var select = obj_modal.find("[name='actions[]']");
                                    var selectedOptions = select.val() || [];
                                    selectedOptions = selectedOptions.filter(function (value) {
                                        return value !== "Nuevo"; // Filtrar "Nuevo" del array
                                    });
                                    selectedOptions.push(optionName); // Agregar la nueva opción

                                    // Actualizar el select con la nueva opción
                                    select.append(
                                        `<option value="${optionName}">${optionName}</option>`
                                    );
                                    select.val(selectedOptions).trigger("change");

                                    // Actualizar select2
                                    select.select2({
                                        search: true,
                                        closeOnSelect: false,
                                    });

                                    // Cerrar el modal y limpiar el campo de la nueva opción
                                    $("#mdl-crud-option-maintenance").modal("hide");
                                    $("#option_maintenance_name").val("");

                                    Swal.fire({
                                        title: "¡Éxito!",
                                        text: "La descripción ha sido agregada correctamente",
                                        icon: "success",
                                    });
                                    self.loadApi();
                                },
                                error: function (xhr) {
                                    console.error("Error:", xhr.responseJSON.message);
                                    Swal.fire({
                                        title: "Error",
                                        text: xhr.responseJSON.message,
                                        icon: "error",
                                        timer: 1500,
                                    });
                                },
                            });
                        } else {
                            alert("Por favor ingresa un nombre válido para la nueva opción.");
                        }
                    });
            }
        });

        $("#cerrar").on("click", function (e) {
            e.preventDefault();
            $("#option_maintenance_name").val(""); // Limpiar el valor del input
        });

        obj_modal.find("[name='actions[]']").on("select2:open", function () {
            $("span.select2-container").css("z-index", "1055");
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_maintenance/";
            var datos = new FormData(this);

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
                    Swal.fire("Exito", message, "success");
                    self.tbl_maintenance.ajax.reload();
                    obj_modal.modal("hide");
                },
                error: function (xhr, status, error) {
                    Swal.fire(
                        "Error del servidor",
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                        "error"
                    );
                },
            });
        });

        $("#form_maintenance_info").on("submit", function (e) {
            e.preventDefault();
            var url = "/update_vehicle_maintenance/";
            var datos = new FormData(this);

            Swal.fire({
                title: "Estas seguro?",
                text: "Solo se podra guardar cambios una sola vez",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Si, adelante",
            }).then((result) => {
                if (!result.isConfirmed) return;

                var actionsformat2 = {};
                $(".action-item").each(function () {
                    var name = $(this).attr("name");
                    var valor = $(this).val();
                    actionsformat2[name] = valor;
                });

                datos.append("actionsformat2", JSON.stringify(actionsformat2));

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
                        Swal.fire("Exito", message, "success");
                        $("#comprobante").val("");
                    },
                    error: function (xhr, status, error) {
                        let errorMessage = "Ocurrió un error inesperado";
                        if (xhr.responseJSON && xhr.responseJSON.message) {
                            errorMessage = xhr.responseJSON.message;
                        }
                        Swal.fire("Error", errorMessage, "error");

                        console.error("xhr:", xhr);
                    },
                });
            });
        });

        $('input[name="comprobante"]').change(function (e) {
            e.preventDefault();
            if ($(this).prop("files").length > 0) {
                $("li select").prop("disabled", false);
            } else {
                $("li select").prop("disabled", true);
            }
        });
    }

    loadApi() {
        const self = this;
        var obj_modal = $("#mdl_crud_computerSystem");
        var url = SIA.static + "assets/json/vehicles-maintenance.json";

        $.ajax({
            type: "GET",
            url: url,
            success: function (response) {
                self.dataMaintenance = {};
                $.each(response.data, function (index, mantenimiento) {
                    var tipo = mantenimiento.tipo;
                    self.dataMaintenance[tipo] = mantenimiento.items;
                });
            },
            error: function (xhr, status, error) {
                console.error("Error al cargar el JSON:", error);
                self.dataMaintenance = { preventivo: [], correctivo: [] };
            },
            complete: function () {},
        });
    }
}

function verificar_mantenimiento(selectedOption, vehicle, tipo, id_edit, modulo, callback = null) {
    var dataToSend = {
        selectedOption: selectedOption, // selectedOptions es un array
        vehicle: vehicle, // El ID del vehículo
        tipo: tipo,
        id_edit: id_edit,
    };
    // datos.append("actionsformat2", JSON.stringify(actionsformat2));
    $.ajax({
        url: "/verificar_mantenimiento/",
        method: "POST",
        data: JSON.stringify(dataToSend),
        contentType: "application/json", // Establecemos el tipo de contenido
        dataType: "json", // Esperamos recibir una respuesta JSON
        success: function (data) {
            // Declarar 'opciones' fuera del bloque if
            let opciones = [];

            if (data.status == "info") {
                // Separar el mensaje en opciones sin modificar el contenido
                opciones = data.message.split("*").filter((op) => op !== "");
            }

            if (modulo == "MODAL") {
                $(
                    ".select2-container--default .select2-selection--multiple .select2-selection__choice"
                ).each(function () {
                    let tituloOpcion = $(this).attr("title");

                    // Si el title está en la lista de opciones devueltas, cambia el color de toda la estructura
                    if (opciones.includes(tituloOpcion)) {
                        $(this).css({
                            "background-color": "rgb(205,101,101)", // Establece el fondo
                            border: "1px solid rgb(205,101,101)",
                        });
                        // Establecer un texto de tooltip cuando el cursor pase sobre el elemento
                        $(this).attr("title", "Cambio realizado en mantenimiento pasado");
                    } else {
                        // Eliminar el color de fondo si no coincide con las opciones
                        $(this).css({
                            "background-color": "var(--primary-color)", // Establece el fondo
                            border: "1px solid var(--primary-color)", // Ajuste para el borde
                        });
                    }
                });
            } else {
                if (callback) {
                    callback(opciones); // Llama al callback con el resultado
                }
            }
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
            Swal.fire({
                title: "Error",
                text: "Hubo un problema al procesar la solicitud",
                icon: "error",
            });
        },
    });
}

function add_option() {
    var optionName = $("#option_maintenance_name").val(); // Obtiene el valor del input
    var maintenanceType = $('select[name="type"]').val(); // Obtiene el tipo de mantenimiento

    $.ajax({
        url: "/add_option/",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            option_maintenance_name: optionName,
            maintenance_type: maintenanceType,
        }),
        success: function (data) {
            $("#mdl-crud-option-maintenance").modal("hide");

            // Limpiar solo el campo de la nueva opción
            $("#option_maintenance_name").val("");

            Swal.fire({
                title: "¡Éxito!",
                text: "La descripción ha sido agregada correctamente",
                icon: "success",
                timer: 1500,
            });
        },
        error: function (xhr) {
            console.error("Error:", xhr.responseJSON.message);
            Swal.fire({
                title: "Error",
                text: xhr.responseJSON.message,
                icon: "error",
                timer: 1500,
            });
        },
    });
}

function actualizarLista() {
    $.ajax({
        url: "/obtener_opciones/",
        method: "GET",
        success: function (data) {
            var selectField = $("#select-field");
            selectField.empty();

            data.forEach((opcion) => {
                selectField.append(`<option value="${opcion.id}">${opcion.descripcion}</option>`);
            });
        },
        error: function (xhr) {
            console.error("Error al cargar las opciones:", xhr);
        },
    });
}

// Manejar el cambio de estado en el select con la clase 'status-man'
$(document).on("change", ".status-man", function () {
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
            update_status_man(id, newStatus);
        } else {
            // Restaurar el valor anterior si se cancela
            var currentStatus = $(this).find("option:selected").text();
            $(this).val(currentStatus);
        }
    });
});

// Función para enviar la solicitud AJAX y actualizar el estado
function update_status_man(id, newStatus) {
    $.ajax({
        url: "/update_status_man/", // URL que definimos en urls.py
        method: "POST",
        data: {
            id: id,
            status: newStatus,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(), // Asegúrate de incluir el token CSRF si estás usando Django
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
