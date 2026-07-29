class VehicleResponsiva {
    constructor(options = {}) {
        this.options = $.extend(
            true,
            {
                table: {
                    id: "#table_responsiva_vehicle",
                    ajax: {
                        url: "/table_vehicle_responsiva_view/",
                        dataSrc: "data",
                        data: {},
                    },
                },
            },
            options
        );

        this.loadTable();
        this.events();
    }

    // tabla
    loadTable() {
        $(this.options.table.id).DataTable({
            destroy: true,
            processing: true,

            ajax: this.options.table.ajax,

            columns: [
                {
                    title: "Responsable",
                    data: function (d) {
                        return `${d.responsible_vehicle__first_name ?? ""} ${d.responsible_vehicle__last_name ?? ""}`;
                    },
                },

                {
                    title: "Creado",
                    data: "created_at",
                    render: function (data) {
                        return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                    },
                },

                {
                    title: "Última actualización",
                    data: "updated_at",
                    render: function (data) {
                        return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                    },
                },

                {
                    title: "Responsiva",
                    data: function (d) {
                        if (d.responsibility_vehicle_pdf) {
                            return `
                                <a
                                    href="${d.responsibility_vehicle_pdf}"
                                    target="_blank"
                                    class="btn btn-sm btn-outline-primary">
                                    Responsiva
                                </a>
                            `;
                        }

                        return "Sin Responsiva";
                    },
                    orderable: false,
                },

                {
                    title: "Historial",
                    data: function () {
                        return `
                            <button
                                class="btn btn-sm btn-outline-primary"
                                data-vehicle-responsiva="history">

                                Historial
                            </button>
                        `;
                    },
                    orderable: false,
                },

                {
                    title: "Acciones",
                    data: "btn_action",
                    orderable: false,
                },
            ],

            language: {
                url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
            },
        });
    }

    // eventos
    events() {
        console.log("Eventos cargados en vehiculos ");

        const self = this;

        // Agregar responsiva
        $(document).on("click", "[data-vehicle-responsiva='add-responsive-vehicle']", function () {
            const modal = $("#mdl-crud-responsiva-vehicle");

            // Limpiar formulario
            modal.find("form")[0].reset();

            // Reiniciar id
            modal.find("input[name='id']").val(0);

            // Limpiar select
            modal.find("select[name='responsible_vehicle']").val(null).trigger("change");

            // Limpiar archivo
            modal.find("input[name='responsibility_vehicle_pdf']").val("");

            // Cambiar título
            modal.find(".modal-title").text("Agregar responsiva");

            // Mostrar/Ocultar botones
            modal.find("button[name='add']").removeClass("d-none");
            modal.find("button[name='update']").addClass("d-none");

            $.ajax({
                url: "/get_users_vehicle_responsiva/",
                type: "GET",
                success: function (response) {
                    const select = $("select[name='responsible_vehicle']");

                    select.empty();

                    select.append(`<option value="">Seleccione...</option>`);

                    response.data.forEach(function (item) {
                        select.append(`
                            <option value="${item.id}">
                                ${item.first_name} ${item.last_name}
                            </option>
                        `);
                    });
                },
            });

            // Mostrar modal
            const bsModal = new bootstrap.Modal(
                document.getElementById("mdl-crud-responsiva-vehicle")
            );

            bsModal.show();
        });

        // Generar carta responsiva
        $(document).on("click", "[data-vehicle-responsiva='generate-pdf']", function () {
            console.log("Entró al evento");

            const responsible_id = $("#mdl-crud-responsiva-vehicle")
                .find("select[name='responsible_vehicle']")
                .val();

            console.log("Responsable:", responsible_id);

            if (!responsible_id) {
                Swal.fire("Aviso", "Seleccione un responsable", "warning");
                return;
            }

            const url = `/vehicle_responsiva_pdf_view/?user_id=${responsible_id}`;

            console.log(url);

            window.open(url, "_blank");
        });

        // Crud responsiva
        $(document).on("submit", "#frm-vehicle-responsiva", function (e) {
            e.preventDefault();

            console.log("Entró al submit");

            const submit = $(e.originalEvent.submitter).attr("name");

            console.log("Botón presionado:", submit);

            let url = "";

            switch (submit) {
                case "add":
                    url = "/add_vehicle_responsiva_pdf/";
                    break;

                case "update":
                    url = "/update_vehicle_responsiva_pdf/";
                    break;

                default:
                    console.log("No se identificó acción");
                    return;
            }

            const formData = new FormData(this);

            console.log("Datos enviados:");

            for (let pair of formData.entries()) {
                console.log(pair[0], pair[1]);
            }

            $.ajax({
                url: url,
                type: "POST",
                data: formData,
                processData: false,
                contentType: false,
                success: function (response) {
                    console.log(response);

                    if (response.status == "success") {
                        Swal.fire({
                            icon: "success",
                            title:
                                submit === "update"
                                    ? "Actualizado Correctamente"
                                    : "Agregado Correctamente",
                            text: response.message,
                            timer: 1500,
                            showConfirmButton: false,
                        });

                        bootstrap.Modal.getInstance(
                            document.getElementById("mdl-crud-responsiva-vehicle")
                        ).hide();

                        $("#table_responsiva_vehicle").DataTable().ajax.reload(null, false);
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: response.message,
                        });
                    }
                },
            });
        });

        // Editar responsiva
        $(document).on("click", "[data-vehicle-responsiva='update-responsiva']", function () {
            const id = $(this).data("id");

            $.ajax({
                url: "/update_vehicle_responsiva_pdf/",
                type: "GET",
                data: {
                    id: id,
                },

                success: function (response) {
                    if (response.status !== "success") {
                        Swal.fire("Error", response.message, "error");
                        return;
                    }

                    const item = response.data;

                    const modal = $("#mdl-crud-responsiva-vehicle");

                    // Limpiar formulario
                    modal.find("form")[0].reset();

                    // Cargar usuarios
                    $.ajax({
                        url: "/get_users_vehicle_responsiva/",
                        type: "GET",

                        success: function (usuarios) {
                            const select = modal.find("select[name='responsible_vehicle']");

                            select.empty();

                            select.append(`<option value="">Seleccione...</option>`);

                            usuarios.data.forEach(function (user) {
                                select.append(`
                                    <option value="${user.id}">
                                        ${user.first_name} ${user.last_name}
                                    </option>
                                `);
                            });

                            // Seleccionar responsable
                            select.val(item.responsible_vehicle_id);
                        },
                    });

                    modal.find("input[name='id']").val(item.id);

                    modal.find(".modal-title").text("Editar responsiva");

                    modal.find("button[name='add']").addClass("d-none");
                    modal.find("button[name='update']").removeClass("d-none");

                    new bootstrap.Modal(
                        document.getElementById("mdl-crud-responsiva-vehicle")
                    ).show();
                },
            });
        });

        // Historial responsiva
        $(document).on("click", "[data-vehicle-responsiva='history']", function () {
            const modal = $("#mdl-crud-vehicle-responsiva-record");

            modal.modal("show");

            // Obtener fila seleccionada
            const fila = $(this).closest("tr");

            // Obtener datos del DataTable
            const datos = $("#table_responsiva_vehicle").DataTable().row(fila).data();

            console.log("Datos historial:", datos);

            let record = [];

            try {
                record = JSON.parse(datos.record || "[]");
            } catch (error) {
                console.error("Error leyendo historial:", error);
            }

            const tbody = modal.find("table tbody");

            tbody.empty();

            if (record.length === 0) {
                tbody.append(`
                        <tr>
                            <td colspan="3" class="text-center">
                                Sin historial disponible
                            </td>
                        </tr>
                    `);

                return;
            }

            $.each(record, function (index, value) {
                const formattedDate = value.date
                    ? moment(value.date).locale("es").format("D [de] MMMM [de] YYYY")
                    : "-----";

                const tr = `
                        <tr>
                            <td>${value.id}</td>
                            <td>${formattedDate}</td>
                            <td>
                                <a 
                                    href="${value.file_path}" 
                                    target="_blank"
                                    class="btn btn-sm btn-outline-primary">

                                    Responsiva

                                </a>
                            </td>
                        </tr>
                    `;

                tbody.append(tr);
            });
        });

        // Eliminar responsiva
        $(document).on("click", "[data-vehicle-responsiva='delete-responsiva']", function () {
            const fila = $(this).closest("tr");

            const datos = $("#table_responsiva_vehicle").DataTable().row(fila).data();

            console.log("Registro a eliminar:", datos);

            Swal.fire({
                title: "¿Está seguro?",
                text: "Esta acción eliminará la responsiva.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Sí, eliminar",
                cancelButtonText: "Cancelar",
            }).then((result) => {
                if (!result.isConfirmed) {
                    return;
                }

                const data = new FormData();

                data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());

                data.append("id", datos.id);

                deleteItem("/delete_vehicle_responsiva_pdf/", data)
                    .then((message) => {
                        Swal.fire("Éxito", "Se ha borrado el registro", "success");

                        $("#table_responsiva_vehicle").DataTable().ajax.reload(null, false);
                    })

                    .catch((error) => {
                        console.error(error);

                        Swal.fire(
                            "Error",
                            typeof error === "string"
                                ? error
                                : "Se produjo un problema en el servidor.",
                            "error"
                        );
                    });
            });
        });
    }
}

$(function () {
    new VehicleResponsiva();
});
