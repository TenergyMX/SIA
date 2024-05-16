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
                    { title: "Id", data: "id", visible: false },
                    { title: "Nombre", data: "name" },
                    { title: "Marca", data: "brand" },
                    { title: "Modelo", data: "model" },
                    { title: "Responsable", data: "responsible__first_name" },
                    { title: "Placas", data: "plate" },
                    { title: "Año", data: "year" },
                    { title: "N. serie", data: "serial_number" },
                    { title: "Color", data: "color" },
                    { title: "Propietario", data: "owner__first_name" },
                    { title: "STD/AT", data: "transmission_type" },
                    { title: "N. Polisa", data: "policy_number" },
                    { title: "Vigencia", data: "validity" },
                    { title: "Aseguradora", data: "insurance_company" },
                    { title: "Kilometraje", data: "mileage" },
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
                        var card = $(".card-vehicle-info");

                        $.each(response["data"], function (index, value) {
                            card.find(`[data-key-value="${index}"]`).html(value).removeClass();
                            card.find(`[name='${index}']`).val(value);
                        });

                        card.find(`[data-key-value="responsible__name"]`).html(`
                            ${response["data"]["responsible__first_name"]}
                            ${response["data"]["responsible__last_name"]}
                        `);
                        card.find("picture img").attr("src", response["data"]["image_path"]);

                        self.data.id = response["data"]["id"] || null;
                        self.data.vehicle_id = response["data"]["id"] || null;
                        self.data.vehicle__name = response["data"]["name"] || null;
                        self.data.vehicle__plate = response["data"]["plate"] || null;
                        self.data.key = "Goku eta vaina e seria";
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
                initComplete: function (settings, json) {
                    $("#table_vehicles_info_wrapper .row:eq(1)").addClass("table-responsive mb-2");
                },
                // responsive: true,
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
                    obj_offcanvas.find(".modal-header").html("Registrar maintenanceoria vehicular");
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
                            console.error("Error al cargar la imagen:", error);
                            Swal.fire("Error", "Error al cargar la imagen", "error");
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

            if (files.length !== 0) {
                var fileInput = self.input.pond.getFiles()[0].file;
                datos.set("cover-image", fileInput);
            }

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
                    self.tbl_info.ajax.reload();
                    obj_offcanvas.modal("hide");
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
