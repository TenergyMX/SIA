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
        $(document).ready(function () {
            self.init();
        });
    }

    init() {
        const self = this;

        // Obtener la parte de la URL que contiene "qr/15"
        const pathParts = window.location.pathname.split("/");

        // Buscar el valor después de "qr"
        const qr = pathParts[pathParts.indexOf("qr") + 1];

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
        // Si `QR` está presente en la URL, esperar a que el modal se cargue y luego abrirlo
        if (qr) {
            self.esperarModal("#mdl_crud_responsiva")
                .then(() => self.openResponsivaModal(qr))
                .catch((error) => console.error(error));
        }
    }
    esperarModal(selector, intentos = 10, intervalo = 100) {
        return new Promise((resolve, reject) => {
            let contador = 0;

            function verificarModal() {
                let modal = document.querySelector(selector);
                if (modal) {
                    resolve(); // Modal encontrado
                } else if (contador < intentos) {
                    contador++;
                    setTimeout(verificarModal, intervalo);
                } else {
                    reject(`El modal "${selector}" no está disponible.`);
                }
            }

            verificarModal();
        });
    }

    openResponsivaModal(id_vehicle) {
        const self = this;
        var obj_modal = $("#mdl_crud_responsiva");
        obj_modal.find("form")[0].reset();
        obj_modal.modal("show");

        $.ajax({
            url: "/validar_vehicle_en_sa/", 
            type: "POST",
            data: {
                id_vehicle: id_vehicle,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function (response) {
                var status = response.status;
                console.log(response);
                if (status == "SALIDA") {
                    obj_modal.find(".modal-header").html("Registrar salida");
                    obj_modal.find(".final").hide().find(":input").prop("disabled", true);
                    obj_modal.find(".inicial").show().find(":input").prop("disabled", false);
                    if (response.fecha_actual) {
                        $("input[name='start_date']").val(response.fecha_actual);
                    }
                    obj_modal.find("[name='initial_mileage']").val(response.km_final || null);
                    obj_modal.find("[name='initial_fuel']").val(response.gasolina_final || null);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                } else if (status == "ENTRADA") {
                    obj_modal.find(".modal-header").html("Registrar entrada");
                    obj_modal.find(".inicial").hide().find(":input").prop("disabled", true);
                    obj_modal.find(".final").show().find(":input").prop("disabled", false);
                    obj_modal.find("[name='id']").val(response.id_register || null);
                    if (response.fecha_actual) {
                        $("input[name='end_date']").val(response.fecha_actual);
                    }
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();
                    setTimeout(function () {
                        $('select[name="responsible_id"]').val(response.id_responsable || null);
                    }, 500);
                    console.log(id_vehicle);
                    console.log(response.id_register);
                    console.log(response.id_responsable);
                }
            },
            error: function (xhr, status, error) {
                // Maneja el error si la solicitud falla
                console.log("Error en la solicitud AJAX:", error);
            },
        });

        console.log(self.vehicle.data.vehicle_id);
        setTimeout(function () {
            $
        }, 500);
        // Usar la función para asignar el valor
        asignarValorSelect(id_vehicle)
        .then(() => {
            console.log("Valor asignado correctamente.");
        })
        .catch((error) => {
            console.error(error);
        });
        // obj_modal.find("[name='vehicle_id']").val(qr || null);
        // obj_modal.find("[name='vehicle_name']").val(self.vehicle.data.vehicle_name || null);

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
                        var isFileInput = obj_modal.find([(name = "${index}")]).is(":file");

                        if (!isFileInput) {
                            obj_modal.find([(name = "${index}")]).val(value);
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
                        if (index === "initial_fuel" || index === "final_fuel") {
                            obj_div.find(`[data-key-value="${index}"]`)
                                .html(isNaN(parseInt(value)) ? "--- %" : parseInt(value) + " %")
                                .removeClass();
                        } else {
                            obj_div.find(`[data-key-value="${index}"]`)
                                .html(isNaN(parseInt(value)) ? "---" : parseInt(value))
                                .removeClass();
                        }
                        
                        
                        

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
                            .attr("src", datos["image_path_exit_1"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_exit_1']")
                            .attr("src", "")
                            .closest(".card")
                            .removeClass("placeholder");
                    }

                    if (datos["image_path_exit_2"]) {
                        $("[alt='image_path_exit_2']")
                            .attr("src", datos["image_path_exit_2"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_exit_2']")
                            .attr("src", "")
                            .closest(".card")
                            .removeClass("placeholder");
                    }
                    // # cargar funcion completa
                    if (datos["image_path_entry_1"]) {
                        $("[alt='image_path_entry_1']")
                            .attr("src", datos["image_path_entry_1"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_entry_1']")
                            .attr("src", "")
                            .closest(".card")
                            .removeClass("placeholder");
                    }
                    // # cargar funcion completa
                    if (datos["image_path_entry_2"]) {
                        $("[alt='image_path_entry_2']")
                            .attr("src", datos["image_path_entry_2"])
                            .closest(".card")
                            .removeClass("placeholder");
                    } else {
                        $("[alt='image_path_entry_2']")
                            .attr("src", "")
                            .closest(".card")
                            .removeClass("placeholder");
                    }
                    // # cargar funcion completa
                    // firma
                    $("[alt='firma']").attr("src", datos["signature"]);

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

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_maintenance/";
            var datos = new FormData(this);

            if (submit == "add" && !self.input.signature.hasDrawing()) {
                Swal.fire("Sin firma", "El responsable debe firmar", "warning");
                return;
            }

            Swal.fire({
                title: "Procesando...",
                text: "Por favor, espera mientras se procesa la solicitud.",
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

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
                                if (response.status == "warning" && response.type == "mantenimiento") {
                                    Swal.fire(
                                        "Warning",
                                        "Vehiculo en proceso de mantenimiento \n" + 
                                        "No se pudo realizar el registro, informe a la persona encargada",
                                        "warning"
                                    );
                                } else if (!response.success && response.error) {
                                    Swal.fire("Error", response.error["message"], "error");
                                } else if (response.warning && response.type == "kilometraje") {
                                    Swal.fire(
                                        "Advertencia",
                                        response.warning["message"],
                                        "warning"
                                    );
                                } else {
                                    Swal.fire("Éxito", "Salida Registrada", "success");
                                }

                                obj_modal.modal("hide");
                                self.tbl_responsiva.ajax.reload();
                                self.input.signature.clearCanvas();
                            },
                            error: function (xhr, status, error) {
                                Swal.close();
                                Swal.fire(
                                    "Error del servidor",
                                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                    "error"
                                );
                            },
                        });
                    })
                    .catch((error) => {
                        Swal.close();
                        Swal.fire("Error", "No se pudo obtener la firma", "error");
                    });
            } else {
                url = "/update_vehicle_responsiva/";

                $.ajax({
                    type: "POST",
                    url: url,
                    data: datos,
                    processData: false,
                    contentType: false,
                    success: function (response) {
                        Swal.close(); // Cerrar alerta de carga antes de mostrar el resultado
                        if (response.status == "warning" && response.type == "mantenimiento") {
                            Swal.fire(
                                "Warning",
                                "Vehiculo en proceso de mantenimiento \n" + 
                                "No se pudo realizar el registro, informe a la persona encargada",
                                "warning"
                            );
                        } else if (!response.success && response.error) {
                            Swal.fire("Error", response.error["message"], "error");
                        } else if (response.warning) {
                            Swal.fire("Advertencia", response.warning["message"], "warning");
                        } else if (response.status == "warning" && response.type == "kilometraje") {
                            Swal.fire("Error", response.message, "warning");
                            return;
                        } else if (!response.success) {
                            Swal.fire("Advertencia", "Error inesperado", "error");
                        } else {
                            Swal.fire("Éxito", "Entrada Registrada", "success");
                        }
                        obj_modal.modal("hide");
                        self.tbl_responsiva.ajax.reload();
                    },
                    error: function (xhr, status, error) {
                        Swal.close();
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

function asignarValorSelect(id_vehicle, intentos = 10, intervalo = 100) {
    return new Promise((resolve, reject) => {
        let contador = 0;

        function verificarYAsignar() {
            var select = $('select[name="vehicle_id"]');
            var opcionExiste = select.find(`option[value="${id_vehicle}"]`).length > 0;

            if (opcionExiste) {
                select.val(id_vehicle); // Asignar el valor si la opción existe
                resolve();
            } else if (contador < intentos) {
                contador++;
                setTimeout(verificarYAsignar, intervalo); // Reintentar después de un intervalo
            } else {
                reject("La opción no está disponible en el select.");
            }
        }

        verificarYAsignar();
    });
}