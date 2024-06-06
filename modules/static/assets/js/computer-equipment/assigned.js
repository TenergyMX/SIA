var user_id = 0;

const responsables = new Users({
    list: { id: ".modal select[name='responsible_id']" },
});

const equipos = new ComputerEquipment({
    data: { responsible_id: user_id },
    table: { id: "#computer_equipment_table" },
    // list: {},
});

const perifericos = new ComputerPeripheral({
    data: { responsible_id: user_id },
    table: {},
});

var tbl_software = $("#users_assigned_table").DataTable({
    ajax: {
        url: "/get_users_with_assigned_computer_equipment/",
    },
    columns: [
        { title: "Usuario", data: "username", visible: false },
        { title: "Nombre", data: "first_name" },
        { title: "Apellido", data: "last_name" },
        {
            title: '<i class="fa-solid fa-gear"></i>',
            data: function (d) {
                return `<button class="btn btn-icon btn-sm btn-primary-light" onclick="update_tables(${d["id"]})">
                    <i class="fa-solid fa-magnifying-glass"></i>
                </button>`;
            },
            orderable: false,
        },
    ],
    language: {
        url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
    },
    dom:
        "<'row g-2 justify-content-between'<'col-md-auto mx-auto'l><'col-md-auto mx-auto'f>>" +
        "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
        "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
});

function update_tables(responsible_id) {
    user_id = responsible_id;
    equipos.data["responsible_id"] = responsible_id;
    equipos.tbl_computerEquipment.ajax.reload();

    perifericos.data["responsible_id"] = responsible_id;
    perifericos.tbl_computerPeripheral.ajax.reload();
}
