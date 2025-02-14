$(document).ready(function() {
    table_driver_vehicles();
});

function table_driver_vehicles() {
    $('#table_driver_vehicles').DataTable({
        destroy: true,
        processing: true,
        ajax: {
            url: "/get_table_vehicles_driver/",
            type: 'GET',
            dataSrc: 'data',
            error: function(xhr, error, thrown) {
                console.error("Error en la carga de datos: ", error);
                alert("No se pudo cargar la información de los conductores");
            }
        },
        columns: [
            { data: 'id' },
            {
                data: "is_active_category",
                render: function (d) {
                    return d
                        ? '<span class="badge bg-outline-success">Activo</span>'
                        : '<span class="badge bg-outline-danger">Inactivo</span>';
                },
                className: "toggleable",
            },
            { 
                data: "btn_action",
                render: function(data, type, row) {
                    return data;  
                }
            }
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        pageLength: 10
    });
}