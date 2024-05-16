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
                    { title: "Vehiculo", data: "vehicle__name" },
                    { title: "Mantenimiento", data: "type" },
                    { title: "Fecha", data: "date" },
                    { title: "Kilometraje", data: "mileage" },
                    { title: "Costos", data: "cost" },
                    { title: "Proveedor", data: "provider__name" },
                    { title: "actions", data: "btn_action", orderable: false },
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

        if (self.table) {
            self.tbl_maintenance = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: self.table.ajax.data,
                },
                columns: self.table.columns,
                order: [
                    [0, "asc"],
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
        self.load__maintenance_actions();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_maintenance");

        $(document).on("click", "[data-vehicle-maintenance]", function (e) {
            var obj = $(this);
            var option = obj.data("vehicle-maintenance");
            // obj_modal.find("form :input").prop("disabled", false).closest(".col-12").show();

            switch (option) {
                case "refresh-table":
                    self.tbl_maintenance.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar maintenanceoria vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find("[name='actions[]']").trigger("change");

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
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();
                    obj_modal.find('[name="type"]').trigger("change");

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

                        obj_modal.find('[name="actions[]"]').val(claves);
                        obj_modal.find('[name="actions[]"]').val(claves);
                        obj_modal.find('[name="actions[]"]').trigger("change");
                    } catch (error) {
                        console.log("Error asjdbakj");
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

                    obj_modal.find('[name="actions[]"]').trigger("change");
                    break;
                case "show-info":
                    hideShow("#v-maintenance-pane .info-details", "#v-maintenance-pane .info");
                    break;
                case "show-info-details":
                    hideShow("#v-maintenance-pane .info", "#v-maintenance-pane .info-details");

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();
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
                    let jsonString = datos["actions"].replace(/'/g, '"');
                    let objeto = JSON.parse(jsonString);

                    obj_div.find("ol.list-group").html(null);
                    $.each(objeto, function (index, value) {
                        let li = $("<li>")
                            .addClass("list-group-item list-group-item-action")
                            .appendTo(obj_div.find("ol.list-group"));
                        li.append(`${index}`);
                        let select = $(`
                                <select name="${index}" class="form-select form-select-sm d-inline-block float-end action-item" style="width: auto;" disabled>
                                    <option value="PENDIENTE">PENDIENTE</option>
                                    <option value="REVISADO">REVISADO</option>
                                    <option value="NO REALIZADO">NO REALIZADO</option>
                                </select>
                            `);
                        select.find(`option[value="${value}"]`).prop("selected", true);
                        li.append(select);
                    });

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
            }
        });

        obj_modal.find('[name="type"]').on("change", function (e) {
            var obj = $(this);
            var val = obj.val();
            self.load__maintenance_actions(val);
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
                    if (!response.success && response.error) {
                        Swal.fire("Error", response.error["message"], "error");
                        return;
                    } else if (!response.success && response.warning) {
                        Swal.fire("Advertencia", response.warning["message"], "warning");
                        return;
                    } else if (!response.success) {
                        console.log(response);
                        Swal.fire("Error", "Ocurrio un error inesperado", "error");
                        return;
                    }
                    Swal.fire("Exito", "Se han guardado los datos con exito", "success");
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
                        if (!response.success && response.error) {
                            Swal.fire("Error", response.error["message"], "error");
                            return;
                        } else if (!response.success && response.warning) {
                            Swal.fire("Advertencia", response.warning["message"], "warning");
                            return;
                        } else if (!response.success) {
                            console.log(response);
                            Swal.fire("Error", "Ocurrio un error inesperado", "error");
                            return;
                        }
                        Swal.fire("Exito", "Se han guardado los datos con exito", "success");
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

    load__maintenance_actions(_type = "preventivo") {
        var select = $("#mdl_crud_maintenance select[name='actions[]']");
        $.ajax({
            url: "/static/assets/json/maintenance.json",
            success: function (response) {
                select.html(null);
                $.each(response["data"][_type], function (index, value) {
                    select.append(`<option value="${value}">${value}</option>`);
                });
            },
            error: function (xhr, status, error) {
                Swal.fire(
                    "Error del servidor",
                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                    "error"
                );
            },
        });
    }
}
