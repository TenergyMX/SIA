$(document).ready(function() {
table_plans();
});

// Función para mostrar la tabla 
function table_plans() {
    $('#table_plans').DataTable({
        destroy: true,  
        processing: true,
        ajax: {
            url: "/get_table_plans/",  
            type: 'GET',
            dataSrc: function (json) {
                json.data.forEach(function (item) {
                    item.status_payment_plan = item.status_payment_plan === 'Activo'; 
                });
                return json.data;  
            }
        },
        columns: [
            { data: 'id' },
            { data: 'company__name' },  
            { data: 'module__name' },  
            { data: 'type_plan' },
            { data: 'start_date_plan' },
            { data: 'periodo' },  
            { data: 'end_date_plan' },
            { data: 'total' },
            {
                data: "status_payment_plan",
                render: function (d) {
                    return d
                        ? '<span class="badge bg-outline-success">Activo</span>'
                        : '<span class="badge bg-outline-danger">Inactivo</span>';
                },
                className: "toggleable",
            },
            { data: 'btn_action' }  
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10
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

// Función para obtener los módulos y cargarlos en el select
function get_modules_plan(selectedModuleId) {
    $.ajax({
        url: "/get_modules_plan/",  
        type: "GET",
        success: function (response) {
            var select = $("#modules_company");
            select.html(null); 
            select.append(
                "<option value='' disabled>Seleccione el módulo</option>"
            );
            $.each(response.data, function (index, value) {
                var selected = value.id == selectedModuleId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los módulos:", error);
            alert("Hubo un error al cargar los módulos.");
        },
    });
}

// Función para mostrar el modal para agregar planes
function add_plans(button) {
    console.log("la funcion para mostrar el modal esta siendo llamada")
    var obj_modal = $("#mdl-crud-plans");
    obj_modal.modal("show");
    // Configurar el modal para agregar
    $('#mdl-crud-plans .modal-title').text('Agregar Plan');
    $('#form_add_plan').attr('onsubmit', 'add_plan(); return false');
    
    // Establecer el valor predeterminado de 'is_active' a '1' para nuevos registros
    $('#form_add_plan [name="is_active"]').val('1');

    get_company_plan();
    get_modules_plan();
}

// Función para agregar un plan
function add_plan() {
    console.log("la funcion para agregar un plan se esta ejecutando")
    var form = $('#form_add_plan')[0];
    var formData = new FormData(form);
    console.log("esto contiene el fromdata de agregar:", formData);

    $.ajax({
        url: '/add_plan/',  
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_plan')[0].reset();
                $('#mdl-crud-plans').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_plans').DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    showConfirmButton: false,
                });
            }
        },
        error: function(error) {
            console.error("Error al guardar el plan:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al guardar el plan.",
                icon: "error",
                showConfirmButton: false,
            });
        },
    });
}

// Evento para el botón de editar planes
function edit_plan(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_plans').DataTable().row(row).data();
    $('#mdl-crud-plans').modal('show');

    $('#mdl-crud-plans .modal-title').text('Editar Plan');

    $('#form_add_plan [name="id"]').val(data.id);
    $('#form_add_plan [name="company_plan"]').val(data.company__id);
    $('#form_add_plan [name="modules_company"]').val(data.module__id);
    // Mapeo de los valores de type_plan
    var typePlanMap = {
        "Básico": "basic",
        "Avanzado": "advanced",
        "Premium": "premium"
    };

    // Asignar el valor del tipo de plan usando el mapeo
    var mappedTypePlan = typePlanMap[data.type_plan] || ""; 

    $('#form_add_plan [name="type_plan"]').val(mappedTypePlan);
    $('#form_add_plan [name="start_date_plan"]').val(data.start_date_plan);
    $('#form_add_plan [name="time_quantity_plan"]').val(data.time_quantity_plan);
    $('#form_add_plan [name="time_unit_plan"]').val(data.time_unit_plan);
    $('#form_add_plan [name="status"]').val(data.status_payment_plan ? "1" : "0");
    console.log("Valor del campo status:", $('#form_add_plan [name="status"]').val());



    get_company_plan(data.company__id);
    get_modules_plan(data.module__id);

    $('#form_add_plan').attr('onsubmit', 'edit_plans(); return false');
    $('#active-field').removeClass('d-none'); // Mostrar el campo 'is_active'
    console.log(" Estos son los datos del formulario:",data);
    console.log("Valor de type_plan:", data.type_plan);
}

//funcion para editar los planes
function edit_plans() {
    var form = $('#form_add_plan')[0];
    var formData = new FormData(form);
    console.log("esto contiene el fromdata:", formData);
    
    $.ajax({
        url: '/edit_plans/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function(xhr) {
            var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        success: function(response) {
            if (response.success) {
                $('#form_add_plan')[0].reset();
                $('#mdl-crud-plans').modal('hide');
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500
                });
                $('#table_plans').DataTable().ajax.reload(); 
                console.log("Tabla recargada después de editar");
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },
        error: function(xhr, error) {
            // Extraer el mensaje de error del servidor
            let errorMessage = "Hubo un error al actualizar el plan.";
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message; // Mensaje del servidor
            }

            console.error("Error al actualizar el plan:", errorMessage);
            Swal.fire({
                title: "¡Error!",
                text: errorMessage,
                icon: "error",
            });
        },
    });
}

// Función para eliminar un plan
function delete_plan(boton) {
    var row = $(boton).closest('tr');
    var data = $('#table_plans').DataTable().row(row).data();
    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, elimínalo!"
    }).then((result) => {
        if (result.isConfirmed) {
            // Si el usuario confirma la eliminación, hacer la solicitud AJAX
            $.ajax({
                url: '/delete_plans/',
                type: 'POST',
                data: {
                    id: data.id
                },
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
                },
                success: function(response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500
                        }).then(() => {
                            // Recargar la tabla después de la eliminación exitosa
                            $('#table_plans').DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function(error) {
                    console.error("Error al eliminar la categoría:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la categoría.", "error");
                }
            });
        }
    });
}

