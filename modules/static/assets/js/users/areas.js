class Areas {
    constructor(options) {
        "use strict";
        const self = this;
        const defaultOptions = {
            data: {
                id: null,
            },
            list: {
                ajax: {
                    url: function () {
                        return "/get_areas/";
                    },
                },
            },
            table: {
                id: null,
                ajax: {
                    url: "/get_areas/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Código", data: "code" },
                    { title: "Nombre", data: "name" },
                    { title: "Descripción", data: "description" },
                    {
                        title: "Estatus",
                        data: function (d) {
                            return d["is_active"]
                                ? '<span class="badge bg-outline-success">Activo</span>'
                                : '<span class="badge bg-outline-danger">Inactivo</span>';
                        },
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
                    url: "/get_areas/",
                    data: {
                        isList: true,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
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
            self.table = { ...defaultOptions.table, ...options.table };
        }

        this.init();
    }

    init() {
        const self = this;

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_areas = $(self.table.id).DataTable({
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

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_area");

        $(document).on("click", "[data-area]", function (e) {
            e.preventDefault();
            var obj = $(this);
            var option = obj.data("area");

            switch (option) {
                case "refresh-table":
                    self.tbl_areas.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_areas.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    obj_modal
                        .find("[name='is_active']")
                        .val(datos["is_active"] == true ? "1" : "0");
                    break;
                case "delete-item":
                    break;
                default:
                    console.log("Opcion dezconocida:" + option);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_area/";
            var datos = new FormData(this);

            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,
                beforeSend: function () {
                    obj_modal.find("[type='submit']").prop("disabled", true);
                },
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
                    self.tbl_areas.ajax.reload();
                },
                error: function (xhr, status, error) {
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    console.error("Error en la petición AJAX:", error);
                },
                complete: function (data) {
                    obj_modal.find("[type='submit']").prop("disabled", false);
                },
            });
        });
    }
}
