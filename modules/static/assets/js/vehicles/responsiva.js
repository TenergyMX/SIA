class VehiclesResponsiva {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
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
            table: {
                id: "#table_responsiva",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_responsiva/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id" },
                    { title: "Vehículo", data: "vehicle__name" },
                    {
                        title: "Responsable",
                        data: function (d) {
                            return d["responsible__first_name"] + " " + d["responsible__last_name"];
                        },
                    },
                    { title: "Km. Inicial", data: "initial_mileage" },
                    { title: "Km. Final", data: "final_mileage" },
                    { title: "Fecha inicio", data: "start_date" },
                    { title: "Fecha final", data: "end_date" },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
            vehicle: {
                data: { id: null },
            },
            provider: {},
        };

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };

            if (self.table.vehicle.id) {
                self.table.ajax.url = "/get_vehicle_responsiva/";
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
            self.tbl_responsiva = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: self.table.ajax.data,
                },
                columns: self.table.columns,
                order: [[0, "desc"]],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
            });

            self.input = {};
            self.input.signature = new CanvasDrawing("canvas-signature");

            delete self.table;
        }

        if (self.vehicle && self.vehicle.data.vehicle_id) {
            $('#mdl_crud_responsiva [name="vehicle_id"]').hide();
            $('#mdl_crud_responsiva [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_responsiva [name="vehicle_id"]').show();
            $('#mdl_crud_responsiva [name="vehicle__name"]').hide();
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_responsiva");

        $(document).on("click", "[data-vehicle-responsiva]", function (e) {
            var obj = $(this);
            var option = obj.data("vehicle-responsiva");
            obj_modal.find("form :input").prop("disabled", false).closest(".col-12").show();
            switch (option) {
                case "refresh-table":
                    self.tbl_responsiva.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar salida");
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

                    obj_modal.find(".inicial").show().find(":input").prop("disabled", false);
                    obj_modal.find(".final").hide().find(":input").prop("disabled", true);
                    break;
                case "update-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    obj_modal.find("[name='vehicle_id']").hide().prop("readonly", true);
                    obj_modal.find("[name='vehicle__name']").show().prop("readonly", true);

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_responsiva.row(fila).data();
                    var select = obj_modal.find('select[name="vehicle_id"]');
                    break;
                case "delete-item":
                    var url = "/delete_vehicle_responsiva/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_responsiva.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_responsiva.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                case "check":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar Entrada");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    $('#mdl_crud_responsiva [name="vehicle_id"]').hide();
                    $('#mdl_crud_responsiva [name="vehicle__name"]').show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_responsiva.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");

                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value);
                        }
                    });

                    obj_modal.find(".inicial").hide().find(":input").prop("disabled", true);
                    obj_modal.find(".final").show().find(":input").prop("disabled", false);
                    break;
                case "show-info":
                    hideShow("#v-responsiva-pane .info-details", "#v-responsiva-pane .info");
                    break;
                case "show-info-details":
                    hideShow("#v-responsiva-pane .info", "#v-responsiva-pane .info-details");
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_responsiva.row(fila).data();
                    var obj_div = $("#v-responsiva-pane .info-details");

                    $.each(datos, function (index, value) {
                        obj_div
                            .find(`[data-key-value="${index}"]`)
                            .html(value || "---")
                            .removeClass();
                        if (index === "initial_fuel") {
                            const posicion = value;
                            const posiciones = [
                                { left: 26, top: 21, deg: -65 },
                                { left: 32, top: 6, deg: -33 },
                                { left: 44, top: 0, deg: 0 },
                                { left: 55, top: 6, deg: 33 },
                                { left: 60, top: 21, deg: 65 },
                            ];
                            const index = Math.floor(posicion / 25);
                            const siguienteIndex = Math.min(index + 1, posiciones.length - 1);
                            const porcentaje = (posicion - index * 25) / 25;
                            const left =
                                posiciones[index].left +
                                (posiciones[siguienteIndex].left - posiciones[index].left) *
                                    porcentaje;
                            const top =
                                posiciones[index].top +
                                (posiciones[siguienteIndex].top - posiciones[index].top) *
                                    porcentaje;
                            const deg =
                                posiciones[index].deg +
                                (posiciones[siguienteIndex].deg - posiciones[index].deg) *
                                    porcentaje;
                            obj_div.find(".punta-inicial").css({
                                left: `${left}%`,
                                top: `${top}%`,
                                transform: `rotate(${deg}deg) scale(0.8)`,
                            });
                        }
                        if (index === "final_fuel") {
                            const posicion = value;
                            const posiciones = [
                                { left: 26, top: 21, deg: -65 },
                                { left: 32, top: 6, deg: -33 },
                                { left: 44, top: 0, deg: 0 },
                                { left: 55, top: 6, deg: 33 },
                                { left: 60, top: 21, deg: 65 },
                            ];
                            const index = Math.floor(posicion / 25);
                            const siguienteIndex = Math.min(index + 1, posiciones.length - 1);
                            const porcentaje = (posicion - index * 25) / 25;
                            const left =
                                posiciones[index].left +
                                (posiciones[siguienteIndex].left - posiciones[index].left) *
                                    porcentaje;
                            const top =
                                posiciones[index].top +
                                (posiciones[siguienteIndex].top - posiciones[index].top) *
                                    porcentaje;
                            const deg =
                                posiciones[index].deg +
                                (posiciones[siguienteIndex].deg - posiciones[index].deg) *
                                    porcentaje;
                            obj_div.find(".punta-final").css({
                                left: `${left}%`,
                                top: `${top}%`,
                                transform: `rotate(${deg}deg) scale(0.8)`,
                            });
                        }
                    });

                    $('[data-key-value="responsible"]').html(
                        datos["responsible__first_name"] + " " + datos["responsible__last_name"] ||
                            "Sin responsable"
                    );

                    if (datos["image_path_exit_1"]) {
                        $("[alt='image_path_exit_1']")
                            .attr("src", "/" + datos["image_path_exit_1"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_exit_1']").closest(".card").addClass("placeholder");
                    }

                    if (datos["image_path_exit_2"]) {
                        $("[alt='image_path_exit_2']")
                            .attr("src", "/" + datos["image_path_exit_1"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_exit_2']").closest(".card").addClass("placeholder");
                    }

                    if (datos["image_path_entry_1"]) {
                        $("[alt='image_path_entry_1']")
                            .attr("src", "/" + datos["image_path_entry_1"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_entry_1']").closest(".card").addClass("placeholder");
                    }

                    if (datos["image_path_entry_2"]) {
                        $("[alt='image_path_entry_2']")
                            .attr("src", "/" + datos["image_path_entry_2"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_entry_2']").closest(".card").addClass("placeholder");
                    }

                    // firma
                    $("[alt='firma']").attr("src", "/" + datos["signature"]);

                    // ! Actualizamos la info card
                    if (self.vehicle && self.vehicle.infoCard) {
                        self.vehicle.infoCard.vehicle.id = datos["vehicle_id"];
                        self.vehicle.infoCard.ajax.reload();
                    }
                    break;
                default:
                    console.log("Opcion dezconocida:" + option);
            }
        });

        /*PREPARE FOR SET A NEW MAINTENANCE IN CASE THE MANTENIMIENTO NEED IT*/
        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_responsiva/";
            var datos = new FormData(this);

            if (submit == "add" && !self.input.signature.hasDrawing()) {
                Swal.fire("Sin firma", "El responsable debe firmar", "warning");
                return;
            }

            if (submit == "add") {
                url = "/add_vehicle_responsiva/";
                self.input.signature
                    .getCanvasBlob()
                    .then((blob) => {
                        datos.append("signature", blob, "signature.png");

                        $.ajax({
                            type: "POST",
                            url: url,
                            data: datos,
                            processData: false,
                            contentType: false,
                            success: function (response) {
                                Swal.close(); // Cerrar alerta de carga antes de mostrar el resultado
                                if (response.status == "warning") {
                                    Swal.fire(
                                        "Warning",
                                        "Vehiculo en proceso de mantenimiento",
                                        "warning"
                                    );
                                }
                                if (!response.success && response.error) {
                                    Swal.fire("Error", response.error["message"], "error");
                                    return;
                                } else if (!response.success && response.warning) {
                                    Swal.fire(
                                        "Advertencia",
                                        response.warning["message"],
                                        "warning"
                                    );
                                } else {
                                    Swal.fire("Exito", "Salida Registrada", "success");
                                }
                                obj_modal.modal("hide");
                                self.tbl_responsiva.ajax.reload();
                                self.input.signature.clearCanvas();
                            },
                            error: function (xhr, status, error) {
                                Swal.fire(
                                    "Error del servidor",
                                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                    "error"
                                );
                            },
                        });
                    })
                    .catch((error) => {});
            } else {
                /* submit == UPDTE */
                url = "/update_vehicle_responsiva/";
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
                        } else if (!response.success) {
                            Swal.fire("Error", "Ocurrio un error inesperado", "error");
                            return;
                        } else {
                            Swal.fire("Exito", "Entrada Registrada", "success");
                        }
                        obj_modal.modal("hide");
                        self.tbl_responsiva.ajax.reload();
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
            // end
        });
    }
}

document.querySelectorAll('.form-control[name^="image_path_"]').forEach((input) => {
    input.classList.add("resize-image");
    input.addEventListener("change", function (event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = function (event) {
                const img = new Image();
                img.src = event.target.result;
                img.onload = function () {
                    const canvas = document.createElement("canvas");
                    const ctx = canvas.getContext("2d");
                    canvas.width = 400;
                    canvas.height = 600;
                    ctx.drawImage(img, 0, 0, 400, 600);
                    canvas.toBlob(
                        function (blob) {
                            const newFile = new File([blob], file.name, {
                                type: file.type,
                                lastModified: Date.now(),
                            });

                            const dataTransfer = new DataTransfer();
                            dataTransfer.items.add(newFile);
                            Swal.fire({
                                title: "Imagen Procesada",
                                text: "La imagen se ha redimensionado correctamente.",
                                icon: "success",
                                confirmButtonText: "OK",
                            });
                            input.files = dataTransfer.files;
                        },
                        "image/jpeg",
                        0.9
                    );
                };
            };
        }
    });
});
