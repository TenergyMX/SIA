class ComputerEquipment {
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
                        return "/get-computer-equipment/";
                    },
                    data: function () {},
                    reload: function () {},
                },
            },
            list: {
                id: null,
                ajax: {},
            },

            // tarjetas
            cards: {
                id: "#computer_cards",
            },

            table: {
                id: "#computer_equipment_table",
                ajax: {
                    url: "/get-computers-equipment/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Identificador", data: "identifier" },
                    { title: "Área", data: "area__name", className: "toggleable" },
                    { title: "Equipo", data: "name", className: "toggleable" },
                    {
                        title: "Numero de serie",
                        data: "serial_number",
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "Responsable",
                        data: function (d) {
                            const firstName = d["current_responsible__first_name"]
                                ? d["current_responsible__first_name"]
                                : "";
                            const lastName = d["current_responsible__last_name"]
                                ? ` ${d["current_responsible__last_name"]}`
                                : "";
                            return `${firstName}${lastName}`;
                        },
                        className: "toggleable",
                    },
                    { title: "Tipo de equipo", data: "equipment_type", className: "toggleable" },
                    { title: "S.O.", data: "so", className: "toggleable", visible: false },
                    { title: "Marca", data: "brand", className: "toggleable" },
                    { title: "Modelo", data: "model", className: "toggleable" },
                    // {
                    //     title: "Fecha Adquisición",
                    //     data: "adquisition_date",
                    //     className: "toggleable",
                    // },
                    {
                        title: "Procesador",
                        data: "processor",
                        className: "toggleable",
                        visible: false,
                    },
                    { title: "RAM", data: "ram", className: "toggleable", visible: false },
                    {
                        title: "Actividad del Equipo",
                        data: "is_active",
                        render: function (data, type, row) {
                            return data ? "Activo" : "Inactivo";
                        },
                        className: "toggleable",
                    },
                    { title: "Estado", data: "equipment_status", className: "toggleable" },
                    {
                        title: "Comentarios",
                        data: "comments",
                        className: "toggleable",
                        visible: true,
                    },

                    {
                        title: "Ver factura",
                        data: "btn_view_factura",
                        orderable: false,
                        className: "text-center",
                    },

                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.cards) {
            self.cards = { ...defaultOptions.cards, ...options.cards };
        } else {
            self.cards = defaultOptions.cards;
        }

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
            self.infoCard.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-computer-equipment/",
                    data: self.data,
                    beforeSend: function () {},
                    success: function (response) {
                        var card = $(".card-info");

                        $.each(response["data"], function (index, value) {
                            card.find(`[data-key="${index}"]`).html(value).removeClass();
                            card.find(`[name='${index}']`).val(value || "-----");
                        });

                        // card.find(`[data-key="current_responsible__name"]`).html(`
                        //     ${response["data"]["current_responsible__first_name"]}
                        // `);

                        card.find(`[data-key="previous_responsible__first_name"]`).html(
                            function () {
                                var d = response["data"];
                                const firstName = d["previous_responsible__first_name"]
                                    ? d["previous_responsible__first_name"]
                                    : "";
                                const lastName = d["previous_responsible__last_name"]
                                    ? ` ${d["previous_responsible__last_name"]}`
                                    : "";
                                return `${firstName}${lastName}`;
                            }
                        );

                        card.find(`[data-key="current_responsible__first_name"]`).html(function () {
                            var d = response["data"];
                            const firstName = d["current_responsible__first_name"]
                                ? d["current_responsible__first_name"]
                                : "";
                            const lastName = d["current_responsible__last_name"]
                                ? ` ${d["current_responsible__last_name"]}`
                                : "";
                            return `${firstName}${lastName}`;
                        });

                        // card.find("picture img").attr("src", response["data"]["image_path"]);

                        self.data.id = response["data"]["id"] || null;
                        self.data.key = "";
                        self.data.name = response["data"]["name"];
                        self.data.model = response["data"]["model"];
                    },
                    error: function (xhr, status, error) {
                        console.log("error");
                    },
                });
            };
        }

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-computers-equipment/",
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

        self.init();
    }

    init() {
        const self = this;

        if (self.infoCard) {
            self.infoCard.ajax.reload();
        }

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_computerEquipment = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function (d) {
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

            self.loadCards();
            delete self.table;
        }

        self.setupEventHandlers();
    }

    loadCards() {
        const self = this;

        $.ajax({
            type: "GET",
            url: self.table.ajax.url,
            dataType: "json",
            success: function (response) {
                let html = "";

                $.each(response.data, function (i, item) {
                    const responsable =
                        (item.current_responsible__first_name || "") +
                        " " +
                        (item.current_responsible__last_name || "");

                    html += `
                    <div class="col-xl-4 col-lg-6 col-md-6">

                        <div class="card shadow-sm h-100">

                            <div class="card-body">

                                <div class="d-flex justify-content-between">

                                    <div class="d-flex">

                                        <div class="bg-primary text-white rounded p-2 me-2">
                                            <i class="fa-solid fa-laptop"></i>
                                        </div>

                                        <div>
                                            <h5 class="fw-bold mb-0">
                                                ${item.name || "-"}
                                            </h5>

                                            <small class="text-muted">
                                                ${item.identifier || "-"}
                                            </small>
                                        </div>

                                    </div>

                                    <span class="badge bg-primary">
                                        ${item.brand || "-"}
                                    </span>

                                </div>

                            </div>

                            <div class="px-3 mb-3">

                                <span class="badge bg-info">
                                    ${item.equipment_type || "-"}
                                </span>

                                <span class="badge ${
                                    item.equipment_status == "En uso" ? "bg-success" : "bg-warning"
                                }">
                                    ${item.equipment_status || "-"}
                                </span>

                                <span class="badge ${item.is_active ? "bg-success" : "bg-danger"}">

                                    ${item.is_active ? "Activo" : "Inactivo"}

                                </span>

                            </div>

                            <div class="row px-3">

                                <div class="col-6">
                                    <small class="text-muted">
                                        Área
                                    </small>

                                    <h6>
                                        ${item.area__name || "-"}
                                    </h6>

                                </div>

                                <div class="col-6">
                                    <small class="text-muted">
                                        Responsable
                                    </small>

                                    <h6>
                                        ${responsable}
                                    </h6>

                                </div>

                            </div>

                            <div class="row px-3 mt-3">

                                <div class="col-6">
                                    <small class="text-muted">
                                        Modelo
                                    </small>

                                    <h6>
                                        ${item.model || "-"}
                                    </h6>

                                </div>

                                <div class="col-6">
                                    <small class="text-muted">
                                        Sistema Operativo
                                    </small>

                                    <h6>
                                        ${item.so || "-"}
                                    </h6>

                                </div>

                            </div>

                            <div class="mx-3 mt-3 p-2 bg-light rounded">

                                ${item.serial_number || "-"}

                            </div>

                            <div class="p-3">

                                <strong>Comentarios:</strong><br>

                                ${item.comments || "Sin comentarios"}

                            </div>

                            <div class="card-footer bg-white">

                                <div class="d-flex justify-content-center gap-2">

                                    ${item.btn_view_factura}

                                    ${item.btn_action}

                                </div>

                            </div>

                        </div>

                    </div>
                    `;
                });

                $(self.cards.id).html(html);
            },
        });
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_computerSystem");

        $(document).on("click", "[data-computer-system]", function (e) {
            var obj = $(this);
            var option = obj.data("computer-system");

            switch (option) {
                case "refresh-table":
                    self.tbl_computerEquipment.ajax.reload();
                    self.loadCards();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar Equipo de computo");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar Equipo de computo");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_computerEquipment.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || null);
                        }
                    });

                    obj_modal
                        .find("[name='is_active']")
                        .val(datos["is_active"] == true ? "1" : "0");
                    break;
                case "dalete-item":
                    var url = "/delete-computer-system/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_computerEquipment.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_computerEquipment.ajax.reload();
                            self.loadCards();
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
            var url = "/" + (submit == "add" ? "add" : "update") + "-computer-system/";
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
                        Swal.fire("Error", "Ocurrio un error inesperado", "error");
                        return;
                    }
                    Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                    self.tbl_computerEquipment.ajax.reload();
                    self.loadCards();
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
