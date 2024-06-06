class ComputerPeripheral {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {
                computerSystem_id: null,
            },
            infoCard: {
                id: null,
                ajax: {
                    url: function () {
                        return "/get_computer_equipment/";
                    },
                    data: function () {},
                    reload: function () {},
                },
            },
            table: {
                id: "#peripherals_table",
                ajax: {
                    url: "/get_computer_peripherals/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Nombre", data: "name", className: "toggleable" },
                    { title: "Tipo.", data: "peripheral_type", className: "toggleable" },
                    { title: "Marca", data: "brand", className: "toggleable" },
                    { title: "Modelo", data: "model", className: "toggleable" },
                    { title: "N. Serie", data: "serial_number", className: "toggleable" },
                    {
                        title: "Descripción",
                        data: "description",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Fecha de Adquisición",
                        data: "acquisition_date",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Ubicación",
                        data: "location",
                        visible: false,
                        className: "toggleable",
                    },
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
                        className: "toggleable",
                    },
                    { title: "Estado", data: "peripheral_status", className: "toggleable" },
                    {
                        title: "Comentarios",
                        data: "comments",
                        visible: false,
                        className: "toggleable",
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
            self.infoCard.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_computer_equipment/",
                    data: self.data,
                    beforeSend: function () {},
                    success: function (response) {
                        var card = $(".card-info");

                        $.each(response["data"], function (index, value) {
                            card.find(`[data-key="${index}"]`).html(value).removeClass();
                            card.find(`[name='${index}']`).val(value || "-----");
                        });

                        card.find(`[data-key="current_responsible__name"]`).html(`
                            ${response["data"]["current_responsible__first_name"]}
                        `);
                        card.find("picture img").attr("src", response["data"]["image_path"]);

                        self.data.id = response["data"]["id"] || null;
                        self.data.key = "Goku eta vaina e seria";
                    },
                    error: function (xhr, status, error) {
                        console.log("error");
                    },
                });
            };
        }

        if (options.table) {
            var mergedTableOptions = deepMerge(defaultOptions.table, options.table);
            self.table = { ...defaultOptions.table, ...mergedTableOptions };
        }

        self.init();
    }

    init() {
        const self = this;

        if (self.infoCard) {
            self.infoCard.ajax.reload();
        }

        if (self.table) {
            self.tbl_computerPeripheral = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function (d) {
                        return self.data;
                    },
                },
                columns: self.table.columns,
                order: [
                    [0, "asc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                dom:
                    "<'row'<'col-md-4'l><'col-md-4 text-center'B><'col-md-4'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
                buttons: [
                    {
                        extend: "colvis",
                        text: "Columnas",
                        columns: function (idx, data, node) {
                            return $(node).hasClass("toggleable");
                        },
                        className: "btn-sm",
                    },
                ],
            });

            delete self.table;
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_computerPeripheral");

        $(document).on("click", "[data-computer-peripheral]", function (e) {
            var obj = $(this);
            var option = obj.data("computer-peripheral");

            switch (option) {
                case "refresh-table":
                    self.tbl_computerPeripheral.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar Periferico");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_computerPeripheral.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "-----");
                        }
                    });
                    break;
                case "delete-item":
                    var url = "/delete_computer_peripheral/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_computerPeripheral.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_computerPeripheral.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                default:
                    console.log("Opción dezconocida: " + option);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_computer_peripheral/";
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
                    self.tbl_computerPeripheral.ajax.reload();
                    obj_modal.modal("hide");
                },
                error: function (xhr, status, error) {
                    var message =
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        message = xhr.responseJSON.message;
                    }
                    Swal.fire("Error del servidor", message, "error");
                },
            });
        });
    }
}
