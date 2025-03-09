class VehiclesAudit {
    constructor(options) {
        const self = this;
        const defaultOptions = {
            data: {},
            table: {
                id: "#table_responsiva",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_audit/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehicle__name" },
                    { title: "Fecha", data: "audit_date" },
                    { title: "Chk. Interior", data: "check_exterior" },
                    { title: "Chk. Exterior", data: "check_interior" },
                    { title: "Chk. Llantas", data: "check_tires" },
                    { title: "Chk. Anticongelante", data: "check_antifreeze_level" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: {
                data: { id: null },
            },
        };

        self.data = defaultOptions.data;

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };

            if (self.table.vehicle.id) {
                self.table.ajax.url = "/get_vehicle_audit/";
                self.table.ajax.data = {
                    vehicle_id: self.table.vehicle.id,
                };

                // Buscar el índice del elemento que quieres eliminar//
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
            self.tbl_audit = $(self.table.id).DataTable({
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

        if (self.vehicle && self.vehicle.data.id) {
            $('#mdl_crud_audit [name="vehicle_id"]').hide();
            $('#mdl_crud_audit [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_audit [name="vehicle_id"]').show();
            $('#mdl_crud_audit [name="vehicle__name"]').hide();
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_audit");

        $(document).on("click", "[data-vehicle-audit]", function (e) {
            const obj = $(this);
            const option = obj.data("vehicle-audit");

            switch (option) {
                case "refresh-table":
                    self.tbl_audit.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Registrar Auditoria vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    if (self.vehicle && self.vehicle.data.id) {
                        obj_modal.find('[name="vehicle_id"]').hide();
                        obj_modal.find('[name="vehicle__name"]').show();
                    } else {
                        obj_modal.find('[name="vehicle_id"]').show();
                        obj_modal.find('[name="vehicle__name"]').hide();
                    }
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });
                    break;
                case "delete-item":
                    var url = "/delete_vehicle_audit/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            console.log("success");
                            Swal.fire("Exito", message, "success");
                            self.tbl_audit.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire(
                                "Oops",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        });
                    break;
                case "check":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Auditoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    obj_modal.find('[name="vehicle_id"]').hide();
                    obj_modal.find('[name="vehicle__name"]').show();
                    obj_modal.find('[name="audit_date"]').prop("readonly", true);
                    break;
                case "show-info":
                    hideShow("#v-audit-pane .info-details", "#v-audit-pane .info");
                    break;
                case "show-info-details":
                    hideShow("#v-audit-pane .info", "#v-audit-pane .info-details");
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();
                    var obj_div = $("#v-audit-pane .info-details");

                    $.each(datos, function (index, value) {
                        obj_div
                            .find(`[data-key-value="${index}"]`)
                            .html(value || "---")
                            .removeClass();
                    });

                    // ! Actualizamos la info card
                    if (self.vehicle && self.vehicle.infoCard) {
                        self.vehicle.infoCard.vehicle.id = datos["vehicle_id"];
                        self.vehicle.infoCard.ajax.reload();
                    }
                    break;
                default:
                    console.log("Opción dezconocida:", option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_audit/";
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
                    self.tbl_audit.ajax.reload();
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
