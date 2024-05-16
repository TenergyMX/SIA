class VehiclesVerificacion {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            table: {
                id: "#table_verificacion",
                ajax: {
                    url: "/get_vehicles_verificacion/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehiculo", data: "vehiculo__name" },
                    { title: "Engomado", data: "engomado" },
                    { title: "Periodo", data: "periodo" },
                    { title: "Fecha de pago", data: "fecha_pago" },
                    { title: "lugar", data: "lugar" },
                    { title: "Monto", data: "monto" },
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

            if (self.vehicle && self.vehicle.data.id) {
                self.table.ajax.url = "/get_vehicle_verificacion/";
                self.table.ajax.data = { vehicle_id: self.table.vehicle.id };
                self.vehicle.data = { vehicle_id: self.table.vehicle.id };

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
            self.tbl_verificacion = $(self.table.id).DataTable({
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
            $('#mdl_crud_verificacion [name="vehiculo_id"]').hide();
            $('#mdl_crud_verificacion [name="vehiculo__name"]').show();
        } else {
            $('#mdl_crud_verificacion [name="vehiculo_id"]').show();
            $('#mdl_crud_verificacion [name="vehiculo__name"]').hide();
        }

        try {
            $.ajax({
                type: "GET",
                url: "/static/assets/json/calendario_de_verificacion.json",
                success: function (response) {
                    self.cv = response["data"];
                },
            });
        } catch (error) {
            console.log("error al obtener calendario");
        }

        $('#mdl_crud_verificacion [name="vehiculo__name"]').prop("readonly", true);
        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_verificacion");

        $(document).on("click", "[data-vehicle-verificacion]", function (e) {
            const obj = $(this);
            const option = obj.data("vehicle-verificacion");

            switch (option) {
                case "refresh-table":
                    self.tbl_verificacion.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar verificacionoria vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find('[name="actions[]"]').trigger("change");

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
                            Swal.fire("Exito", message, "success");
                            self.tbl_verificacion.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                default:
                    console.log("Opcion dezconocida:" + option);
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
            // e.preventDefault();
            const obj = $(this);
            const option = obj.find("option:selected");
            var plate = option.data("plate");
            var d = self.getUltimoDigito(plate);
            var datos = self.cv[d];

            obj_modal.find("[name='engomado']").val(datos["engomado_ES"]).trigger("change");
            obj_modal.find(".col-alert-verifiacion .message").html(`
                Verificación:
                1er semestre (${datos["s1"][0]["month_name_ES"]} - ${datos["s1"][1]["month_name_ES"]}) y
                2do semestre (${datos["s2"][0]["month_name_ES"]} - ${datos["s2"][1]["month_name_ES"]})
            `);
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

    calcEngomado() {}

    getUltimoDigito(plate) {
        // Obtener el valor de la propiedad 'plate' del objeto diccionario
        var plate = plate || "";

        // Recorrer la cadena 'plate' en reversa
        for (var i = plate.length - 1; i >= 0; i--) {
            var char = plate[i];
            // Verificar si el carácter es un dígito
            if (/\d/.test(char)) {
                return char;
            }
        }
        // Devolver false si no se encuentra ningún dígito
        return false;
    }
}
