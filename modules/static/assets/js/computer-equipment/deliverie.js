class ComputerEquipment_deliverie {
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
                id: "",
                ajax: {
                    url: "/get-computer-equipment-deliveries/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    {
                        title: "Responsable",
                        data: function (d) {
                            const firstName = d["responsible__first_name"]
                                ? d["responsible__first_name"]
                                : "";
                            const lastName = d["responsible__last_name"]
                                ? ` ${d["responsible__last_name"]}`
                                : "";
                            return `${firstName}${lastName}`;
                        },
                    },
                    {
                        title: "PDF",
                        data: function (d) {
                            if (d["responsibility_letter"]) {
                                return `<a href="${d["responsibility_letter"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Responsiva
                                </a>`;
                            } else {
                                return "";
                            }
                        },
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            table_details: {},
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
        var obj_modal = $("#mdl-crud-computer-equipment-deliverie");

        if (self.table) {
            self.tbl_deliverie = $(self.table.id).DataTable({
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
                dom:
                    "<'row justify-content-between'<'col-md-auto'l><'col-md-auto'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
                initComplete: function (settings, json) {
                    delete self.table;
                },
            });
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-computer-equipment-deliverie");

        $(document).on("click", "[data-sia-computer-equipment-deliverie]", function (e) {
            var obj = $(this);
            var option = obj.data("sia-computer-equipment-deliverie");

            switch (option) {
                case "refresh-table":
                    self.tbl_deliverie.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Agregar entrega de equipo");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find("[name='responsible_id']").trigger("change");
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal
                        .find(".modal-header .modal-title")
                        .html("Actualizar entrega de equipo");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_deliverie.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });
                    break;
                case "delete-item":
                    var url = "/delete-computer-equipment-deliverie/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_deliverie.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_deliverie.ajax.reload();
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
                case "check":
                    break;
                default:
                    console.log("Opcion dezconocida:", option);
                    break;
            }
        });

        obj_modal.find("[name='responsible_id']").on("change", function () {
            var valor = $(this).val().toLowerCase();

            if (valor == "") {
                obj_modal.find("a.pdf-link").closest("div").hide();
            } else {
                obj_modal.find("a.pdf-link").closest("div").show();

                var ruta = `/computers-equipment/deliverie/pdf/?user_id=${valor}`;
                obj_modal.find("a.pdf-link").attr("href", ruta);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-computer-equipment-deliverie/";
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
                    obj_modal.modal("hide");
                    Swal.fire("Éxito", message, "success");
                    self.tbl_deliverie.ajax.reload();
                },
                error: function (xhr, status, error) {
                    let errorMessage = "Ocurrió un error inesperado";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    }
                    Swal.fire("Error", errorMessage, "error");
                    console.log("Error en la petición AJAX:");
                    console.error("xhr:", xhr);
                },
            });
        });
    }
}
