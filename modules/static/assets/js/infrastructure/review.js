class InfrastructureReview {
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
                id: "#infraestructura-reviews-table",
                ajax: {
                    url: "/get-infrastructure-reviews/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Categoría", data: "category__name", className: "toggleable" },
                    { title: "Item", data: "item__name", className: "toggleable" },
                    { title: "Check", data: "checked", className: "toggleable" },
                    { title: "Notas", data: "notes", className: "toggleable", visible: false },
                    {
                        title: "fecha",
                        data: "date",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                        className: "toggleable",
                    },
                    {
                        title: "Revisado Por",
                        data: function (d) {
                            const firstName = d["reviewer__first_name"]
                                ? d["reviewer__first_name"]
                                : "";
                            const lastName = d["reviewer__last_name"]
                                ? ` ${d["reviewer__last_name"]}`
                                : "";
                            return firstName + lastName;
                        },
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "Archivo",
                        data: function (d) {
                            if (d["file"]) {
                                return `<a href="/${d["file"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Archivo
                                </a>`;
                            } else {
                                return "";
                            }
                        },
                        className: "toggleable",
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-infrastructure-reviews/",
                    data: {
                        isList: true,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        select.append("<option value=''>-----</option>");
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}">
                                    ${value["name"]}
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
                });
            };
        }

        if (options.table) {
            var mergedTableOptions = deepMerge(defaultOptions.table, options.table);
            self.table = { ...defaultOptions.table, ...mergedTableOptions };
        }

        if (options.category) {
            self.category = options.category;
        }

        if (options.item) {
            self.item = options.item;
            self.item.dataList = {};
        }

        self.init();
    }

    init() {
        const self = this;

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_infrastructure_reviews = $(self.table.id).DataTable({
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
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-infrastructure-review");

        $(document).on("click", "[data-infrastructure-review]", function (e) {
            var obj = $(this);
            var option = obj.data("infrastructure-review");

            switch (option) {
                case "refresh-table":
                    self.tbl_infrastructure_reviews.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar item a la categoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find("select[name='category_id']").trigger("change");
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar item a la categoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infrastructure_reviews.row(fila).data();

                    if (self.item) {
                        self.item.list.data["category_id"];
                        obj_modal.find("select[name='category_id']").trigger("change");
                    }
                    obj_modal.find("form").find("[name='category_id']").prop("disabled", true);
                    obj_modal.find("form").find("[name='item_id']").prop("disabled", true);
                    obj_modal.find("form").find("[name='item']").prop("disabled", true);
                    obj_modal.find("form").find("[name='date']").prop("disabled", true);
                    $.each(datos, function (index, value) {
                        var inputElement = obj_modal.find(`[name="${index}"]`);
                        var isFileInput = inputElement.is(":file");
                        if (!isFileInput) {
                            inputElement.val(value || null);
                        }
                    });
                    console.log(datos);
                    setTimeout(function () {
                        obj_modal.find("select[name='item_id']").val(datos["item_id"]);
                    }, 1500);
                    break;
                case "delete-item":
                    var url = "/delete-infrastructure-review/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infrastructure_reviews.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_infrastructure_reviews.ajax.reload();
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
            var url = "/" + (submit == "add" ? "add" : "update") + "-infrastructure-review/";
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
                    self.tbl_infrastructure_reviews.ajax.reload();
                },
                error: function (xhr, status, error) {
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    console.error("Error en la petición AJAX:", error);
                },
            });
        });

        obj_modal.find("select[name='category_id']").on("change", function () {
            var category_id = $(this).val();
            if (self.item) {
                self.item.list.data["category_id"] = category_id;
                self.item.list.ajax.reload();
            }
        });
    }
}
