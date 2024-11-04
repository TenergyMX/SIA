class InfrastructureItem {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            infoCard: {
                id: null,
                ajax: {
                    url: function () {
                        return "/get-infrastructure-items/";
                    },
                    data: function () {},
                    reload: function () {},
                },
            },
            list: {
                id: null,
                ajax: {},
                data: {
                    isList: true,
                    category_id: 1,
                    category__name: "Se tenia que decir y se dijo",
                },
            },
            table: {
                id: "#computer_equipment_table",
                ajax: {
                    url: "/get-infrastructure-items/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Categoría", data: "category__name", className: "toggleable" },
                    { title: "Nombre", data: "name", className: "toggleable" },
                    { title: "Cantidad", data: "quantity", className: "toggleable" },
                    { title: "Descripción", data: "description", className: "toggleable" },
                    {
                        title: "Estatus",
                        data: "is_active",
                        render: function (d) {
                            return d
                                ? '<span class="badge bg-outline-success">Activo</span>'
                                : '<span class="badge bg-outline-danger">Inactivo</span>';
                        },
                        className: "toggleable",
                    },
                    {
                        title: "Fecha de inicio",
                        data: "start_date",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "Periodo",
                        data: function (d) {
                            let options_unit = {
                                day: d.time_quantity == 1 ? "Día" : "Días",
                                month: d.time_quantity == 1 ? "Mes" : "Meses",
                                year: d.time_quantity == 1 ? "Año" : "Años",
                            };
                            let quantity = d.time_quantity == 1 ? "Un" : d.time_quantity;
                            let unit = options_unit[d.time_unit];
                            return quantity + " " + unit;
                        },
                        className: "toggleable",
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.list) {
            var mergedListOptions = deepMerge(defaultOptions.list, options.list);
            self.list = { ...defaultOptions.list, ...mergedListOptions };

            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-infrastructure-items/",
                    data: self.list.data,
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        select.append("<option value='' data-category-id>-----</option>");
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}" data-category-id="${value["category_id"]}">
                                    ${value["name"]}
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
                    complete: function () {},
                });
            };
            self.dataList = {};
        }

        if (options.table) {
            var mergedTableOptions = deepMerge(defaultOptions.table, options.table);
            self.table = { ...defaultOptions.table, ...mergedTableOptions };
        }

        self.init();
    }

    init() {
        const self = this;

        self.generateReview().then(() => {
            if (self.list) {
                console.log(self.list.data);
                self.list.ajax.reload();
            }

            if (self.table) {
                self.tbl_infraesstructure_items = $(self.table.id).DataTable({
                    ajax: {
                        url: self.table.ajax.url,
                        dataSrc: self.table.ajax.dataSrc,
                        data: function (d) {
                            return self.data;
                        },
                    },
                    columns: self.table.columns,
                    order: [[0, "asc"]],
                    language: {
                        url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                    },
                    dom:
                        "<'row justify-content-between'<'col-md'l><'col-md text-center'B><'col-md'f>>" +
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
                    initComplete: function (settings, json) {},
                });

                delete self.table;
            }

            self.setupEventHandlers();
        });
    }

    generateReview() {
        return new Promise((resolve, reject) => {
            $.ajax({
                type: "GET",
                url: "https://sia-tenergy.com/generates_review/",
                success: function (response) {
                    resolve(response);
                },
                error: function (xhr, status, error) {
                    reject(error);
                },
            });
        });
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-infrastructure-item");

        $(document).on("click", "[data-infrastructure-item]", function (e) {
            var obj = $(this);
            var option = obj.data("infrastructure-item");

            switch (option) {
                case "refresh-table":
                    self.tbl_infraesstructure_items.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar item a la categoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar item a la categoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infraesstructure_items.row(fila).data();
                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name="${index}"]`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name="${index}"]`).val(value || null);
                        }
                    });

                    obj_modal
                        .find("[name='is_active']")
                        .val(datos["is_active"] == true ? "1" : "0");
                    break;
                case "delete-item":
                    var url = "/delete-infrastructure-item/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infraesstructure_items.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_infraesstructure_items.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                default:
                    console.log("Opción dezconocida: " + option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-infrastructure-item/";
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
                    self.tbl_infraesstructure_items.ajax.reload();
                    message = response.message || "Se han guardado los datos con éxito";
                    Swal.fire("Éxito", message, "success");
                    obj_modal.modal("hide");
                },
                error: function (xhr, status, error) {
                    var message =
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        message = xhr.responseJSON.message;
                    }
                    Swal.fire("Error", message, "error");
                },
            });
        });
    }
}
