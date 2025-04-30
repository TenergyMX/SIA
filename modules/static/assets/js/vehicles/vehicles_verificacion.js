class VehiclesVerificacion {
    constructor(options) {
        "use strict";

        const self = this;
        self.filtro_estado = "todos";

        const defaultOptions = {
            infoCard: {
                id: null,
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: function () {
                        return "/get_vehicles_verificacion/";
                    },
                    data: function (d) {
                        return {
                            ...d,
                            vehicle_id: self.vehicle?.data?.id || null,
                            tipo_carga: self.filtro_estado,
                        };
                    },
                },
            },

            table: {
                id: "#table_verificacion",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_verificacion/",
                    dataSrc: "data",
                    data: function (d) {
                        return {
                            ...d,
                            vehicle_id: self.vehicle?.data?.id || null,
                            tipo_carga: self.filtro_estado,
                        };
                    },
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehiculo__name" },
                    { title: "Engomado", data: "engomado" },
                    { title: "Periodo", data: "periodo" },
                    { title: "Fecha de pago", data: "fecha_pago" },
                    { title: "Lugar", data: "lugar" },
                    { title: "Monto", data: "monto" },
                    { title: "Estatus", data: "status" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: {
                data: { id: null },
            },
        };

        // Merge de opciones
        this.table = { ...defaultOptions.table, ...(options.table || {}) };
        this.vehicle = { ...defaultOptions.vehicle, ...(options.vehicle || {}) };

        if (options.infoCard) {
            this.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
        }

        // Configuración especial si hay un vehicle.id
        if (this.table.vehicle?.id) {
            this.table.ajax.url = "/get_vehicle_verificacion/";
            const originalDataFn = this.table.ajax.data;
            this.table.ajax.data = function (d) {
                const baseParams = originalDataFn ? originalDataFn(d) : d;
                return {
                    ...baseParams,
                    vehicle_id: self.table.vehicle.id,
                };
            };

            // Eliminar columna de vehículo si es necesario
            const indexToRemove = this.table.columns.findIndex(
                (column) => column.title === "Vehículo" && column.data === "vehiculo__name"
            );
            if (indexToRemove !== -1) {
                this.table.columns.splice(indexToRemove, 1);
            }
        }

        this.init();
    }

    init() {
        const self = this;

        // Inicializar contadores
        self.updateCounters({
            total: 0,
            pagadas: 0,
            vencidas: 0,
            proximas: 0,
            pendientes: 0,
        });

        if (self.table) {
            self.tbl_verificacion = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    data: function (d) {
                        const baseData =
                            typeof self.table.ajax.data === "function"
                                ? self.table.ajax.data(d)
                                : self.table.ajax.data || {};
                        return {
                            ...d,
                            ...baseData,
                            tipo_carga: self.filtro_estado,
                        };
                    },
                    dataSrc: function (json) {
                        // Actualizar contadores cuando se cargan los datos
                        if (json.counters) {
                            self.updateCounters(json);
                        }
                        return json.data;
                    },
                },
                columns: self.table.columns,
                order: [[0, "desc"]],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
            });
        }

        // Configurar eventos de filtro
        $(".filter-card")
            .off("click")
            .on("click", function () {
                const status = $(this).data("status");
                $(".filter-card").removeClass("active");
                $(this).addClass("active");
                self.filtro_estado = status;

                if (self.tbl_verificacion) {
                    self.tbl_verificacion.ajax.reload();
                }
            });

        if (self.vehicle && self.vehicle.data.id) {
            $('#mdl_crud_verificacion [name="vehiculo_id"]').hide();
            $('#mdl_crud_verificacion [name="vehiculo__name"]').show();
        } else {
            $('#mdl_crud_verificacion [name="vehiculo_id"]').show();
            $('#mdl_crud_verificacion [name="vehiculo__name"]').hide();
        }

        // Cargar calendario de verificación
        try {
            $.ajax({
                type: "GET",
                url: "/static/assets/json/calendario_de_verificacion.json",
                success: function (response) {
                    self.cv = response["data"];
                },
                error: function () {
                    console.error("Error al cargar calendario de verificación");
                },
            });
        } catch (error) {
            console.error("Error al obtener calendario:", error);
        }

        $('#mdl_crud_verificacion [name="vehiculo__name"]').prop("readonly", true);
        self.setupEventHandlers();
    }

    updateCounters(data) {
        const counters = data.counters || data;

        $("#counter-todas").text(counters.total || 0);
        $("#counter-pagadas").text(counters.pagadas || 0);
        $("#counter-vencidas").text(counters.vencidas || 0);
        $("#counter-proximas").text(counters.proximas || 0);
        $("#counter-pendientes").text(counters.pendientes || 0);
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_verificacion");

        $(document).on("click", "[data-vehicle-verificacion]", function (e) {
            const obj = $(this);
            const option = obj.data("vehicle-verificacion");

            switch (option) {
                case "refresh-table":
                    if (self.tbl_verificacion) {
                        self.tbl_verificacion.ajax.reload();
                    }
                    break;

                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar verificación vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    if (self.vehicle && self.vehicle.data.id) {
                        obj_modal.find('[name="vehiculo_id"]').hide();
                        obj_modal.find('[name="vehiculo__name"]').show();
                    } else {
                        obj_modal.find('[name="vehiculo_id"]').show();
                        obj_modal.find('[name="vehiculo__name"]').hide();
                    }

                    obj_modal
                        .find("[name='vehiculo_id']")
                        .val(self.vehicle.data.vehicle_id || null);
                    obj_modal
                        .find("[name='vehiculo__name']")
                        .val(self.vehicle.data.vehicle__name || null);
                    $('select[name="vehiculo_id"]').trigger("change");
                    $("select[name='engomado']").trigger("change");
                    break;

                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_verificacion.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });

                    obj_modal.find('[name="vehiculo_id"]').hide();
                    obj_modal.find('[name="vehiculo__name"]').show();
                    obj_modal.find('[name="engomado"]').trigger("change");
                    break;

                case "delete-item":
                    var url = "/delete_vehicle_verificacion/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_verificacion.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Éxito", message, "success");
                            self.tbl_verificacion.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;

                default:
                    console.log("Opción desconocida:", option);
            }
        });

        $(document).on("change", "[name='engomado']", function (e) {
            let color = $(this).val();
            let bg = {
                Amarillo: "yellow",
                Rosa: "pink",
                Rojo: "red",
                Verde: "green",
                Azul: "blue",
            };
            $(".engomado-color-bg").css("background-color", color ? bg[color] : "");
        });

        $(document).on("change", "[name='vehiculo_id']", function (e) {
            const obj = $(this);
            const option = obj.find("option:selected");
            var plate = option.data("plate");
            var d = self.getUltimoDigito(plate);

            if (self.cv && self.cv[d]) {
                var datos = self.cv[d];
                obj_modal.find("[name='engomado']").val(datos["engomado_ES"]).trigger("change");
                obj_modal.find(".col-alert-verifiacion .message").html(`
                    Verificación:<br>
                    1er semestre (${datos["s1"][0]["month_name_ES"]} - ${datos["s1"][1]["month_name_ES"]})<br>
                    2do semestre (${datos["s2"][0]["month_name_ES"]} - ${datos["s2"][1]["month_name_ES"]})
                `);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_verificacion/";
            var datos = new FormData(this);

            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (!response.success) {
                        const message =
                            response.error?.message ||
                            response.warning?.message ||
                            "Ocurrió un error inesperado";
                        const type = response.error ? "error" : "warning";
                        Swal.fire(type === "error" ? "Error" : "Advertencia", message, type);
                        return;
                    }

                    Swal.fire("Éxito", "Se han guardado los datos correctamente", "success");
                    self.tbl_verificacion.ajax.reload();
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

    getUltimoDigito(plate) {
        if (!plate) return "0"; // Valor por defecto

        for (var i = plate.length - 1; i >= 0; i--) {
            var char = plate[i];
            if (/\d/.test(char)) {
                return char;
            }
        }
        return "0"; // Valor por defecto si no encuentra dígitos
    }
}
