$(document).ready(function () {
    // Inicializar la tabla de datos
    $("#equipments_tools_table").DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_equipments_tools_categorys/",
            type: "GET",
            dataSrc: "data",
        },
        columns: [
            { data: "id" },
            { data: "name" },
            { data: "short_name" },
            { data: "description" },
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
                data: "btn_action",
                render: function (data, type, row) {
                    return data;
                },
            },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10,
    });
});

// Función para mostrar el formulario en modo agregar
function add_category() {
    var obj_modal = $("#mdl-crud-equipments-tools-category");
    obj_modal.modal("show");

    // Configurar el modal para agregar
    $("#mdl-crud-equipments-tools-category .modal-title").text("Agregar Categoría");
    $("#form_add_category_equip").attr("onsubmit", "add_equipment_category(); return false");

    // Establecer el valor predeterminado de 'is_active' a '1' para nuevos registros
    $('#form_add_category_equip [name="is_active"]').val("1");
    $("#active-field").addClass("d-none"); // Ocultar el campo 'is_active'
}

// Función para agregar una categoría
function add_equipment_category() {
    var form = $("#form_add_category_equip")[0];
    var formData = new FormData(form);
    $.ajax({
        url: "/add_equipment_category/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_category_equip")[0].reset();
                $("#mdl-crud-equipments-tools-category").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#equipments_tools_table").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    showConfirmButton: false,
                    timer: 1500,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al guardar la categoría:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                showConfirmButton: false,
                timer: 1500,
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// Evento para el botón de editar
function edit_category_category(boton) {
    var row = $(boton).closest("tr");
    var data = $("#equipments_tools_table").DataTable().row(row).data();

    // Mostrar el modal
    $("#mdl-crud-equipments-tools-category").modal("show");

    // Cambiar el título del modal para indicar que es una actualización
    $("#mdl-crud-equipments-tools-category .modal-title").text("Editar Categoría");

    // Cargar los datos en el formulario
    $('#form_add_category_equip [name="id"]').val(data.id);
    $('#form_add_category_equip [name="name"]').val(data.name);
    $('#form_add_category_equip [name="short_name"]').val(data.short_name);
    $('#form_add_category_equip [name="description"]').val(data.description);
    $('#form_add_category_equip [name="is_active"]').val(data.is_active ? "1" : "0");

    // Configurar el formulario para editar
    $("#form_add_category_equip").attr("onsubmit", "edit_category(); return false");
    $("#active-field").removeClass("d-none"); // Mostrar el campo 'is_active'
}

// Función para editar una categoría
function edit_category() {
    var form = $("#form_add_category_equip")[0];
    var formData = new FormData(form);

        // Validar campos
        var name = formData.get('name').trim();
        var shortName = formData.get('short_name').trim();
        var description = formData.get('description').trim();
    
        if (!name || !shortName || !description) {
            Swal.fire({
                title: "¡Error!",
                text: "Todos los campos son obligatorios.",
                icon: "error",
                showConfirmButton: true
            });
            return;
        }
    
    $.ajax({
        url: "/edit_category/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success) {
                $("#form_add_category_equip")[0].reset();
                $("#mdl-crud-equipments-tools-category").modal("hide");
                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
                $("#equipments_tools_table").DataTable().ajax.reload();
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                    timer: 1500,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al guardar la categoría:", error);
            Swal.fire({
                title: "¡Error!",
                text: response.message,
                icon: "error",
                timer: 1500,
            });
        },
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

// Función para eliminar una categoría
function delete_category(boton) {
    var row = $(boton).closest("tr");
    var data = $("#equipments_tools_table").DataTable().row(row).data();

    Swal.fire({
        title: "¿Estás seguro?",
        text: "¡No podrás revertir esta acción!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Sí, elimínalo!",
    }).then((result) => {
        if (result.isConfirmed) {
            // Si el usuario confirma la eliminación, hacer la solicitud AJAX
            $.ajax({
                url: "/delete_category/",
                type: "POST",
                data: {
                    id: data.id,
                },
                beforeSend: function (xhr) {
                    xhr.setRequestHeader(
                        "X-CSRFToken",
                        $('input[name="csrfmiddlewaretoken"]').val()
                    );
                },
                success: function (response) {
                    if (response.success) {
                        Swal.fire({
                            title: "¡Eliminado!",
                            text: response.message,
                            icon: "success",
                            timer: 1500,
                        }).then(() => {
                            // Recargar la tabla después de la eliminación exitosa
                            $("#equipments_tools_table").DataTable().ajax.reload();
                        });
                    } else {
                        Swal.fire("Error", response.message, "error");
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Error al eliminar la categoría:", error);
                    Swal.fire("Error", "Hubo un error al eliminar la categoría.", "error");
                },
            });
        }
    });
}
