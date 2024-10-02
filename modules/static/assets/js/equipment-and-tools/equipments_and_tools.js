$(document).ready(function() {
    // Inicializar la tabla de datos
    $('#equipments_tools_table').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: '/get_equipments_tools_categorys/', 
            type: 'GET',
            dataSrc: 'data' 
        },
        columns: [
            { data: 'id' },
            { data: 'name' },
            { data: 'short_name' },
            { data: 'description' },
            {
                data: "is_active",
                render: function (d) {
                    return d
                        ? '<span class="badge bg-outline-success">Activo</span>'
                        : '<span class="badge bg-outline-danger">Inactivo</span>';
                },
                className: "toggleable",
            },
            { 
                data: null,
                defaultContent: "<button type='button' class='btn btn-icon btn-sm btn-primary-light edit-btn' onclick='edit_category_category(this)' aria-label='info'><i class='fa-solid fa-pen'></i></button> " +
                                "<button type='button' class='btn btn-icon btn-sm btn-danger-light delete-btn' onclick='delete_category(this)' aria-label='delete'><i class='fa-solid fa-trash'></i></button>",
                orderable: false
            }
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10
    });
    
    // Función para recargar la tabla
    function reloadTable() {
        table.ajax.reload(); // Esto recargará los datos de la tabla
    }

    // Manejar el clic en el botón de recargar
    $('#refreshTableButton').on('click', function() {
        reloadTable();
    });
});

// Función para mostrar el formulario
function add_category() {
    var obj_modal = $("#mdl-crud-equipments-tools-category");
    obj_modal.modal("show");
}
// Función para agregar una categoría
function add_equipment_category() {
    var form = $('#form_add_category_equip')[0];//id del formulario dentro del modal 
    var formData = new FormData(form);

    $.ajax({
        url: '/add_equipment_category/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_category_equip')[0].reset();//id del formulario dentro del modal
                $('#mdl-crud-equipments-tools-category').modal('hide');//id del modal 
                alert(response.message); // Mensaje de éxito
                $('#equipments_tools_table').DataTable().ajax.reload(); // Recargar la tabla
            } else {
                alert('An error occurred: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al guardar la categoría:", error);
            alert("Hubo un error al guardar la categoría.");
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    });
}
// Evento para el botón de editar
function edit_category_category(boton) {
    //crear una nueva instancia hacia la fila que se esta seleccionando 
    var row = $(boton).closest('tr');
    //busca en la tabla la fila que se obtiene al inicio y almacena toda la informacion de la misma
    var data = $('#equipments_tools_table').DataTable().row(row).data();
   
    // Mostrar el modal
    $('#mdl-crud-equipments-tools-category').modal('show');

    // Cambiar el título del modal para indicar que es una actualización
    $('#mdl-crud-equipments-tools-category .modal-title').text('Editar Categoría');
    // Cargar los datos en el formulario
    $('#form_add_category_equip [name="id"]').val(data.id);
    $('#form_add_category_equip [name="name"]').val(data.name);
    $('#form_add_category_equip [name="short_name"]').val(data.short_name);
    $('#form_add_category_equip [name="description"]').val(data.description)
    if (data.is_active == true){
        $('#form_add_category_equip [name="is_active"]').val("1");  
    }else{
        $('#form_add_category_equip [name="is_active"]').val("0");
    }
    //cambia la funcion del formulario para evitar
    $('#form_add_category_equip').attr('onsubmit', ' edit_category(); return false');

}
function edit_category(){
    var form = $('#form_add_category_equip')[0];
    var formData = new FormData(form);
    $('#form_add_category_equip').attr('onsubmit', ' add_category(); return false');

    $.ajax({
        url: '/edit_category/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_category_equip')[0].reset();
                $('#mdl-crud-equipments-tools-category').modal('hide');
                alert(response.message); // Mensaje de éxito
                $('#equipments_tools_table').DataTable().ajax.reload(); // Recargar la tabla
            } else {
                alert('An error occurred: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            console.error("Error al guardar la categoría:", error);
            alert("Hubo un error al guardar la categoría.");
        },
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
        }
    });
}
function delete_category(boton){
    var row = $(boton).closest('tr');
    var data = $('#equipments_tools_table').DataTable().row(row).data();

    console.log(data);

    if (confirm('¿Estás seguro de que quieres eliminar esta categoría?')) {
        $.ajax({
            url: '/delete_category/', 
            type: 'POST',
            data: {
                id: data.id
            },
            success: function(response) {
                if (response.success) {
                    alert(response.message); 
                    $('#equipments_tools_table').DataTable().ajax.reload(); 
                } else {
                    alert('An error occurred: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error("Error al eliminar la categoría:", error);
                alert("Hubo un error al eliminar la categoría.");
            },
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
            }
        });
    }
}