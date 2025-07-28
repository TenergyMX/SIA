class VehiclesTenencia {
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
                        return "/get_vehicles_tenencia/";
                    },
                    data: function () {
                        return {
                            vehicle_id: defaultOptions.info.id || defaultOptions.info.vehicle_id,
                        };
                    },
                    reload: function () {},
                },
            },

            table: {
                id: "#table_tenencia",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_tenencia/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehiculo__name" },
                    { title: "Fecha de pago", data: "fecha_pago" },
                    { title: "Monto", data: "monto" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: {
                data: { id: null },
            },
        };

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };

            if (self.table.vehicle.id) {
                self.table.ajax.url = "/get_vehicle_tenencia/";
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

        self.init();
    }

    init() {
        const self = this;

        if (self.table) {
            self.tbl_tenencia = $(self.table.id).DataTable({
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

        if (self.vehicle && self.vehicle.data.id) {
            $('#mdl_crud_tenencia [name="vehicle_id"]').hide();
            $('#mdl_crud_tenencia [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_tenencia [name="vehicle_id"]').show();
            $('#mdl_crud_tenencia [name="vehicle__name"]').hide();
        }

        this.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_tenencia");

        $(document).on("click", "[data-vehicle-tenencia]", function (e) {
            var obj = $(this);
            var option = obj.data("vehicle-tenencia");
            obj_modal.find("form :input").prop("disabled", false).closest(".col-12").show();

            switch (option) {
                case "refresh-table":
                    self.tbl_tenencia.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar mantenimiento vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find('[name="actions[]"]').trigger("change");

                    if (self.vehicle && self.vehicle.data.id) {
                        obj_modal.find("[name='vehiculo_id']").hide().prop("readonly", true);
                        obj_modal.find("[name='vehiculo__name']").show().prop("readonly", false);
                    } else {
                        obj_modal.find("[name='vehiculo_id']").show().prop("readonly", false);
                        obj_modal.find("[name='vehiculo__name']").hide();
                    }

                    obj_modal
                        .find("[name='vehiculo_id']")
                        .val(self.vehicle.data.vehicle_id || null);
                    obj_modal
                        .find("[name='vehiculo__name']")
                        .val(self.vehicle.data.vehicle__name || null)
                        .prop("readonly", true);
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_tenencia.row(fila).data();
                    var select = obj_modal.find('select[name="vehiculo_id"]');

                    if (select.find(`option[value="${datos["vehiculo_id"]}"]`).length < 1) {
                        select.append(
                            `<option value="${datos["vehiculo_id"]}">${datos["vehiculo__name"]}</option>`
                        );
                    }

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });

                    if (self.vehicle && self.vehicle.data.id) {
                        obj_modal.find("[name='vehiculo_id']").hide().prop("readonly", true);
                        obj_modal.find("[name='vehiculo__name']").show().prop("readonly", false);
                    } else {
                        obj_modal.find("[name='vehiculo_id']").show().prop("readonly", false);
                        obj_modal.find("[name='vehiculo__name']").hide();
                    }
                    break;
                case "delete-item":
                    var url = "/delete_vehicle_tenencia/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_tenencia.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_tenencia.ajax.reload();
                        })
                        .catch((error) => {
                            console.error("este es el Error en la eliminación:", error); // Para ver el error en la consola
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
                    var datos = self.tbl_tenencia.row(fila).data();

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
                    var datos = self.tbl_tenencia.row(fila).data();
                    var obj_div = $("#v-maintenance-pane .info-details");
                    $.each(datos, function (index, value) {
                        obj_div.find(`[data-key-value="${index}"]`).html(value).removeClass();
                    });

                    try {
                        var actionsString = datos["actions"];
                        var jsonString = actionsString.replace(/'/g, '"');
                        var actions_list = JSON.parse(jsonString);
                        obj_div.find("ol.list-group").html(null);

                        $.each(actions_list, function (index, value) {
                            obj_div
                                .find("ol.list-group")
                                .append(
                                    `<li class="list-group-item list-group-item-action">${value}</li>`
                                );
                        });
                    } catch (error) {
                        console.log(error);
                    }

                    if (!self.options.isSingleVehicle) {
                        load_vehicle_info_card(datos["vehicle_id"]);
                    }
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_tenencia/";
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
                        Swal.fire("Error", "Ocurrio un error inesperado", "error");
                        return;
                    }
                    Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                    self.tbl_tenencia.ajax.reload();
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
    }
}
