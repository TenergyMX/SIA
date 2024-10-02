$(document).ready(function() {
    // Inicializar la tabla de datos
    $('#equipments_tools_table').DataTable({//id de la tabla del html
        destroy: true,
        processing: true,
        ajax: {
            url: '/get_equipments_tools/', 
            type: 'GET',
            dataSrc: 'data' 
        },
        columns: [
            { data: 'id' },
            { data: 'equipment_category' },
            { data: 'equipment_name' },
            { data: 'equipment_type' },
            { data: 'equipment_brand'},
            { data: 'equipment_description'},
            { data: 'cost'},
            { data: 'amount'},
            { data: 'equipment_technical_sheet'},
            { data: 'equipment_area'},
            { data: 'equipment_responsible'},
            { data: 'equipment_location'},
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
function add_equipment() {
    var obj_modal = $("#mdl-crud-equipments-tools");
    obj_modal.modal("show");
}



// Función para agregar una equipo o herramienta
function add_equipment_tools() {
    var form = $('#form_add_equipments_tools')[0];//id del formulario dentro del modal 
    var formData = new FormData(form);

    $.ajax({
        url: '/add_equipment_tools/', 
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                $('#form_add_equipments_tools')[0].reset();//id del formulario dentro del modal
                $('#mdl-crud-equipments-tools').modal('hide');//id del modal 
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