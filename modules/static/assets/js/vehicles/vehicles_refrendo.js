class VehiclesRefrendo {
    constructor(options) {
        "use strict";
        const self = this;
        self.filtro_estado = "todos";

        const defaultOptions = {
            infoCard: {
                id: null,
                vehicle: { id: null },
                ajax: {
                    url: () => "/get_vehicles_refrendo/",
                    data: (d) => ({
                        ...d,
                        vehicle_id: self.vehicle?.data?.id || self.vehicle?.id || null,
                        tipo_carga: self.filtro_estado,
                    }),
                },
            },
            table: {
                id: "#table_refrendo",
                vehicle: { id: null },
                ajax: {
                    url: "/get_vehicles_refrendo/",
                    dataSrc: "data",
                    data: (d) => ({
                        ...d,
                        vehicle_id: self.vehicle?.data?.id || self.vehicle?.id || null,
                        tipo_carga: self.filtro_estado,
                    }),
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehiculo__name" },
                    { title: "Fecha de pago", data: "fecha_pago" },
                    { title: "Monto", data: "monto" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: { id: null, data: { id: null } },
        };

        // Merge opciones
        self.vehicle = { ...defaultOptions.vehicle, ...(options.vehicle || {}) };
        self.table = { ...defaultOptions.table, ...(options.table || {}) };
        self.infoCard = { ...defaultOptions.infoCard, ...(options.infoCard || {}) };

        // ---- Caso: tabla de un solo vehículo ----
        if (self.table.vehicle.id) {
            self.vehicle.id = self.table.vehicle.id;

            self.vehicle.data = {
                id: self.table.vehicle.id,
                vehiculo_id: self.table.vehicle.id,
                vehiculo__name: "",
            };

            self.table.ajax.url = "/get_vehicle_refrendo/";
            self.table.ajax.data = (d) => ({
                ...d,
                vehicle_id: self.table.vehicle.id,
                tipo_carga: self.filtro_estado,
            });

            const indexToRemove = self.table.columns.findIndex(
                (column) => column.title === "Vehículo" && column.data === "vehiculo__name"
            );
            if (indexToRemove !== -1) {
                self.table.columns.splice(indexToRemove, 1);
            }
        }

        self.init();
    }

    init() {
        const self = this;
        this.driverSia();
        this.driverSiaFormulario();
        console.log(self.vehicle);
        // Inicializar contadores
        self.updateCounters({
            total: 0,
            pagadas: 0,
            vencidas: 0,
            proximas: 0,
            pendientes: 0,
        });

        if (self.table) {
            self.tbl_refrendo = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,

                    dataSrc: function (json) {
                        // Solo actualiza contadores si estás en "todos"
                        if (json.counters && self.filtro_estado === "todos") {
                            self.updateCounters(json);
                        }
                        return json.data;
                    },

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

                    data: function (d) {
                        return {
                            ...d,
                            vehicle_id: self.vehicle?.data?.id || null,
                            tipo_carga: self.filtro_estado,
                        };
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
            });
            delete self.table;
        }

        // Eventos de filtro
        $(".filter-card")
            .off("click")
            .on("click", function () {
                const status = $(this).data("status");
                $(".filter-card").removeClass("active");
                $(this).addClass("active");
                self.filtro_estado = status;

                if (self.tbl_refrendo) {
                    self.tbl_refrendo.ajax.reload();
                }
            });

        if (self.vehicle && self.vehicle.data.vehicle_id) {
            $('#mdl_crud_verificacion [name="vehiculo_id"]').hide();
            $('#mdl_crud_verificacion [name="vehiculo__name"]').show();
        } else {
            $('#mdl_crud_verificacion [name="vehiculo_id"]').show();
            $('#mdl_crud_verificacion [name="vehiculo__name"]').hide();
        }

        self.setupEventHandlers();

        //this.loadVehiclesOpions();
    }

    loadVehiclesOpions() {
        const self = this;
        var datos = new FormData();
        datos.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
        datos.append("id", self.vehicle.data.id);
        $.ajax({
            type: "POST",
            url: "/get-vehicles/list/",
            data: datos,
            processData: false,
            contentType: false,
            success: function (response) {
                console.log(response);
                $('#mdl_crud_refrendo [name="vehiculo_id"]')
                    .show()
                    .attr("disabled", false)
                    .html(response.option);
                $('#mdl_crud_refrendo [name="vehiculo__name"]').hide();
            },
            error: function (xhr, status, error) {
                Swal.fire(
                    "Error del servidor",
                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                    "error"
                );
            },
        });
    }

    driverSia() {
        $(".btn-driver").on("click", function () {
            const driver = window.driver.js.driver;
            const driverObj = driver({
                showProgress: true,
                steps: [
                    {
                        element: ".drive-1",
                        popover: {
                            title: "Todas los refrendos",
                            description:
                                "Se muestra un registro por vehiculo, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-2",
                        popover: {
                            title: "Refrendos evaluados",
                            description:
                                "Se muestran todos lso refrendos evaluados, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-3",
                        popover: {
                            title: "Refrendos vencidos",
                            description:
                                "Se muestran todos los refrendos vencidos, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-4",
                        popover: {
                            title: "Refrendos próximos a evaluar",
                            description:
                                "Se muestran los refrendos proximos a evaluar, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-5",
                        popover: {
                            title: "Agregar Refrendo",
                            description: "Agrega un nuevo refrendo a traves del formulario.",
                        },
                    },
                ],
                nextBtnText: "Siguiente",
                prevBtnText: "Anterior",
                doneBtnText: "Listo",
            });
            driverObj.drive();
        });
    }

    driverSiaFormulario() {
        const modal = $("#mdl_crud_refrendo").length;
        if (modal == 1) {
            $(".btn-drive-form").on("click", function () {
                const driver = window.driver.js.driver;
                const driverObj = driver({
                    showProgress: true,
                    steps: [
                        {
                            element: ".drive-6",
                            popover: {
                                title: "Vehículo",
                                description: "Selecciona un vehículo para agregar un refrendo.",
                            },
                        },
                        {
                            element: ".drive-7",
                            popover: {
                                title: "Fecha de pago",
                                description: "Ingresa una fecha a realizar el pago del refrendo.",
                            },
                        },
                        {
                            element: ".drive-8",
                            popover: {
                                title: "Monto pagado",
                                description: "Ingrese el monto pagado por el refrendo.",
                            },
                        },
                        {
                            element: ".drive-9",
                            popover: {
                                title: "Comprobante de pago",
                                description: "Adjunta un comprobante de pago en caso de tenerlo.",
                            },
                        },
                    ],
                    nextBtnText: "Siguiente",
                    prevBtnText: "Anterior",
                    doneBtnText: "Listo",
                });
                driverObj.drive();
            });
        }
    }

    updateCounters(data) {
        const counters = data.counters || data;
        const total = counters.total || 0;
        const totalVehiculos = counters.total_vehiculos || 0;
        $("#counter-todas").text(`${total} de ${totalVehiculos} vehículos`);
        $("#counter-pagadas").text(counters.pagadas || 0);
        $("#counter-vencidas").text(counters.vencidas || 0);
        $("#counter-proximas").text(counters.proximas || 0);
        $("#counter-pendientes").text(counters.pendientes || 0);
        $("#counter-sin_refrendo").text(
            `${counters.sin_refrendo || 0} de ${
                counters.total_vehiculos_sin_refrendo || 0
            } vehículos`
        );
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_refrendo");

        $(document).on("click", "[data-vehicle-refrendo]", function (e) {
            var obj = $(this);
            var option = obj.data("vehicle-refrendo");

            switch (option) {
                case "refresh-table":
                    self.tbl_refrendo.ajax.reload();
                    break;

                case "add-item":
                    // guarda el id y nombre del vehículo seleccionado
                    const vehiculoId = self?.vehicle?.id || null;
                    const vehiculoNombre = self?.vehicle?.name || null;

                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal
                        .find(".modal-header .modal-title")
                        .html("Registrar refrendo vehicular");

                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find('[name="actions[]"]').trigger("change");

                    const selectVehiculo = obj_modal.find('[name="vehiculo_id"]');

                    // si tienes el id del vehículo, vuelve a setearlo en el select
                    if (vehiculoId) {
                        selectVehiculo.val(vehiculoId).trigger("change");

                        // si quieres que quede fijo y no seleccionable:
                        // selectVehiculo.prop("disabled", true);
                    }

                    initRefrendoCalendar(obj_modal.find("[name='fecha_pago']"));
                    break;

                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_refrendo.row(fila).data();
                    var select = obj_modal.find('select[name="vehiculo_id"]');

                    if (select.find(`option[value="${datos["vehiculo_id"]}"]`).length < 1) {
                        select.append(
                            `<option value="${datos["vehiculo_id"]}">${datos["vehiculo__name"]}</option>`
                        );
                    }

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });

                    if (self.vehicle && self.vehicle.data.id) {
                        obj_modal.find('[name="vehiculo_id"]').hide();
                        obj_modal.find('[name="vehiculo__name"]').show();
                    } else {
                        obj_modal.find('[name="vehiculo_id"]').show();
                        obj_modal.find('[name="vehiculo__name"]').hide();
                    }
                    initRefrendoCalendar(obj_modal.find("[name='fecha_pago']"));

                    break;
                case "delete-item":
                    var url = "/delete_vehicle_refrendo/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_refrendo.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_refrendo.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                default:
                    console.log("Opcion dezconocida:" + option);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_refrendo/";
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
                    self.tbl_refrendo.ajax.reload();
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

function initRefrendoCalendar(inputElement) {
    if (inputElement.length) {
        if (inputElement[0]._flatpickr) {
            inputElement[0]._flatpickr.destroy();
        }
        inputElement.flatpickr({
            dateFormat: "Y-m-d",
            locale: "es",
            disable: [
                function (date) {
                    return date.getMonth() >= 3;
                },
            ],
        });
    }
}
