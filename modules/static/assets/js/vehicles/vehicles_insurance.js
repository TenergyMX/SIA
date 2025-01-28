class VehiclesInsurance {
    constructor(options) {
        const self = this;
        const defaultOptions = {
            data: {},
            table: {
                id: "#table_responsiva",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_insurance/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehicle__name" },
                    { title: "Num. Poliza", data: "policy_number" },
                    { title: "Aseguradora", data: "insurance_company" },
                    { title: "Fecha de inicio", data: "start_date" },
                    { title: "Fecha final", data: "end_date" },
                    {
                        title: "Vigencia",
                        data: function (d) {
                            return d["validity"] ? d["validity"] + " meses" : "";
                        },
                    },
                    { title: "Costo", data: "cost" },
                    {
                        title: "Responsable",
                        data: function (d) {
                            return d["responsible__first_name"] + " " + d["responsible__last_name"];
                        },
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: {
                data: { id: null },
            },
        };

        self.data = defaultOptions.data;

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };
            
            
            if (self.table.vehicle.id) {
                self.table.ajax.url = "/get_vehicle_insurance/";
                self.table.ajax.data = {
                    vehicle_id: self.table.vehicle.id,
                };

                // Buscar el índice del elemento que quieres eliminar
                let indexToRemove = self.table.columns.findIndex(function (column) {
                    return column.title === "Vehiculo" && column.data === "vehicle__name";
                });

                // Si se encontró el índice, eliminar el elemento del array
                if (indexToRemove !== -1) {
                    self.table.columns.splice(indexToRemove, 1);
                }
            }
        }

        if (options.vehicle) {
            self.vehicle = { ...defaultOptions.vehicle, ...options.vehicle };
        }

        self.init();
    }

    init() {
        const self = this;

        if (self.table) {
            self.tbl_insurance = $(self.table.id).DataTable({
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

        if (self.vehicle && self.vehicle.data.id) {
            $('#mdl_crud_insurance [name="vehicle_id"]').hide();
            $('#mdl_crud_insurance [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_insurance [name="vehicle_id"]').show();
            $('#mdl_crud_insurance [name="vehicle__name"]').hide();
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_insurance");

        $(document).on("click", "[data-vehicle-insurance]", function (e) {
            const obj = $(this);
            const option = obj.data("vehicle-insurance");

            switch (option) {
                case "refresh-table":
                    self.tbl_insurance.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Registrar Seguro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    if (self.vehicle && self.vehicle.data.vehicle_id) {
                        obj_modal.find('[name="vehicle_id"]').hide();
                        obj_modal.find('[name="vehicle__name"]').show();
                    } else {
                        obj_modal.find('[name="vehicle_id"]').show();
                        obj_modal.find('[name="vehicle__name"]').hide();
                    }

                    obj_modal.find("[name='vehicle_id']").val(self.vehicle.data.vehicle_id || null);
                    obj_modal
                        .find("[name='vehicle__name']")
                        .val(self.vehicle.data.vehicle__name || null);
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Actualizar Seguro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_insurance.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });
                    break;
                case "delete-item":
                    var url = "/delete_vehicle_insurance/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_insurance.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            console.log("success");
                            Swal.fire("Exito", message, "success");
                            self.tbl_insurance.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire(
                                "Oops",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        });
                    break;
                case "check":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("insuranceoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_insurance.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    obj_modal.find('[name="vehicle_id"]').hide();
                    obj_modal.find('[name="vehicle__name"]').show();
                    obj_modal.find('[name="insurance_date"]').prop("readonly", true);
                    break;
                case "show-info":
                    hideShow("#v-insurance-pane .info-details", "#v-insurance-pane .info");
                    break;
                case "show-info-details":
                    hideShow("#v-insurance-pane .info", "#v-insurance-pane .info-details");
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_insurance.row(fila).data();
                    var obj_div = $("#v-insurance-pane .info-details");

                    $.each(datos, function (index, value) {
                        obj_div
                            .find(`[data-key-value="${index}"]`)
                            .html(value || "---")
                            .removeClass();
                    });

                    // ! Actualizamos la info card
                    if (self.vehicle && self.vehicle.infoCard) {
                        self.vehicle.infoCard.vehicle.id = datos["vehicle_id"];
                        self.vehicle.infoCard.ajax.reload();
                    }
                    break;
                default:
                    console.log("Opción dezconocida:", option);
                    break;
            }
        });

        $(document).on("change", "[name='start_date']", function (e) {
            var startDate = new Date(obj_modal.find('[name="start_date"]').val());
            var validityMonths = parseInt(obj_modal.find("[name='validity']").val());

            if (isNaN(validityMonths)) {
                validityMonths = 3;
                obj_modal.find("[name='validity']").val(validityMonths);
            }

            // Sumar meses a la fecha de inicio
            startDate.setMonth(startDate.getMonth() + validityMonths);

            // Formatear la fecha como dd/mm/yyyy
            var day = startDate.getDate();
            var month = startDate.getMonth() + 1;
            var year = startDate.getFullYear();

            var formattedDay = day < 10 ? "0" + day : day;
            var formattedMonth = month < 10 ? "0" + month : month;

            // Establecer la fecha calculada en el campo end_date
            obj_modal
                .find("[name='end_date']")
                .val(year + "-" + formattedMonth + "-" + formattedDay);
        });

        obj_modal.find("form").on("submit", function (e) {
            alert("prueba");
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_insurance/";
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
                    self.tbl_insurance.ajax.reload();
                    obj_modal.modal("hide");
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
    }
}
