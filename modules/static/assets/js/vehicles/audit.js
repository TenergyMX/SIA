class VehiclesAudit {
    constructor(options) {
        const self = this;
        self.filtro_estado = "todas";

        const defaultOptions = {
            data: {},
            table: {
                id: "#table_audit",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_audit/",
                    dataSrc: function (json) {
                        if (self.filtro_estado === "todas") {
                            self.updateCounters(json);
                        }
                        return json.data;
                    },
                    data: function (d) {
                        const period = document.getElementById("audit-period")?.value || "mensual";
                        const date = document.getElementById("audit-date")?.value || null;
                        return {
                            ...d,
                            vehicle_id: self.vehicle?.data?.id || null,
                            tipo_carga: self.filtro_estado,
                            period: period,
                            selected_date: date,
                        };
                    },
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Vehículo", data: "vehicle__name" },
                    { title: "Fecha", data: "audit_date" },
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
                self.table.ajax.url = "/get_vehicle_audit/";
                self.table.ajax.data = {
                    vehicle_id: self.table.vehicle.id,
                };

                // Buscar el índice del elemento que quieres eliminar//
                let indexToRemove = self.table.columns.findIndex(function (column) {
                    return column.title === "Vehículo" && column.data === "vehicle__name";
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
        this.driverSia();
        this.driverSiaFormulario();
        self.setupPeriodFilter();

        // Inicializar contadores
        self.updateCounters({
            total: 0,
            evaluadas: 0,
            vencidas: 0,
            proximas: 0,
            total_vehiculos: 0,
        });

        if (self.table) {
            self.tbl_audit = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: self.table.ajax.data,
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

        // Filtros de estado
        $(".filter-card")
            .off("click")
            .on("click", function () {
                const status = $(this).data("status");
                $(".filter-card").removeClass("active");
                $(this).addClass("active");
                self.filtro_estado = status;

                if (self.tbl_audit) {
                    self.tbl_audit.ajax.reload();
                }
            });

        // Mostrar u ocultar campos en modal
        if (self.vehicle && self.vehicle.data.id) {
            $('#mdl_crud_audit [name="vehicle_id"]').hide();
            $('#mdl_crud_audit [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_audit [name="vehicle_id"]').show();
            $('#mdl_crud_audit [name="vehicle__name"]').hide();
        }

        self.setupEventHandlers();
    }

    setupPeriodFilter() {
        const self = this;
        const periodSelect = document.getElementById("audit-period");
        const dateInput = document.getElementById("audit-date");

        if (!periodSelect || !dateInput) return;

        periodSelect.addEventListener("change", function () {
            dateInput.type = this.value === "mensual" ? "month" : "week";
            if (self.tbl_audit) {
                self.tbl_audit.ajax.reload();
            }
        });

        dateInput.addEventListener("change", function () {
            if (self.tbl_audit) {
                self.tbl_audit.ajax.reload();
            }
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
                            title: "Todas las auditorías",
                            description:
                                "Se muestra un registro por vehiculo, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-2",
                        popover: {
                            title: "Auditorías evaluadas",
                            description:
                                "Se muestran todas las auditorias evaluadas, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-3",
                        popover: {
                            title: "Auditorías vencidas",
                            description:
                                "Se muestran todos las auditorias vencidas, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-4",
                        popover: {
                            title: "Auditorías próximas a evaluar",
                            description:
                                "Se muestran las auditorias proximas a evaluar, con sus respectivos datos.",
                        },
                    },
                    {
                        element: ".drive-5",
                        popover: {
                            title: "Agregar auditoría",
                            description: "Agrega una nueva auditoria a traves del formulario.",
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
        const modal = $("#mdl_crud_audit").length;
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
                                description: "Selecciona un vehículo a auditar.",
                            },
                        },
                        {
                            element: ".drive-7",
                            popover: {
                                title: "Fecha de auditoría",
                                description: "Ingresa una fecha a realizar la auditoria.",
                            },
                        },
                        {
                            element: ".drive-8",
                            popover: {
                                title: "Nota general",
                                description: "Comenta las observaciones que se tienen.",
                            },
                        },
                        {
                            element: ".drive-9",
                            popover: {
                                title: "Checks",
                                description:
                                    "Selecciona las opciones a tomar en cuenta durante la auditoria.",
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
        $("#counter-evaluadas").text(counters.evaluadas || 0);
        $("#counter-vencidas").text(counters.vencidas || 0);
        $("#counter-proximas").text(counters.proximas || 0);
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_audit");
        $(document).on("click", "[data-vehicle-audit]", function (e) {
            const obj = $(this);
            const option = obj.data("vehicle-audit");

            switch (option) {
                case "refresh-table":
                    self.tbl_audit.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal
                        .find(".modal-header  .modal-title")
                        .html("Registrar Auditoria vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    if (self.vehicle && self.vehicle.data.vehicle_id) {
                        $('#mdl_crud_audit [name="vehicle_id"]').hide();
                        $('#mdl_crud_audit [name="vehicle__name"]').show();
                    } else {
                        $('#mdl_crud_audit [name="vehicle_id"]').show();
                        $('#mdl_crud_audit [name="vehicle__name"]').hide();
                    }
                    var checksField = obj_modal.find("[name='checks[]']");
                    checksField.empty(); // Limpiar las opciones anteriores del select

                    obj_modal.find("[name='vehicle_id']").val(self.vehicle.data.vehicle_id || null);
                    obj_modal
                        .find("[name='vehicle__name']")
                        .val(self.vehicle.data.vehicle__name || null);

                    //llamar la función de cargar checks
                    obtener_checks_empresa();
                    obj_modal.on("change", "[name='checks[]']", function () {
                        var modal = $("#mdl_crud_audit .select2-selection__choice");
                        modal.attr(
                            "style",
                            "background-color: var(--primary-color) !important; border: 1px solid var(--primary-color) !important;"
                        );
                    });

                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header").html("Actualizar Auditoría vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    if (self.vehicle && self.vehicle.data.vehicle_id) {
                        $('#mdl_crud_audit [name="vehicle_id"]').hide();
                        $('#mdl_crud_audit [name="vehicle__name"]').show();
                    } else {
                        $('#mdl_crud_audit [name="vehicle_id"]').show();
                        $('#mdl_crud_audit [name="vehicle__name"]').hide();
                    }
                    $.each(datos, function (index, value) {
                        if (index === "checks") {
                            var checksField = obj_modal.find("[name='checks[]']");
                            checksField.empty(); // Limpiar las opciones anteriores del select

                            // Si 'checks' es un array, recorrer y agregar las opciones
                            if (Array.isArray(value)) {
                                $.each(value, function (checkIndex, checkValue) {
                                    // Crear la opción y agregarla al select
                                    var option = $("<option>")
                                        .val(checkValue.id)
                                        .text(checkValue.name);

                                    // Si es un nuevo check, agregar clase especial
                                    if (checkValue.is_add_new) {
                                        option.addClass("text-success fw-bold");
                                    }

                                    // Agregar la opción al select
                                    checksField.append(option);
                                });
                            }

                            // Inicializar select2 después de agregar las opciones
                            checksField.select2({
                                width: "100%",
                                placeholder: "Seleccione los checks",
                                allowClear: true,
                            });

                            $(checksField).css({
                                "background-color": "var(--primary-color)", // Establece el fondo
                                border: "1px solid var(--primary-color)", // Ajuste para el borde
                            });
                            $(
                                ".select2-container--default .select2-selection--multiple .select2-selection__choice"
                            ).css({
                                "background-color": "var(--primary-color)", // Establece el fondo
                                border: "1px solid var(--primary-color)", // Ajuste para el borde
                            });
                            // Marcar las opciones como seleccionadas en el select2
                            checksField.val(value.map((check) => check.id)).trigger("change");
                        } else {
                            obj_modal.find(`[name='${index}']`).val(value); // Rellenar el resto de los campos
                        }
                    });
                    obj_modal.on("change", "[name='checks[]']", function () {
                        var modal = $("#mdl_crud_audit .select2-selection__choice");
                        modal.attr(
                            "style",
                            "background-color: var(--primary-color) !important; border: 1px solid var(--primary-color) !important;"
                        );
                    });
                    obtener_checks_empresa();
                    var audit_id = datos["id"];
                    break;

                case "add":
                    add_vehicle_audit();
                    break;
                case "delete-item":
                    var url = "/delete_vehicle_audit/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            self.tbl_audit.ajax.reload();
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
                    obj_modal.find(".modal-header").html("Auditoria");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    obj_modal.find('[name="vehicle_id"]').hide();
                    obj_modal.find('[name="vehicle__name"]').show();
                    obj_modal.find('[name="audit_date"]').prop("readonly", true);
                    break;
                case "show-info-details":
                    hideShow("#v-audit-pane .info", "#v-audit-pane .info-details");
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();
                    var obj_div = $("#v-audit-pane .info-details");

                    var tbody = obj_div.find("#audit-checks-table tbody");
                    tbody.empty();
                    $("#audit-checks-table")
                        .attr("data-audit-id", datos.id)
                        .data("checks", datos.checks);

                    // Llenar la información general
                    $.each(datos, function (index, value) {
                        obj_div
                            .find(`[data-key-value="${index}"]`)
                            .html(value || "---")
                            .removeClass();

                        if ($("#" + index).length > 0) {
                            $("#" + index).val(value || "---");

                            // Verificamos si la auditoría está chequeada
                            if (datos.is_checked) {
                                $("#" + index).prop("readonly", true);
                            } else {
                                $("#" + index).prop("readonly", false);
                            }
                        }
                    });

                    // Detectar checks malos/muy malos
                    var hasBadChecks = false;
                    if (Array.isArray(datos["checks"])) {
                        datos["checks"].forEach(function (checkItem) {
                            if (checkItem.status === "Malo" || checkItem.status === "Muy Malo") {
                                hasBadChecks = true;
                            }
                        });
                    }

                    // Insertar campo "Fecha compromiso"
                    if (hasBadChecks) {
                        obj_div.find("#commitment-date-container").remove();
                        let target = obj_div.find(".audit_date");
                        if (datos.commitment_date && datos.commitment_date !== "") {
                            // Ya existe fecha -> mostrar solo como texto
                            target.after(`
                                <p id="commitment-date-container" class="card-text mt-2">
                                    <span class="fw-bold">Fecha compromiso: </span>
                                    <span>${datos.commitment_date}</span>
                                </p>
                            `);
                        } else {
                            let auditDate = target.text().trim();
                            let auditDateISO = auditDate.includes("-")
                                ? auditDate
                                : auditDate.split("/").reverse().join("-");

                            target.after(`
                                <p id="commitment-date-container" class="card-text mt-2">
                                    <span class="fw-bold">Fecha compromiso: </span>
                                    <input type="date" id="commitment_date" 
                                        name="commitment_date" 
                                        class="form-control form-control-sm d-inline-block w-auto" 
                                        min="${auditDateISO}">
                                </p>
                            `);
                        }
                    } else {
                        $("#commitment-date-container").remove();
                    }

                    // Depurar la sección de checks
                    if (datos["checks"]) {
                        // Comprobar si 'checks' es un arreglo
                        if (Array.isArray(datos["checks"])) {
                            var hasBadChecks = false;
                            datos["checks"].forEach(function (checkItem, idx) {
                                if (
                                    checkItem.status === "Malo" ||
                                    checkItem.status === "Muy Malo"
                                ) {
                                    hasBadChecks = true;
                                }
                                // Crear un select para el estado
                                var selectStatus = `
                                    <select class="form-select status-select" data-key-value="status" ${
                                        datos.is_checked ? "disabled" : ""
                                    }>
                                        <option value="Muy Malo" ${
                                            checkItem.status === "Muy Malo" ? "selected" : ""
                                        }>Muy Malo</option>
                                        <option value="Malo" ${
                                            checkItem.status === "Malo" ? "selected" : ""
                                        }>Malo</option>
                                        <option value="Regular" ${
                                            checkItem.status === "Regular" ? "selected" : ""
                                        }>Regular</option>
                                        <option value="Bueno" ${
                                            checkItem.status === "Bueno" ? "selected" : ""
                                        }>Bueno</option>
                                        <option value="Excelente" ${
                                            checkItem.status === "Excelente" ? "selected" : ""
                                        }>Excelente</option>
                                    </select>
                                `;

                                // Crear el campo de notas (textarea si no está chequeado)
                                var notesField = datos.is_checked
                                    ? `<span>${checkItem.notes || "---"}</span>`
                                    : `<textarea class="form-control editable-textarea" rows="2" placeholder="Escribe las notas aquí..." ${
                                          datos.is_checked ? "readonly" : ""
                                      }>${checkItem.notes || ""}</textarea>`;

                                // Agregar encabezado de evidencia si existe fecha compromiso
                                if (
                                    datos.commitment_date &&
                                    $("#audit-checks-table thead tr").find(".evidencia-th")
                                        .length === 0
                                ) {
                                    $("#audit-checks-table thead tr").append(
                                        "<th class='evidencia-th'>Evidencia de corrección</th>"
                                    );
                                }

                                // Crear la fila de la tabla
                                var nuevaFila = `
                                    <tr>
                                        <th>${checkItem.name || "---"}</th>
                                        <td class="status">${selectStatus}</td>
                                        <td class="notes">${notesField}</td>
                                        <td class="image">
                                            ${
                                                checkItem.imagen && checkItem.imagen !== ""
                                                    ? `<a href="${checkItem.imagen}" target="_blank" class="btn btn-sm btn-info">
                                                        <i class="fa fa-image"></i> Ver imagen
                                                    </a>`
                                                    : datos.is_checked
                                                    ? `<span class="text-muted">Sin imagen</span>`
                                                    : `<input data-key-value="images" type="file" accept="image/*"
                                                                class="form-control form-control-sm correction-image check-image"
                                                                name="correction_${checkItem.name}">`
                                            }
                                        </td>
                                    </tr>
                                `;

                                tbody.append(nuevaFila);
                            });
                        }
                    } else {
                    }
                    // Actualizar la información del vehículo
                    if (self.vehicle && self.vehicle.infoCard) {
                        self.vehicle.infoCard.vehicle.id = datos["vehicle_id"];
                        self.vehicle.infoCard.ajax.reload();
                    }
                    $("#update-audit-btn")
                        .attr("onclick", `evaluate_audit(${datos["id"]}, ${datos["vehicle_id"]})`)
                        .show();
                    if (Boolean(datos.is_checked)) {
                        // Ocultar el botón si ya está chequeada
                        $("#update-audit-btn").hide();
                    } else {
                        // Mostrar el botón de actualización solo si no está chequeada
                        $("#update-audit-btn").show();
                    }

                    if (datos.commitment_date && hasBadChecks) {
                        enableCorrectionEvidence(datos.checks);
                    }

                    $("#correction-btn-container").remove();
                    if (hasBadChecks && datos.commitment_date) {
                        const targetParent = $("#general_notes").parent();
                        targetParent.append(`
                            <div id="correction-btn-container" class="mt-2 d-flex justify-content-start">
                                <button type="button" id="save-correction-btn" class="btn btn-success">Guardar correcciones</button>
                            </div>
                        `);

                        //setTimeout
                        $("#save-correction-btn")
                            .off("click")
                            .on("click", function () {
                                save_correction_evidence(datos.checks);
                            });
                    }

                    break;
                case "show-info":
                    hideShow("#v-audit-pane .info-details", "#v-audit-pane .info");
                    break;
                case "upd_audit_checks":
                    upd_audit_checks();

                    break;
                default:
                    break;
            }
        });
    }
}

function obtener_checks_empresa(selectedValues = []) {
    let selectChecks = $("select[name='checks[]']");
    let currentSelected = selectChecks.val() || [];

    $.ajax({
        url: `/obtener_checks_empresa/`,
        method: "GET",
        dataType: "json",
        success: function (data) {
            selectChecks.empty();

            if (Array.isArray(data) && data.length > 0) {
                data.forEach(function (check, index) {
                    if (!check.id) {
                        return;
                    }

                    let isSelected = [...currentSelected, ...selectedValues].includes(
                        check.id.toString()
                    )
                        ? "selected"
                        : "";
                    selectChecks.append(
                        `<option value="${check.id}" ${isSelected}>${check.name}</option>`
                    );
                });
            }

            // Agregar opción para añadir un nuevo check
            selectChecks.append(`
                <option value="add_new" class="text-success fw-bold">
                    Agregar Nuevo Check
                </option>
            `);

            setTimeout(() => {
                selectChecks.val([...currentSelected, ...selectedValues]).trigger("change");
            }, 100);

            // Inicializar Select2 con las configuraciones necesarias
            selectChecks.select2({
                width: "100%",
                placeholder: "Seleccione los checks",
                dropdownParent: $("#mdl_crud_audit"),
                dropdownAutoWidth: true,
                closeOnSelect: false,
            });
        },
        error: function (xhr, status, error) {},
    });
}

// Detectar cuando el usuario selecciona "Agregar Nuevo Check"
$(document).on("change", "select[name='checks[]']", function () {
    if ($(this).val()?.includes("add_new")) {
        $(this).val([
            ...$(this)
                .val()
                .filter((val) => val !== "add_new"),
        ]); // Evita perder los seleccionados
        $("#mdl-crud-check").modal("show");
    }
});

function upd_audit_checks() {
    // Deshabilitar el botón para evitar múltiples clics
    var saveButton = $("#btn_guardar"); // Suponiendo que tu botón tiene el id 'btn_guardar'
    saveButton.prop("disabled", true);

    var modal = document.getElementById("mdl_crud_audit");
    var form = modal.querySelector("[name='form-vrt']");
    var formData = new FormData(form);

    var checksArray = [];
    form.querySelectorAll("input[name='checks[]']:checked").forEach(function (checkbox) {
        checksArray.push(checkbox.value);
    });

    formData.append("checks", JSON.stringify(checksArray));

    $.ajax({
        url: "/upd_audit_checks/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                Swal.fire("Éxito", "Auditoría actualizada correctamente", "success");
                $("#mdl_crud_audit").modal("hide");
                $("#table_audit").DataTable().ajax.reload();
            } else {
                Swal.fire("Error", response.error, "error");
            }
            // Volver a habilitar el botón
            saveButton.prop("disabled", false);
        },
        error: function () {
            Swal.fire("Error", "No se pudo actualizar la auditoría", "error");
            // Volver a habilitar el botón en caso de error
            saveButton.prop("disabled", false);
        },
    });
}

// Función para manejar el envío del formulario de checks
function add_check() {
    var form = document.getElementById("form_add_check");
    var formData = new FormData(form);
    let selectedValues = $("select[name='checks[]']").val() || []; // Guardar selecciones antes de actualizar

    $.ajax({
        type: "POST",
        url: "/add_check/",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                let nuevoCheckId = response.new_check_id; // ID del nuevo check devuelto por el servidor
                if (nuevoCheckId) {
                    selectedValues.push(nuevoCheckId.toString()); // Agregar el nuevo check a los seleccionados
                }

                Swal.fire({
                    title: "Éxito",
                    text: "Check agregado correctamente",
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });

                form.reset();
                obtener_checks_empresa(selectedValues); // Recargar select sin perder selección

                $("#mdl-crud-check")
                    .modal("hide")
                    .on("hidden.bs.modal", function () {
                        $(this).find("input, button, select").blur(); // Evitar error de `aria-hidden`
                    });
            } else {
                Swal.fire({
                    title: "Error",
                    text: response.message || "Ocurrió un error inesperado",
                    icon: "error",
                    timer: 1500,
                    showConfirmButton: false,
                });
            }
        },
        error: function (xhr, status, error) {},
    });
}

function add_vehicle_audit() {
    var modal = document.getElementById("mdl_crud_audit");
    var form = modal.querySelector("[name='form-vrt']");
    var formData = new FormData(form);
    $.ajax({
        url: "/add_vehicle_audit/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                Swal.fire("Éxito", "Auditoría agregada correctamente", "success");
                $("#mdl_crud_audit").modal("hide");
                $("#table_audit").DataTable().ajax.reload();
            } else {
                Swal.fire("Error", response.error, "error");
            }
        },
        error: function () {
            Swal.fire("Error", "No se pudo agregar la auditoría", "error");
        },
    });
}

function evaluate_audit(id, vehicle_id) {
    var auditData = [];
    var formData = new FormData();

    $("#audit-checks-table tbody tr").each(function () {
        var row = $(this);
        var name = row.find("th").text().trim();
        var status = row.find("td.status select").val();
        var notas = row.find("td.notes textarea").val().trim();
        var imagenInput = row.find("td.image input[type='file']")[0];
        var imagenFile = imagenInput && imagenInput.files.length > 0 ? imagenInput.files[0] : null;

        var checkData = {
            id: name,
            status: status,
            notas: notas,
            imagen: imagenFile ? imagenFile.name : "",
        };

        auditData.push(checkData);

        if (imagenFile) {
            formData.append(`imagen_${name.replace(/\s+/g, "_")}`, imagenFile);
        }
    });

    formData.append("audit_id", id);
    formData.append("vehicle_id", vehicle_id);
    formData.append("audit_data", JSON.stringify(auditData));
    formData.append("csrfmiddlewaretoken", $('input[name="csrfmiddlewaretoken"]').val());

    // Mostrar loading con SweetAlert
    Swal.fire({
        title: "Procesando registro de auditoria...",
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/evaluate_audit/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            Swal.close();

            if (response.success) {
                Swal.fire("Éxito", "Auditoría evaluada correctamente", "success");
                $("#table_audit")
                    .DataTable()
                    .ajax.reload(function () {
                        reloadAuditDetails(id);
                    }, false);
                $("#update-audit-btn").hide();
            } else {
                Swal.fire("Error", response.error, "error");
            }
        },
        error: function (xhr, status, error) {
            Swal.close();

            Swal.fire("Error", "Hubo un error al actualizar la auditoría", "error");
        },
    });
}

$(document).on("change", ".check-image", function (e) {
    let input = this;
    let file = input.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
        Swal.fire("Error", "El archivo seleccionado no es una imagen.", "error");
        input.value = "";
        return;
    }

    let reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = function (event) {
        let img = new Image();
        img.src = event.target.result;

        img.onload = function () {
            let canvas = document.createElement("canvas");
            let ctx = canvas.getContext("2d");

            // Detectar orientación
            let isHorizontal = img.width >= img.height;
            let newWidth, newHeight;

            if (isHorizontal) {
                // Imágenes horizontales
                newWidth = 2000;
                newHeight = 1400;
            } else {
                // Imágenes verticales
                newWidth = 1000;
                newHeight = 1500;
            }

            // Ajustar el canvas al nuevo tamaño
            canvas.width = newWidth;
            canvas.height = newHeight;

            // Dibujar y escalar la imagen
            ctx.drawImage(img, 0, 0, newWidth, newHeight);

            // Reducir calidad (60%)
            let quality = 0.6;
            let compressedDataUrl = canvas.toDataURL(file.type, quality);

            // Convertir de DataURL a Blob
            fetch(compressedDataUrl)
                .then((res) => res.blob())
                .then((blob) => {
                    let newFile = new File([blob], file.name, { type: file.type });

                    // Reemplazar archivo original en el input
                    let dataTransfer = new DataTransfer();
                    dataTransfer.items.add(newFile);
                    input.files = dataTransfer.files;

                    // Notificar
                    Swal.fire({
                        icon: "success",
                        title: "Imagen optimizada",
                        text: `La imagen fue redimensionada a ${newWidth}x${newHeight} y reducida de calidad.`,
                        timer: 1300,
                        showConfirmButton: false,
                    });
                });
        };
    };
});

// Filtro por periodo (mes/semana)
$("#audit-period, #audit-date").on("change", function () {
    if (self.tbl_audit) {
        self.tbl_audit.ajax.reload();
    }
});

// Escucha cambios en el input de fecha
$(document).on("change", "#commitment_date", function () {
    var commitmentDate = $(this).val();
    var auditId = $("#audit-checks-table").data("audit-id");

    // Obtener la fecha de la auditoría en formato ISO (YYYY-MM-DD)
    var auditDate = $(".audit_date").text().trim();
    var auditDateISO = auditDate.includes("-")
        ? auditDate
        : auditDate.split("/").reverse().join("-");

    if (!commitmentDate) {
        Swal.fire("Atención", "Selecciona una fecha de compromiso", "warning");
        return;
    }

    // Validar fecha compromiso >= fecha auditoría
    if (new Date(commitmentDate) < new Date(auditDateISO)) {
        Swal.fire(
            "Error",
            "La fecha compromiso no puede ser anterior a la fecha de auditoría",
            "error"
        );
        $(this).val("");
        return;
    }

    if (!commitmentDate) {
        Swal.fire("Atención", "Selecciona una fecha de compromiso", "warning");
        return;
    }

    if (!auditId) {
        Swal.fire("Error", "No se encontró el ID de la auditoría", "error");
        return;
    }

    // Mostrar mensaje de confirmación
    Swal.fire({
        title: "¿Estás seguro?",
        html: `¿Te comprometes a realizar las mejoras antes del <strong>${commitmentDate}</strong>?`,
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Sí, comprometerme",
        cancelButtonText: "Cancelar",
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/save_commitment_date/",
                method: "POST",
                data: {
                    audit_id: auditId,
                    commitment_date: commitmentDate,
                    csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
                },
                success: function (res) {
                    if (res.success) {
                        Swal.fire("Éxito", "Fecha compromiso guardada y correo enviado", "success");

                        $("#commitment-date-container").html(`
                            <span class="fw-bold">Fecha compromiso: </span>
                            <span class="text-success">${commitmentDate}</span>
                        `);

                        const checks = $("#audit-checks-table").data("checks");
                        enableCorrectionEvidence(checks);

                        // addEvidenceColumn();
                    } else {
                        Swal.fire("Error", res.error, "error");
                    }
                },
                error: function (xhr, status, error) {
                    console.error(error);
                    Swal.fire("Error", "Hubo un error al guardar la fecha compromiso", "error");
                },
            });
        } else {
            $("#commitment_date").val("");
        }
    });
});

function enableCorrectionEvidence(checks) {
    const tbody = $("#audit-checks-table tbody");

    // Agregar columna de evidencia si no existe
    if ($("#audit-checks-table thead tr").find(".evidencia-th").length === 0) {
        $("#audit-checks-table thead tr").append(
            "<th class='evidencia-th'>Evidencia de corrección</th>"
        );
    }

    let allHaveEvidence = true; // bandera para decidir si mostrar el botón

    // Recorrer las filas
    tbody.find("tr").each(function (idx, row) {
        const check = checks[idx];

        let cellContent = "";

        if (check.status === "Malo" || check.status === "Muy Malo") {
            if (check.correction && check.correction !== "") {
                // Si ya existe evidencia, mostrar enlace
                cellContent = `<a href="${check.correction}" target="_blank" class="btn btn-sm btn-info">
                                    <i class="fa fa-image"></i> Ver corrección
                               </a>`;
            } else {
                // Si no existe, agregar input
                cellContent = `<input type="file" accept="image/*" class="form-control form-control-sm correction-image check-image" name="correction_${check.name}">`;
                allHaveEvidence = false; // al menos un check sin evidencia
            }
        } else {
            cellContent = `<span class="text-muted">No aplica</span>`;
        }

        // limpiar y volver a insertar la celda
        $(row).find(".correction-evidence").remove();
        $(row).append(`<td class="correction-evidence">${cellContent}</td>`);
    });

    // Mostrar botón solo si hay algún check malo/muy malo sin evidencia
    $("#save-correction-btn").remove(); // limpiar antes
    if (!allHaveEvidence) {
        $("#v-audit-pane .info-details #update-button-container").append(`
            <button id="save-correction-btn" class="btn btn-success mt-2">Guardar correcciones</button>
        `);

        $("#save-correction-btn")
            .off("click")
            .on("click", function () {
                save_correction_evidence(checks);
            });
    }
}

function save_correction_evidence(checks) {
    const auditId = $("#audit-checks-table").attr("data-audit-id");
    const formData = new FormData();
    formData.append("audit_id", auditId);

    let emptyFound = false;

    $(".correction-image").each(function (idx, input) {
        if (input.files.length > 0) {
            formData.append(input.name, input.files[0]);
        } else {
            emptyFound = true;
        }
    });

    if (emptyFound) {
        Swal.fire({
            icon: "warning",
            title: "Faltan imágenes",
            text: "Debes subir imágenes en todos los checks malos/muy malos antes de enviar.",
        });
        return;
    }

    Swal.fire({
        title: "¿Quieres enviar las evidencias de corrección?",
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Sí, enviar",
        cancelButtonText: "Cancelar",
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/vehicles/save_correction_evidence/",
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (response.success) {
                        Swal.fire({
                            icon: "success",
                            title: "Éxito",
                            text: "Correcciones guardadas exitosamente",
                        });

                        // Reemplazar inputs por botones Ver Imagen usando paths devueltos
                        $(".correction-image").each(function (idx, input) {
                            const checkName = $(input).attr("name").replace("correction_", "");
                            const s3Path = response.paths[checkName] || "#";
                            $(input).replaceWith(
                                `<a href="${s3Path}" target="_blank" class="btn btn-sm btn-success">
                                    <i class="fa fa-image"></i> Ver corrección
                                </a>`
                            );
                        });

                        // Ocultar botón guardar si ya no hay inputs
                        if ($(".correction-image").length === 0) {
                            $("#save-correction-btn").remove();
                        }
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: response.error,
                        });
                    }
                },
                error: function () {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: "Error al enviar las correcciones",
                    });
                },
            });
        }
    });
}

function reloadAuditDetails(auditId) {
    const table = $("#table_audit").DataTable();
    table.rows().every(function () {
        const data = this.data();
        if (data && data.id === auditId) {
            const $row = $(this.node());
            const $btn = $row.find("[data-vehicle-audit='show-info-details']");
            if ($btn.length > 0) {
                $btn.trigger("click");
            }
            return false;
        }
    });
}
