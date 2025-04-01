class ComputerEquipment_maintenance {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            list: {
                id: null,
                ajax: {},
            },
            table: {
                id: "#maintenance_table",
                ajax: {
                    url: "/get-computer-equipment-maintenances/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Equipo", data: "computerSystem__name" },
                    { title: "Tipo", data: "type" },
                    { title: "Realizado por", data: "performed_by" },
                    {
                        title: "Costo",
                        data: "cost",
                        render: $.fn.dataTable.render.number(",", ".", 2, "$"),
                    },
                    {
                        title: "Fecha",
                        data: "date",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                    },
                    {
                        title: "Revisado",
                        data: "is_checked",
                        render: function (data, type, row) {
                            return data
                                ? '<span class="badge bg-outline-success">SI</span>'
                                : '<span class="badge bg-outline-danger">NO</span>';
                        },
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.computer) {
            self.computer = options.computer;
            self.data = { ...self.data, ...self.computer.data };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };
        }

        self.init();
    }

    init() {
        const self = this;
        var obj_modal = $("#mdl_crud_computer_equipment_maintenance");

        if (self.table) {
            self.tbl_maintenance = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function () {
                        return self.data;
                    },
                },
                columns: self.table.columns,
                order: [
                    [0, "desc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                initComplete: function (settings, json) {
                    delete self.table;
                },
            });
        }
        if (self.data["computerSystem_id"] && self.data["computerSystem_id"] != null) {
            $(".tr-computer-equipment").hide();
        } else {
            $(".tr-computer-equipment").show();
        }

        self.setupEventHandlers();
        self.loadApi();
        obj_modal.find("[name='actions[]']").select2();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_computer_equipment_maintenance");
        var formato = new Intl.NumberFormat("es-MX", {
            style: "currency",
            currency: "MXN",
        });

        $(document).on("click", "[data-sia-computer-equipment-maintenance]", function (e) {
            var obj = $(this);
            var option = obj.data("sia-computer-equipment-maintenance");

            switch (option) {
                case "refresh-table":
                    self.tbl_maintenance.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Agregar mantenimiento");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    obj_modal.find("[name='type']").trigger("change");
                    obj_modal.find("[name='performed_by']").trigger("change");
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Actualizar mantenimiento");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });

                    obj_modal.find("[name='type']").trigger("change");
                    obj_modal.find("[name='performed_by']").trigger("change");

                    try {
                        let jsonString = datos["actions"].replace(/'/g, '"');
                        let objeto = JSON.parse(jsonString);
                        let claves = Object.keys(objeto);

                        obj_modal.find('[name="actions[]"]').val(claves);
                        obj_modal.find('[name="actions[]"]').trigger("change");
                    } catch (error) {}
                    break;
                case "delete-item":
                    var url = "/delete-computer-equipment-maintenance/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_maintenance.ajax.reload();
                        })
                        .catch((error) => {
                            var message = "Se ha producido un problema en el servidor.";
                            message += " Por favor, inténtalo de nuevo más tarde.";
                            if (typeof error === "string") {
                                message = error;
                            }

                            Swal.fire("Error", error, "error");
                        });
                    break;
                case "show-info":
                    hideShow("#v-maintenance-pane .info-details", "#v-maintenance-pane .info");
                    break;
                case "show-info-details":
                    hideShow("#v-maintenance-pane .info", "#v-maintenance-pane .info-details");
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_maintenance.row(fila).data();
                    var obj_div = $(".info-details");

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_div.find(`[name="${index}"]`).is(":file");
                        if (!isFileInput) {
                            obj_div
                                .find(`[data-key="${index}"]`)
                                .html(value || "-----")
                                .removeClass();
                            obj_div.find(`[name="${index}"]`).val(value);
                        }
                    });

                    // Realizador por...
                    if (datos["performed_by"] == "Proveedor") {
                        obj_div.find(".tr-provider").show();
                        obj_div.find(".tr-user").hide();
                    } else {
                        obj_div.find(".tr-provider").hide();
                        obj_div.find(".tr-user").show();
                    }

                    // Dar formato al costo
                    obj_div.find("[data-key='cost']").html(formato.format(datos["cost"]));

                    // Dar formato a la Fecha
                    var formattedDate = datos["date"]
                        ? moment(datos["date"]).format("D [de] MMMM [de] YYYY")
                        : "-----";
                    obj_div.find("[data-key='date']").html(formattedDate).removeClass();

                    // Lista
                    var jsonString = datos["actions"].replace(/'/g, '"');
                    var objeto = JSON.parse(jsonString);
                    obj_div.find("ol.list-group").html(null);
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

                    // Check de la lista
                    if (datos["is_checked"]) {
                        obj_div.find("li select").prop("disabled", true);
                        obj_div.find(".form-btn").hide();
                    } else {
                        obj_div.find("li select").prop("disabled", false);
                        obj_div.find(".form-btn").show();
                    }
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url =
                "/" + (submit == "add" ? "add" : "update") + "-computer-equipment-maintenance/";
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
                    obj_modal.modal("hide");
                    self.tbl_maintenance.ajax.reload();
                },
                error: function (xhr, status, error) {
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    console.error("Error en la petición AJAX:", error);
                },
            });
        });

        obj_modal.find("[name='type']").on("change", function () {
            var tipo = $(this).val().toLowerCase();
            var select = obj_modal.find("[name='actions[]']");
            var optionsHTML = "";
            select.empty();
            $.each(self.dataMaintenance[tipo], function (index, value) {
                optionsHTML += `<option value="${value["descripcion"]}">${value["descripcion"]}</option>`;
            });
            select.html(optionsHTML);

            // select2
            obj_modal.find("[name='actions[]']").select2("destroy");
            obj_modal.find("[name='actions[]']").select2({
                search: true,
                closeOnSelect: false,
            });
        });

        obj_modal.find("[name='performed_by']").on("change", function () {
            var op = $(this).val();
            obj_modal
                .find(".col-proveedor, .col-usuario")
                .hide()
                .find(":input")
                .prop("disabled", true);
            if (op == "Proveedor") {
                obj_modal.find(".col-proveedor").show().find(":input").prop("disabled", false);
            } else if (op == "Usuario") {
                obj_modal.find(".col-usuario").show().find(":input").prop("disabled", false);
            }
        });

        obj_modal.find("[name='actions[]']").on("select2:open", function () {
            $("span.select2-container").css("z-index", "1055");
        });

        $("#v-maintenance-pane .info-details form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/update-computer-equipment-maintenance/";
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
                datos.append("is_checked", true);

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
                        self.tbl_maintenance.ajax.reload();
                        hideShow("#v-maintenance-pane .info-details", "#v-maintenance-pane .info");
                    },
                    error: function (xhr, status, error) {
                        Swal.fire(
                            "Error del servidor",
                            "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                            "error"
                        );
                    },
                });

                // END the
            });
        });
    }

    loadApi() {
        const self = this;
        var obj_modal = $("#mdl_crud_computerSystem");
        var url = SIA.static + "assets/json/computers-equipment-maintenance.json";

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
                self.dataMaintenance = { preventivo: [], correctivo: [] };
            },
            complete: function () {},
        });
    }
}
