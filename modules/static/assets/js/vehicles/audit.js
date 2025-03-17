class VehiclesAudit {
    constructor(options) {
        const self = this;
        const defaultOptions = {
            data: {},
            table: {
                id: "#table_audit",
                vehicle: {
                    id: null,
                },
                ajax: {
                    url: "/get_vehicles_audit/",
                    dataSrc: "data",
                    data: {},
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
            self.tbl_audit = $(self.table.id).DataTable({
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
            $('#mdl_crud_audit [name="vehicle_id"]').hide();
            $('#mdl_crud_audit [name="vehicle__name"]').show();
        } else {
            $('#mdl_crud_audit [name="vehicle_id"]').show();
            $('#mdl_crud_audit [name="vehicle__name"]').hide();
        }

        self.setupEventHandlers();
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
                    obj_modal.find(".modal-header").html("Registrar Auditoria vehicular");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    obj_modal.find("[name='vehicle_id']").val(self.vehicle.data.vehicle_id || null).hide();
                    obj_modal
                        .find("[name='vehicle__name']")
                        .val(self.vehicle.data.vehicle__name || null)
                        .show();

                    //llamar la función de cargar checks
                    obtener_checks_empresa();
                    
                    break;
                    case "update-item":
                        obj_modal.modal("show");
                        obj_modal.find("form")[0].reset();
                        obj_modal.find(".modal-header").html("Actualizar Auditoría vehicular");
                        obj_modal.find("[type='submit']").hide();
                        obj_modal.find("[name='update']").show();
                    
                        var fila = $(this).closest("tr");
                        var datos = self.tbl_audit.row(fila).data();
                    
                    
                        $.each(datos, function (index, value) {
                    
                            if (index === 'checks') {
                    
                                var checksField = obj_modal.find("[name='checks[]']");
                                checksField.empty(); // Limpiar las opciones anteriores del select
                    
                                // Si 'checks' es un array, recorrer y agregar las opciones
                                if (Array.isArray(value)) {
                                    $.each(value, function (checkIndex, checkValue) {
                                        
                                        // Crear la opción y agregarla al select
                                        var option = $("<option>").val(checkValue.id).text(checkValue.name);
                    
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
                                    width: '100%',
                                    placeholder: "Seleccione los checks",
                                    allowClear: true
                                });
                    
                                // Marcar las opciones como seleccionadas en el select2
                                checksField.val(value.map(check => check.id)).trigger('change');
                            } else {
                                obj_modal.find(`[name='${index}']`).val(value); // Rellenar el resto de los campos
                            }
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
                    // Suponiendo que 'datos' contiene los datos de la auditoría
                    hideShow("#v-audit-pane .info", "#v-audit-pane .info-details");
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_audit.row(fila).data();
                    var obj_div = $("#v-audit-pane .info-details");
                                
                    // Limpiar los datos previos
                    var tbody = obj_div.find(".table tbody");
                    tbody.empty();
                
                    // Llenar la información general
                    $.each(datos, function (index, value) {
                        obj_div
                            .find(`[data-key-value="${index}"]`)
                            .html(value || "---")
                            .removeClass();
                        
                        // Si es un campo de tipo input, podemos agregar un 'readonly' si está chequeado
                        if ($("#" + index).length > 0) {
                            $("#" + index).val(value || "---");
                
                            // Verificamos si la auditoría está chequeada
                            if (datos.is_checked) {
                                $("#" + index).prop("readonly", true); // Deshabilitar el campo
                            } else {
                                $("#" + index).prop("readonly", false); // Habilitar el campo
                            }
                        }
                    });
                    // Depurar la sección de checks
                    if (datos["checks"]) {
                
                        // Comprobar si 'checks' es un arreglo
                        if (Array.isArray(datos["checks"])) {
                            datos["checks"].forEach(function (checkItem, idx) {
                
                                // Crear un select para el estado
                                var selectStatus = `
                                    <select class="form-select status-select" data-key-value="status" ${datos.is_checked ? "disabled" : ""}>
                                        <option value="Muy Malo" ${checkItem.status === "Muy Malo" ? "selected" : ""}>Muy Malo</option>
                                        <option value="Malo" ${checkItem.status === "Malo" ? "selected" : ""}>Malo</option>
                                        <option value="Regular" ${checkItem.status === "Regular" ? "selected" : ""}>Regular</option>
                                        <option value="Bueno" ${checkItem.status === "Bueno" ? "selected" : ""}>Bueno</option>
                                        <option value="Excelente" ${checkItem.status === "Excelente" ? "selected" : ""}>Excelente</option>
                                    </select>
                                `;
                
                                // Crear el campo de notas (textarea si no está chequeado)
                                var notesField = datos.is_checked 
                                    ? `<span>${checkItem.notes || "---"}</span>` // Mostrar las notas como texto si está chequeado
                                    : `<textarea class="form-control editable-textarea" rows="2" placeholder="Escribe las notas aquí..." ${datos.is_checked ? "readonly" : ""}>${checkItem.notes || ""}</textarea>`; // Solo poner readonly si está chequeado

                                // Crear la fila de la tabla
                                var nuevaFila = `
                                    <tr>
                                        <th>${checkItem.name || "---"}</th>
                                        <td class="status">${selectStatus}</td>
                                        <td class="notes">${notesField}</td>
                                    </tr>
                                `;
                                tbody.append(nuevaFila);
                            });
                        } else {
                            console.log("'checks' no es un arreglo válido.");
                        }
                    } else {
                        console.log("No se encontraron datos de 'checks'.");
                    }
                
                    // Actualizar la información del vehículo
                    if (self.vehicle && self.vehicle.infoCard) {
                        self.vehicle.infoCard.vehicle.id = datos["vehicle_id"];
                        self.vehicle.infoCard.ajax.reload();
                    }
                    $("#update-audit-btn")
                        .attr("onclick", `evaluate_audit(${datos["id"]})`)
                        .show(); // Asegurarse de que el botón se muestre si no está chequeado
                    if (Boolean(datos.is_checked)) {
                        // Ocultar el botón si ya está chequeada
                        $("#update-audit-btn").hide();
                        
                    } else {
                        // Mostrar el botón de actualización solo si no está chequeada
                        $("#update-audit-btn").show();
                        
                    }
                break;
                case "show-info":
                    hideShow("#v-audit-pane .info-details", "#v-audit-pane .info");
                    break;
                case "upd_audit_checks":
                    // Asumimos que tienes una variable 'action' que determina el flujo
                    // Solo se agrega el EventListener una vez
                    upd_audit_checks(); 
                    
                    break;
                default:
                    console.log("Opción dezconocida:", option);
                    break;
            }
        });      
    }
}

function obtener_checks_empresa(selectedValues = []) {
    let selectChecks = $("select[name='checks[]']");
    let currentSelected = selectChecks.val() || []; // Obtener valores seleccionados actuales

    $.ajax({
        url: `/obtener_checks_empresa/`,
        method: "GET",
        dataType: "json",
        success: function (data) {
            selectChecks.empty(); // Limpiar opciones previas

            if (Array.isArray(data) && data.length > 0) {
                data.forEach(function (check, index) {
                    if (!check.id) {
                        console.warn(`⚠️ Check en índice ${index} no tiene un ID válido:`, check);
                        return;
                    }

                    let isSelected = [...currentSelected, ...selectedValues].includes(check.id.toString()) ? "selected" : "";
                    selectChecks.append(`<option value="${check.id}" ${isSelected}>${check.name}</option>`);
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
                width: '100%',
                placeholder: "Seleccione los checks",
                dropdownParent: $('#mdl_crud_audit'),
                dropdownAutoWidth: true,
                closeOnSelect: false,
            });
        },
        error: function (xhr, status, error) {
            console.error(" Error en la solicitud AJAX:", status, error);
        }
    });
}

// Detectar cuando el usuario selecciona "Agregar Nuevo Check"
$(document).on("change", "select[name='checks[]']", function () {
    if ($(this).val()?.includes("add_new")) {
        $(this).val([...$(this).val().filter(val => val !== "add_new")]); // Evita perder los seleccionados
        $("#mdl-crud-check").modal("show");      
    }
});


function upd_audit_checks() {
    alert("Actualizando auditoría...");
    
    // Deshabilitar el botón para evitar múltiples clics
    var saveButton = $("#btn_guardar");  // Suponiendo que tu botón tiene el id 'btn_guardar'
    saveButton.prop("disabled", true);

    var form = document.getElementsByName("form-vrt")[0];  
    var formData = new FormData(form);

    var checksArray = [];
    form.querySelectorAll("input[name='checks[]']:checked").forEach(function(checkbox) {
        checksArray.push(checkbox.value);
    });

    formData.append('checks', JSON.stringify(checksArray));

    $.ajax({
        url: "/upd_audit_checks/",  // URL del endpoint
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                Swal.fire("Éxito", "Auditoría actualizada correctamente", "success");
                $("#mdl_crud_audit").modal("hide");
                $('#table_audit').DataTable().ajax.reload();
            } else {
                Swal.fire("Error", response.error, "error");
            }
            // Volver a habilitar el botón
            saveButton.prop("disabled", false);
        },
        error: function() {
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
                    showConfirmButton: false
                });

                form.reset();
                obtener_checks_empresa(selectedValues); // Recargar select sin perder selección

                $("#mdl-crud-check").modal("hide").on('hidden.bs.modal', function () {
                    $(this).find("input, button, select").blur(); // Evitar error de `aria-hidden`
                });
            } else {
                Swal.fire({
                    title: "Error",
                    text: response.message || "Ocurrió un error inesperado",
                    icon: "error",
                    timer: 1500,
                    showConfirmButton: false
                });
            }
        },
        error: function (xhr, status, error) {
            console.error(" Error al agregar nuevo check:", status, error);
        }
    });
}

function add_vehicle_audit() {
    var modal = document.getElementById("mdl_crud_audit"); // O document.querySelector("#mdl_crud_audit")
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


function evaluate_audit(id) {
    var auditData = [];
    
    // Recorremos todas las filas de la tabla
    $('#audit-checks-table tbody tr').each(function() {
        var row = $(this);
        
        // Obtener el texto del <th> en la primera columna
        var name = row.find('th').text().trim();  

        // Obtener el valor seleccionado del <select> en la segunda columna
        var status = row.find('td.status select').val();  

        // Obtener el texto del <textarea> en la tercera columna
        var notas = row.find('td.notes textarea').val().trim();  

        // Crear un objeto con los datos
        var checkData = {
            id: name,    
            status: status, 
            notas: notas
        };


        // Añadir el objeto a la lista de auditoría
        auditData.push(checkData);
    });
    var audit_id = id; 

    // Enviar los datos via AJAX al backend
    $.ajax({
        url: "/evaluate_audit/",
        type: "POST",
        data: {
            'audit_id': audit_id,
            'audit_data': JSON.stringify(auditData),
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function(response) {
            if (response.success) {
                Swal.fire("Success", "Auditoria evaluada correctamente", "success");
                $('#table_audit').DataTable().ajax.reload();
                $("#update-audit-btn").hide()
            } else {
                Swal.fire("Error", response.error, "error");
            }
        },
        error: function() {
            Swal.fire("Error", "There was an error updating the audit", "error");
        }
    });
}


