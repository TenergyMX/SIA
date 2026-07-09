$(document).ready(function () {
    // table_plans();
    load_cards_plans();
});

function load_cards_plans() {
    console.log("planes activos");
    $.ajax({
        url: "/get_table_plans/",
        type: "GET",

        success: function (response) {
            if (response.status != "success") return;

            let html = "";

            response.data.forEach(function (plan) {
                let estado = plan.status_payment_plan
                    ? `<span class="badge bg-success">Activo</span>`
                    : `<span class="badge bg-danger">Inactivo</span>`;

                let modulos = "";

                plan.modules.split(",").forEach(function (m) {
                    modulos += `
                        <span class="badge bg-primary me-1 mb-1">
                            ${m.trim()}
                        </span>
                    `;
                });

                html += `

                <div class="col-md-6 col-xl-3 mb-3">

                    <div class="card shadow h-100">

                        <div class="card-header">

                            <h5 class="mb-0">
                                ${plan.company__name}
                            </h5>

                            ${estado}

                        </div>

                        <div class="card-body">

                            <p>
                                <strong>Plan:</strong>
                                ${plan.type_plan}
                            </p>

                            <p>
                                <strong>Módulos</strong>
                            </p>

                            <div class="mb-3">

                                ${modulos}

                            </div>

                            <div class="row">

                                <div class="col-6">
                                    <small class="text-muted">
                                        Inicio
                                    </small>

                                    <div>
                                        ${plan.start_date_plan}
                                    </div>
                                </div>

                                <div class="col-6">
                                    <small class="text-muted">
                                        Fin
                                    </small>

                                    <div>
                                        ${plan.end_date_plan}
                                    </div>
                                </div>

                            </div>

                            <hr>

                            <div class="row">

                                <div class="col-6">

                                    <small class="text-muted">
                                        Periodo
                                    </small>

                                    <div>
                                        ${plan.periodo}
                                    </div>

                                </div>

                                <div class="col-6">

                                    <small class="text-muted">
                                        Total
                                    </small>

                                    <div>
                                        $${plan.total}
                                    </div>

                                </div>

                            </div>

                        </div>

                        <div class="card-footer text-end">

                            ${plan.btn_action}

                        </div>

                    </div>

                </div>

                `;
            });

            $("#plans_container").html(html);

            swal.close();
        },
    });
}

//funcion para mostrar las empresas
function get_company_plan(selectedCompanyId) {
    $.ajax({
        url: "/get_company_plan/",
        type: "GET",
        success: function (response) {
            var select = $("#company_plan");
            select.html(null); // Limpiar las opciones existentes
            select.append(
                "<option value='' disabled selected>Seleccione una de las empresas existentes</option>"
            );
            $.each(response.data, function (index, value) {
                var selected = value.id == selectedCompanyId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las empresas existentes:", error);
            alert("Hubo un error al cargar las empresas existentes.");
        },
    });
}

// // Función para obtener los módulos y cargarlos en el select
// function get_modules_plan(selectedModuleId = []) {
//     console.log("selectedModuleId:", selectedModuleId);
//     console.log("Tipo:", typeof selectedModuleId);
//     console.log("Es arreglo:", Array.isArray(selectedModuleId));

//     if (!Array.isArray(selectedModuleId)) {
//         selectedModuleId = [String(selectedModuleId)];
//     } else {
//         selectedModuleId = selectedModuleId.map(String);
//     }

//     $.ajax({
//         url: "/get_modules_plan/",
//         type: "GET",
//         success: function (response) {
//             // var selected = selectedModuleId.includes(String(value.id)) ? "selected" : "";
//             var select = $("#modules_company");
//             select.empty();
//             // select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);

//             $.each(response.data, function (index, value) {
//                 var selected = selectedModuleId.includes(String(value.id)) ? "selected" : "";
//                 select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
//             });
//             select2module();
//             select.val(selectedModuleId).trigger("change");

//             // Si no se recibió ningún módulo, seleccionar TODOS
//             if (selectedModuleId.length === 0) {
//                 const allModules = response.data.map((m) => String(m.id));

//                 select.val(allModules).trigger("change");
//             }
//         },
//         error: function (xhr, status, error) {
//             console.error("Error al cargar los módulos:", error);
//             alert("Hubo un error al cargar los módulos.");
//         },
//     });
// }

// Función para mostrar el modal para agregar planes
// function add_plans() {
//     var obj_modal = $("#mdl-crud-plans");
//     obj_modal.modal("show");
//     // Configurar el modal para agregar
//     $("#mdl-crud-plans .modal-title").text("Agregar Plan");
//     $("#form_add_plan").attr("onsubmit", "add_plan(); return false");

//     // Establecer el valor predeterminado de 'is_active' a '1' para nuevos registros
//     $('#form_add_plan [name="is_active"]').val("1");

//     $("#modules_company").prop("disabled", false);

//     get_company_plan();
//     get_modules_plan();
// }

// // Función para agregar un plan
// function add_plan() {
//     console.log("la funcion para agregar un plan se esta ejecutando");
//     var form = $("#form_add_plan")[0];
//     var formData = new FormData(form);
//     console.log("esto contiene el fromdata de agregar:", formData);

//     $.ajax({
//         url: "/add_plan/",
//         type: "POST",
//         data: formData,
//         processData: false,
//         contentType: false,
//         success: function (response) {
//             if (response.success) {
//                 $("#form_add_plan")[0].reset();
//                 $("#mdl-crud-plans").modal("hide");
//                 Swal.fire({
//                     title: "¡Éxito!",
//                     text: response.message,
//                     icon: "success",
//                     timer: 1500,
//                 });
//                 //$("#table_plans").DataTable().ajax.reload();

//                 /**Swal Loader*/
//                 Swal.fire({
//                     title: "Actualizando catalago de planes registrados",
//                     allowOutsideClick: false,
//                     allowEscapeKey: false,
//                     showConfirmButton: false,
//                     didOpen: () => {
//                         Swal.showLoading();
//                         const htmlContainer = document.querySelector("#swal2-html-container");
//                         if (htmlContainer) {
//                             htmlContainer.style.display = "flex";
//                         }
//                     },
//                 });
//                 load_cards_plans();
//             } else {
//                 Swal.fire({
//                     title: "¡Error!",
//                     text: response.message,
//                     icon: "error",
//                     showConfirmButton: false,
//                 });
//             }
//         },
//         error: function (error) {
//             console.error("Error al guardar el plan:", error);
//             Swal.fire({
//                 title: "¡Error!",
//                 text: "Hubo un error al guardar el plan.",
//                 icon: "error",
//                 showConfirmButton: false,
//             });
//         },
//     });
// }

// // Evento para el botón de editar planes
// function edit_plan(boton) {
//     // var row = $(boton).closest("tr");
//     //var data = $("#table_plans").DataTable().row(row).data();
//     var pk = $(boton).data("value");
//     var order = $(boton).data("order");

//     get_row_plan(pk, order);
// }

// //funcion para editar los planes
// function edit_plans() {
//     var form = $("#form_add_plan")[0];
//     var formData = new FormData(form);
//     console.log("esto contiene el fromdata:", formData);

//     $.ajax({
//         url: "/edit_plans/",
//         type: "POST",
//         data: formData,
//         processData: false,
//         contentType: false,
//         beforeSend: function (xhr) {
//             var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
//             xhr.setRequestHeader("X-CSRFToken", csrfToken);
//         },
//         success: function (response) {
//             if (response.success) {
//                 $("#form_add_plan")[0].reset();
//                 $("#mdl-crud-plans").modal("hide");
//                 Swal.fire({
//                     title: "¡Éxito!",
//                     text: response.message,
//                     icon: "success",
//                     timer: 1500,
//                 });
//                 $("#table_plans").DataTable().ajax.reload();
//                 console.log("Tabla recargada después de editar");
//             } else {
//                 Swal.fire({
//                     title: "¡Error!",
//                     text: response.message,
//                     icon: "error",
//                 });
//             }
//         },
//         error: function (xhr, error) {
//             // Extraer el mensaje de error del servidor
//             let errorMessage = "Hubo un error al actualizar el plan.";
//             if (xhr.responseJSON && xhr.responseJSON.message) {
//                 errorMessage = xhr.responseJSON.message; // Mensaje del servidor
//             }

//             console.error("Error al actualizar el plan:", errorMessage);
//             Swal.fire({
//                 title: "¡Error!",
//                 text: errorMessage,
//                 icon: "error",
//             });
//         },
//     });
// }

function select2module() {
    $("#modules_company").select2({
        dropdownParent: $("#mdl-crud-plans"),
        placeholder: "Seleccione uno o varios módulos",
        allowClear: true,
        closeOnSelect: false,
        width: "100%",
    });
}

$("#modules_company").empty();
response.modules.forEach((module) => {
    $("#modules_company").append(new Option(module.name, module.id));
});
$("#modules_company").trigger("change");

// Función para cancelar un plan
function cancel_subscription(button) {
    let id = $(button).data("value");

    Swal.fire({
        title: "¿Cancelar suscripción?",
        text: "La suscripción será cancelada y no se realizarán más cobros.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, cancelar",
        cancelButtonText: "No",
        confirmButtonColor: "#d33",
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/cancel_subscription/",
                type: "POST",
                data: {
                    id: id,
                    csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
                },
                success: function (response) {
                    if (response.success) {
                        Swal.fire("Cancelada", response.message, "success");
                        table_plans();
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
            });
        }
    });
}

// function get_row_plan(pk, order = "") {
//     $.ajax({
//         url: "/get_table_plans/",
//         type: "GET",
//         data: {
//             pk: pk,
//         },
//         success: function (response) {
//             console.log(response);

//             $("#mdl-crud-plans").modal("show");
//             let data = response.data[0];

//             if (order == "edit") {
//                 $("#company_plan").prop("disabled", true);
//                 $("#modules_company").prop("disabled", true);
//             } else {
//                 $("#company_plan").prop("disabled", false);
//                 $("#modules_company").prop("disabled", false);
//             }

//             $("#mdl-crud-plans .modal-title").text("Editar Plan");

//             $('#form_add_plan [name="id"]').val(data.id);
//             $('#form_add_plan [name="company_plan"]').val(data.company__id);
//             // $('#form_add_plan [name="modules_company"]').val(data.module__id);
//             // $("#modules_company")
//             //     .val([String(data.module__id)])
//             //     .trigger("change");

//             // Mapeo de los valores de type_plan
//             var typePlanMap = {
//                 Básico: "basic",
//                 Avanzado: "advanced",
//                 Premium: "premium",
//             };

//             // Asignar el valor del tipo de plan usando el mapeo
//             var mappedTypePlan = typePlanMap[data.type_plan] || "";

//             $('#form_add_plan [name="type_plan"]').val(mappedTypePlan);
//             $('#form_add_plan [name="start_date_plan"]').val(data.start_date_plan);
//             $('#form_add_plan [name="time_quantity_plan"]').val(data.time_quantity_plan);
//             $('#form_add_plan [name="time_unit_plan"]').val(data.time_unit_plan);
//             $('#form_add_plan [name="status"]').val(data.status_payment_plan ? "1" : "0");
//             console.log("Valor del campo status:", $('#form_add_plan [name="status"]').val());

//             $("#form_add_plan").attr("onsubmit", "edit_plans(); return false");
//             $("#active-field").removeClass("d-none"); // Mostrar el campo 'is_active'
//             console.log(" Estos son los datos del formulario:", data);
//             console.log("Valor de type_plan:", data.type_plan);

//             get_company_plan(data.company__id);

//             console.log("esto contienen data", data);
//             console.log("modulos", data.module__id);
//             console.log(data.module_ids);

//             get_modules_plan(data.module__id);
//         },

//         error: function (xhr, status, error) {
//             console.error("Error al cargar las empresas existentes:", error);
//             alert("Hubo un error al cargar las empresas existentes.");
//         },
//     });
// }
