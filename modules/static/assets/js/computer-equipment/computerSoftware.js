class ComputerSoftware {
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
                id: "#softwares_table",
                ajax: {
                    url: "/get_softwares/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Funcion", data: "function", className: "toggleable" },
                    { title: "Nombre", data: "name", className: "toggleable" },
                    { title: "Versión", data: "version", className: "toggleable" },
                    { title: "Total", data: "max_installations", className: "toggleable" },
                    { title: "Instaladas", data: "installation_count", className: "toggleable" },
                    { title: "Descripción", data: "description", className: "toggleable" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            table_installations: {
                ajax: {
                    url: "/get_software_installations/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Equipo", data: "computerSystem__name", className: "toggleable" },
                    { title: "Tipo", data: "software__function", className: "toggleable" },
                    { title: "Nombre", data: "software__name", className: "toggleable" },
                    {
                        title: "Identificador",
                        data: "software_identifier",
                        className: "toggleable",
                    },
                    {
                        title: "Fecha de instalación",
                        data: "installation_date",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                        className: "toggleable",
                    },
                    {
                        title: "Versión",
                        data: "software__version",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Descripción",
                        data: "software__description",
                        visible: false,
                        className: "toggleable",
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

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_softwares/",
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

        if (options.table_installations) {
            if (self.computer.data && self.computer.data.computerSystem_id) {
                self.data["mode"] = "computer-to-software";

                // Buscar el índice del elemento que quieres eliminar
                let indexToRemove = 0;

                // Si se encontró el índice, eliminar el elemento del array
                if (indexToRemove !== -1) {
                    defaultOptions.table_installations.columns.splice(indexToRemove, 1);
                }
            }

            self.table_installations = {
                ...defaultOptions.table_installations,
                ...options.table_installations,
            };

            self.table_installations.ajax.data = self.data;
        }

        self.init();
    }

    init() {
        const self = this;
        var obj_modal = $("#mdl_crud_software");
        var obj_modal2 = $("#mdl_crud_softwareInstallation");

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_software = $(self.table.id).DataTable({
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
                dom:
                    "<'row justify-content-between'<'col-md-auto'l><'col-md-auto'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
            });

            delete self.table;
        }

        if (self.table_installations) {
            self.tbl_software_installations = $(self.table_installations.id).DataTable({
                ajax: {
                    url: self.table_installations.ajax.url,
                    dataSrc: self.table_installations.ajax.dataSrc,
                    data: function (d) {
                        return self.data;
                    },
                },
                columns: self.table_installations.columns,
                order: [
                    [0, "asc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                dom:
                    "<'row justify-content-between'<'col-md-auto'l><'col-md-auto text-center'B><'col-md-auto'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
                buttons: [
                    {
                        extend: "colvis",
                        text: "columnas",
                        columns: function (idx, data, node) {
                            return $(node).hasClass("toggleable");
                        },
                        className: "btn-sm",
                    },
                ],
                initComplete: function () {
                    $(".dt-buttons.btn-group").removeClass("btn-group");
                    $(".dt-buttons .btn-group").removeClass("btn-group");
                    delete self.table_installations;
                },
            });
        }

        if (self.data && self.data["mode"] == "computer-to-software") {
            obj_modal2.find("[name='add']").show();
            obj_modal2.find("[name='software_id']").show();
            obj_modal2.find("[name='software__name']").hide();
            obj_modal2.find("[name='computerSystem_id']").hide();
            obj_modal2.find("[name='computerSystem__name']").show();
        } else {
            obj_modal2.find("[name='software__name']").hide();
            obj_modal2.find("[name='computerSystem__name']").hide();
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_software");
        var obj_modal2 = $("#mdl_crud_softwareInstallation");

        $(document).on("click", "[data-computer-software]", function (e) {
            var obj = $(this);
            var option = obj.data("computer-software");
            console.log("click");

            switch (option) {
                case "refresh-table":
                    self.tbl_software.ajax.reload();
                    break;
                case "refresh-details-table":
                case "refresh-installation-table":
                    self.tbl_software_installations.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar Software");
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
                    var datos = self.tbl_software.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "-----");
                        }
                    });

                    obj_modal
                        .find("[name='is_unlimited']")
                        .val(datos["is_unlimited"] == true ? "1" : "0");
                    break;
                case "delete-item":
                    var url = "/delete_computer_software/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_software.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                case "add-item-installation":
                    obj_modal2.modal("show");
                    obj_modal2.find("form")[0].reset();
                    obj_modal2.find(".modal-header").html("Agregar");
                    obj_modal2.find("[type='submit']").hide();
                    obj_modal2.find("[name='add']").show();

                    if (self.computer && self.computer.data && self.computer.data.name) {
                        self.data["computerSystem__name"] = self.computer.data.name;
                    }

                    if (self.data && self.data["mode"] == "computer-to-software") {
                        var select = obj_modal2.find("select[name='computerSystem_id']");
                        var valueToSelect = self.data.computerSystem_id;

                        if (select.find(`option[value="${valueToSelect}"]`).length === 0) {
                            var newOption = document.createElement("option");
                            newOption.value = valueToSelect;
                            newOption.text = self.data["computerSystem__name"] || "Equipo";
                            select[0].appendChild(newOption);
                        }
                        select.val(valueToSelect);
                    }
                    obj_modal2
                        .find("[name='computerSystem__name']")
                        .val(self.data["computerSystem__name"] || "Equipo");
                    break;
                case "update-item-installation":
                    obj_modal2.modal("show");
                    obj_modal2.find("form")[0].reset();
                    obj_modal2.find(".modal-header").html("Actualizar");
                    obj_modal2.find("[type='submit']").hide();
                    obj_modal2.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_software_installations.row(fila).data();

                    var select = obj_modal2.find("select[name='computerSystem_id']");
                    if (select.find(`option[value="${datos["computerSystem_id"]}"]`).length === 0) {
                        select.append(
                            $("<option>", {
                                value: datos["computerSystem_id"],
                                text: datos["computerSystem__name"] || "Equipo",
                            })
                        );
                    }
                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal2.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal2.find(`[name='${index}']`).val(value || "-----");
                        }
                    });
                    break;
                case "delete-item-installation":
                    var url = "/delete_software_installation/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_software_installations.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_software_installations.ajax.reload();
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
                case "show-computer-to-software":
                    // Esta tabla indicaría qué software está instalado en cada equipo.
                    // Es decir, por cada equipo, podrías listar todo el software que tiene instalado.
                    break;
                case "show-software-to-computer":
                    // Esta tabla indicaría en qué equipos está instalado cada software.
                    // Es decir, por cada software, podrías listar todos los equipos en los que está instalado
                    break;
                default:
                    console.log("Opción dezconocida: " + option);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_software/";
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
                    self.tbl_software.ajax.reload();
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

        obj_modal2.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_software_installation/";
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
                    self.tbl_software_installations.ajax.reload();
                    obj_modal2.modal("hide");
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
