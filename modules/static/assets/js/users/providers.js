class Providers {
    constructor(options) {
        "use strict";
        const self = this;
        const defaultOptions = {
            data: {
                id: null,
            },
            list: {
                id: null,
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: function () {
                        return "/get_vehicles_info/";
                    },
                },
            },
            table: {
                id: null,
                ajax: {
                    url: "/get-providers/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Nombre", data: "name" },
                    {
                        title: "Telefono",
                        data: "phone_number",
                        render: function (data, type, row) {
                            if (!data) return "";
                            // Asegúrate de que el número tiene al menos 10 dígitos
                            let cleaned = ("" + data).replace(/\D/g, "");
                            let match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
                            if (match) {
                                return match[1] + " " + match[2] + " " + match[3];
                            }
                            return data;
                        },
                    },
                    { title: "Dirección", data: "address" },
                    {
                        title: "Estatus",
                        data: "is_active",
                        render: function (data, type, row) {
                            return data
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
                    url: "/get-providers/",
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
            self.tbl_providers = $(self.table.id).DataTable({
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
        var obj_modal = $("#mdl_crud_provider");

        $(document).on("click", "[data-sia-provider]", function (e) {
            e.preventDefault();
            var obj = $(this);
            var option = obj.data("sia-provider");

            switch (option) {
                case "refresh-table":
                    self.tbl_providers.ajax.reload();
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
                    var datos = self.tbl_providers.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    obj_modal
                        .find("[name='is_active']")
                        .val((datos["is_active"] = true ? "1" : "0"));
                    break;
                case "delete-item":
                    var url = "/delete-provider/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_providers.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_providers.ajax.reload();
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
                default:
                    console.log("Opcion dezconocida:" + option);
            }
        });

        $("#mdl_crud_provider form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-provider/";
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
                    Swal.fire("Exito", message, "success");
                    obj_modal.modal("hide");
                    self.tbl_providers.ajax.reload();
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
                complete: function (data) {
                    obj_modal.find("[type='submit']").prop("disabled", false);
                },
            });
        });
    }
}
