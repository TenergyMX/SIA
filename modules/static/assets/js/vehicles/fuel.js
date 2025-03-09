class ComputerEquipment_fuel {
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
                    url: "/get-vehicle-fuels/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "vehículo", data: "vehicle__name", className: "toggleable" },
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
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Tipo de Combustible",
                        data: "fuel_type",
                        visible: false,
                        className: "toggleable",
                    },
                    { title: "Combustible (Litros)", data: "fuel", className: "toggleable" },
                    { title: "Costo", data: "cost", className: "toggleable" },
                    {
                        title: "Fecha",
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
                        title: "Comprobante de pago",
                        data: function (d) {
                            if (d["payment_receipt"]) {
                                return `<a href="/${d["payment_receipt"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Comprobante
                                </a>`;
                            } else {
                                return "Sin Comprobante";
                            }
                        },
                        orderable: false,
                        className: "toggleable",
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            graph: {
                id: "#chart",
                options: {
                    chart: {
                        type: "bar",
                        zoom: {
                            enabled: true,
                        },
                        toolbar: {
                            show: true,
                        },
                        width: "100%",
                    },
                    dataLabels: {
                        enabled: true,
                        style: {
                            fontSize: "12px",
                            colors: ["#333"],
                        },
                    },
                    annotations: {
                        points: [
                            {
                                x: "Barra 1",
                                label: {
                                    style: {},
                                },
                            },
                        ],
                    },
                    series: [],
                    title: {
                        text: "Combustible",
                    },
                    noData: {
                        text: "Loading...",
                    },
                },
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };
        }

        if (options.graph) {
            self.graph = { ...defaultOptions.graph, ...options.graph };
        }

        self.init();
    }

    init() {
        const self = this;
        var obj_modal = $("#mdl_crud_computer_equipment_maintenance");

        if (self.table) {
            self.tbl_fuel = $(self.table.id).DataTable({
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
                    "<'row'<'col-md'l><'col-md text-center'B><'col-md'f>>" +
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
                initComplete: function (settings, json) {
                    delete self.table;
                },
            });
        }

        if (self.graph) {
            self.chart = new ApexCharts(document.querySelector(self.graph.id), self.graph.options);
            self.chart.render();
        }

        var currentYear = new Date().getFullYear();
        var startYear = 2023;
        var $select = $(".card [name='year']");

        for (var i = currentYear; i >= startYear; i--) {
            $select.append('<option value="' + i + '">' + i + "</option>");
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-vehicle-fuel");

        $(document).on("click", "[data-sia-vehicle-fuel]", function (e) {
            var obj = $(this);
            var option = obj.data("sia-vehicle-fuel");

            switch (option) {
                case "refresh-table":
                    self.tbl_fuel.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Agregar registro");
                    obj_modal.find(":input").prop("disabled", false);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    obj_modal.find("[name='computerSystem_id']").prop("disabled", false);
                    obj_modal.find("[name='is_checked']").val(0).closest(".row").hide();

                    obj_modal.find("select").prop("required", true);
                    obj_modal.find("[name='date']").prop("required", true);
                    obj_modal.find("[name='payment_receipt']").prop("required", true);
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Actualizar registro");
                    obj_modal.find(":input").prop("disabled", false);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_fuel.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });
                    obj_modal.find("[name='payment_receipt']").prop("required", false);
                    break;
                case "delete-item":
                    var url = "/delete-vehicle-fuel/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_fuel.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_fuel.ajax.reload();
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
                    console.log("Opción dezconocida: " + option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-vehicle-fuel/";
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
                    Swal.fire("Éxito", message, "success");
                    obj_modal.modal("hide");
                    self.tbl_fuel.ajax.reload();
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

        $(".card-apexcharts form select").on("change", function (e) {
            e.preventDefault();
            var form = $(this).closest("form");
            var vehicle_id = form.find("[name='vehicle_id']").val();
            var type = form.find("[name='type']").val();
            var year = form.find("[name='year']").val();

            // start
            $.ajax({
                type: "GET",
                url: "/get-vehicle-fuels-charts/",
                data: {
                    vehicle_id: vehicle_id,
                    type: type,
                    year: year,
                },
                beforeSend: function () {
                    Swal.fire({
                        title: "Procesando...",
                        html: "Espere un momento por favor, mientras procesamos tu peticion",
                        allowOutsideClick: false,
                        didOpen: () => {
                            Swal.showLoading();
                        },
                    });
                },
                success: function (response) {
                    Swal.close();
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
                    var datos = response["data"]["chart"];
                    var dataLabelFormatter;

                    if (type === "Litros") {
                        dataLabelFormatter = function (value) {
                            return value + " L.";
                        };
                    } else if (type === "Pesos") {
                        dataLabelFormatter = function (value) {
                            return "$" + value.toLocaleString();
                        };
                    } else {
                        dataLabelFormatter = function (value) {
                            return value;
                        };
                    }

                    self.chart.updateOptions({
                        xaxis: {
                            title: {
                                text: "Meses",
                            },
                            categories: datos.xaxis.categories,
                        },
                        yaxis: {
                            title: {
                                text: datos.yaxis.title.text,
                            },
                        },
                        dataLabels: {
                            formatter: dataLabelFormatter,
                        },
                        tooltip: {
                            enabled: true,
                            y: {
                                formatter: function (value) {
                                    return dataLabelFormatter(value);
                                },
                            },
                        },
                    });

                    self.chart.updateSeries([
                        {
                            name: datos.name || "SIA",
                            data: datos.series.data,
                        },
                    ]);
                },
                error: function (xhr, status, error) {
                    Swal.close();
                    let errorMessage = "Ocurrió un error inesperado";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    }
                    Swal.fire("Error", errorMessage, "error");
                    console.log("Error en la petición AJAX:");
                    console.error("xhr:", xhr);
                },
            });
            // end
        });
    }
}
