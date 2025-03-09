class ComputerEquipment_audit {
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
                    url: "/get-computer-equipment-audits/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Equipo", data: "computerSystem__name" },
                    {
                        title: "Fecha",
                        data: "audit_date",
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
            self.tbl_audit = $(self.table.id).DataTable({
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

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_computer_equipment_audit");

        $(document).on("click", "[data-sia-computer-equipment-audit]", function (e) {
            var obj = $(this);
            var option = obj.data("sia-computer-equipment-audit");

            switch (option) {
                case "refresh-table":
                    self.tbl_audit.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Agregar Auditoria");
                    obj_modal.find(":input").prop("disabled", false);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    obj_modal.find("[name='computerSystem_id']").prop("disabled", false);
                    obj_modal.find("[name='is_checked']").val(0).closest(".row").hide();
                    obj_modal.find("select").prop("required", true);
                    // obj_modal.find(".info-2").hide().find(":input").prop("diabled", true);
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Actualizar Auditoria");
                    obj_modal.find(":input").prop("disabled", false);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });

                    var is_checked = datos["is_checked"] ? 1 : 0;
                    obj_modal.find("[name='is_checked']").val(is_checked).prop("disabled", false);
                    obj_modal.find("[name='computerSystem_id']").prop("disabled", false);
                    obj_modal.find("[name='is_checked']").closest(".row").show();
                    break;
                case "delete-item":
                    var url = "/delete-computer-equipment-audit/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_audit.ajax.reload();
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
                case "check-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Relizar auditoria");
                    obj_modal.find(":input").prop("disabled", false);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });

                    obj_modal.find("[name='is_checked']").val(1).prop("disabled", false);
                    obj_modal.find("[name='computerSystem_id']").prop("disabled", true);
                    obj_modal.find("[name='is_checked']").closest(".row").hide();

                    obj_modal.find("select").prop("required", true);
                    break;
                case "show-info-details":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Información de auditoria");
                    obj_modal.find("[type='submit']").hide();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });

                    var is_checked = datos["is_checked"] ? 1 : 0;
                    obj_modal.find("[name='is_checked']").val(is_checked).prop("disabled", false);

                    obj_modal.find(":input:not(button)").prop("disabled", true);
                    obj_modal.find(".data-bs-dismiss").prop("disabled", false);
                    break;
                default:
                    console.log("Opción dezconocida: " + option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-computer-equipment-audit/";
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
                    obj_modal.modal("hide");
                    self.tbl_audit.ajax.reload();
                },
                error: function (xhr, status, error) {
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    console.error("Error en la petición AJAX:", error);
                },
            });
        });
    }
}
