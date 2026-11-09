var user_id = 0;

//Responsables de equipos de computo
const responsables = new Users({
    //list: { id: ".modal select[name='responsible_id']" },
    list: {
        id: "#mdl_crud_computerSystem select[name='current_responsible_id']",
    },
});

// Responsables de periféricos
const responsablesPerifericos = new Users({
    list: {
        id: "#mdl_crud_computerPeripheral select[name='responsible_id']",
    },
});

const areas = new Areas({
    list: {
        id: "#mdl_crud_computerSystem select[name='area_id']",
    },
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

// Al seleccionar una empresa, cargar sus áreas y responsables para duplicar computadoras
$(document)
    .off("change", "#equipment_company")
    .on("change", "#equipment_company", function () {
        console.log("Esta es la funcion para cargar los usuarios y areas dentro del formulario");
        const companyId = $(this).val();

        if (!companyId) {
            $("#double_area_id")
                .empty()
                .append('<option value="">Seleccione una empresa primero</option>')
                .prop("disabled", true);

            $("#double_current_responsible_id")
                .empty()
                .append('<option value="">Seleccione una empresa primero</option>')
                .prop("disabled", true);

            return;
        }

        loadCompanyAreas(companyId);

        loadCompanyResponsibles(companyId);
    });

// Al seleccionar una empresa, cargar sus usuarios para duplicar computadoras
$(document)
    .off("change", "#equipment_company")
    .on("change", "#equipment_company", function () {
        const companyId = $(this).val();

        if (!companyId) {
            $("#double_current_responsible_id")
                .empty()
                .append("<option value  Seleccione una empresa primero</option>")
                .prop("disabled", true);

            return;
        }

        loadCompanyResponsiblesPeripheral(companyId);
    });

// Baja de equipos de cómputo
$(document)
    .off("submit", "#formdisableComputer")
    .on("submit", "#formdisableComputer", function (e) {
        e.preventDefault();
        disable_computer_system(this, equipos.tbl_computerEquipment);
    });

// Baja de periféricos
$(document)
    .off("submit", "#formdisablePeripheral")
    .on("submit", "#formdisablePeripheral", function (e) {
        e.preventDefault();
        disable_computer_peripheral(this, perifericos.tbl_computerPeripheral);
    });
