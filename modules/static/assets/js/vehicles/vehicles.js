class Vehicles {
    constructor(options) {
        "use strict";
        const self = this;
        const defaultOptions = {
            data: {
                id: null,
                vehicle_id: null,
                vehicle__name: null,
            },
            infoCard: {
                id: null,
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: function () {
                        return "/get_vehicles_info/";
                    },
                    data: function () {
                        return {
                            vehicle_id: defaultOptions.info.id || defaultOptions.info.vehicle_id,
                        };
                    },
                    reload: function () {},
                },
            },
            list: {
                id: "select[name='vehicle_id']",
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
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_info/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    {
                        title: "Alerta",
                        data: "alert",
                        className: "toggleable",
                        render: function (data, type, row) {
                            if (data) {
                                return '<i class="fa-solid fa-bell fa-shake" style="color:rgb(255, 174, 0)"></i>';
                            }
                            return "";
                        },
                    },

                    { title: "Nombre", data: "name", className: "toggleable" },
                    { title: "Marca", data: "brand", className: "toggleable" },
                    { title: "Modelo", data: "model", className: "toggleable" },
                    {
                        title: "Responsable",
                        data: "responsible__first_name",
                        className: "toggleable",
                    },
                    { title: "Placas", data: "plate", className: "toggleable" },
                    { title: "Año", data: "year", className: "toggleable" },
                    { title: "N. serie", data: "serial_number", className: "toggleable" },
                    { title: "Color", data: "color", className: "toggleable" },
                    {
                        title: "Propietario",
                        data: "owner__first_name",
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "STD/AT",
                        data: "transmission_type",
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "N. Poliza",
                        data: "policy_number",
                        className: "toggleable",
                        visible: false,
                    },
                    { title: "Vigencia", data: "validity", className: "toggleable" },
                    {
                        title: "Aseguradora",
                        data: "insurance_company",
                        className: "toggleable",
                        visible: false,
                    },
                    { title: "Kilometraje", data: "mileage", className: "toggleable" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            userPermissionTable: {},
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
            self.infoCard.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_vehicle_info/",
                    data: {
                        vehicle_id: self.infoCard.vehicle.id,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        if (response.alert && response.alert.missing_tables) {
                            const missingTables = response.alert.missing_tables;
                            missingTables.forEach(function (table) {
                                $(`#v-${table} .alert-icon`).html(
                                    '<i class="fa-regular fa-circle-exclamation" style="color:rgb(255, 174, 0);"></i>'
                                );
                            });
                        } else {
                            console.error("La respuesta no tiene la estructura esperada.");
                        }
                        // console.log(response["imgPath"]);
                        var card = $(".card-vehicle-info");

                        $.each(response["data"], function (index, value) {
                            card.find(`[data-key-value="${index}"]`).html(value).removeClass();
                            card.find(`[name='${index}']`).val(value);
                        });

                        card.find(`[data-key-value="responsible__name"]`).html(`
                            ${response["data"]["responsible__first_name"]}
                            ${response["data"]["responsible__last_name"]}
                        `);

                        card.find("picture img").attr("src", response["imgPath"]);

                        self.data.id = response["data"]["id"] || null;
                        self.data.vehicle_id = response["data"]["id"] || null;
                        self.data.vehicle__name = response["data"]["name"] || null;
                        self.data.vehicle__plate = response["data"]["plate"] || null;
                        self.data.key = " ";
                    },
                    error: function (xhr, status, error) {},
                });
            };
        }

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_vehicles_info/",
                    data: {
                        isList: true,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}" data-plate="${value["plate"]}">
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
            this.table = { ...defaultOptions.table, ...options.table };
            this.table.ajax.dataSrc = function (d) {
                $("span.vehicle-info-recordsTotal").html(d["recordsTotal"] || 0);
                return d["data"];
            };
        }

        if (options.userPermissionTable) {
            this.userPermissionTable = {
                ...defaultOptions.userPermissionTable,
                ...options.userPermissionTable,
            };
        }

        this.init();
    }

    init() {
        const self = this;
        self.input = {};

        if (self.infoCard && self.infoCard.vehicle.id) {
            self.infoCard.ajax.reload();
        }

        if (self.list) {
            self.list.ajax.reload();

            $("#mdl_crud_maintenance select[name='actions[]']").select2({
                closeOnSelect: false,
            });
        }

        if (self.table) {
            self.tbl_info = $(self.table.id).DataTable({
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

            // Incluimos librerias que modifican los inputs
            FilePond.registerPlugin(
                FilePondPluginImagePreview,
                FilePondPluginImageExifOrientation,
                FilePondPluginFileValidateSize,
                FilePondPluginImageEdit
            );

            // Configura las opciones de FilePond
            FilePond.setOptions({
                stylePanelAspectRatio: null,
                imagePreviewHeight: null,
                stylePanelLayout: "compact",
                labelIdle:
                    'Arrastra y suelta la imagen del vehículo o <span class="filepond--label-action">Examinar</span>',
            });

            self.input.pond = FilePond.create(document.querySelector(".filepond"), {
                allowMultiple: false,
                allowProcess: false,
            });

            // delete self.table;
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_offcanvas = $("#oc_crud_vechicles_info");

        $(document).on("click", "[data-vehicle-info]", function (e) {
            e.preventDefault();

            var obj = $(this);
            var option = obj.data("vehicle-info");

            switch (option) {
                case "refresh-table":
                    self.tbl_info.ajax.reload();
                    break;
                case "add-item":
                    obj_offcanvas.find("form")[0].reset();
                    obj_offcanvas.offcanvas("show");
                    obj_offcanvas.find("[type='submit']").hide();
                    obj_offcanvas.find("[name='add']").show();
                    break;
                case "update-item":
                    obj_offcanvas.find("form")[0].reset();
                    obj_offcanvas.offcanvas("show");
                    obj_offcanvas.find(".modal-header").html("Actualizar registro");
                    obj_offcanvas.find("[type='submit']").hide();
                    obj_offcanvas.find("[name='update']").show();

                    obj_offcanvas.find("[name='vehicle_id']").hide().prop("readonly", true);
                    obj_offcanvas.find("[name='vehicle__name']").show().prop("readonly", true);

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_info.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_offcanvas.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_offcanvas.find(`[name='${index}']`).val(value);
                        }
                    });

                    self.input.pond
                        .addFile(datos["image_path"])
                        .then((file) => {})
                        .catch((error) => {
                            Swal.fire("Error", "Error al cargar la imagen", error);
                        });
                    obj_offcanvas.find("[type='submit']").hide();
                    obj_offcanvas.find("[name='update']").show();

                    break;
                case "delete-item":
                    var url = "/delete_vehicle_info/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_info.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_info.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                default:
                    console.log("Opcion dezconocida:" + option);
            }
        });

        // submit
        obj_offcanvas.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_info/";
            var datos = new FormData(this);
            var files = self.input.pond.getFiles();
            if (files.length > 0) {
                var fileInput = files[0].file;
                if (fileInput && fileInput instanceof File) {
                    datos.set("cover-image", fileInput, fileInput.name);
                } else {
                    console.error("No se ha podido obtener un archivo válido.");
                }
            }

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
                    Swal.fire("Éxito", message, "success");
                    self.tbl_info.ajax.reload();
                    obj_offcanvas.offcanvas("hide");
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
        // end
    }
}
