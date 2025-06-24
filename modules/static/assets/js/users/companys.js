class Company {
    constructor() {
        this.init();
    }

    init() {
        this.table_companys();
        this.loadCompanys(); // Llenar el select al inicializar
    }

    // Inicialización de la tabla
    table_companys() {
        this.table = $("#table_companys").DataTable({
            id: null,
            destroy: true,
            processing: true,
            ajax: {
                url: "/get_companys/",
                type: "GET",
                dataSrc: "data",
            },
            columns: [
                { title: "Id", data: "id" },
                { title: "Nombre", data: "name" },
                { title: "Dirección", data: "address" },
                {
                    title: "Acciones",
                    data: null,
                    render: (data, type, row) => {
                        return `
                            <button onclick="company.edit_companys(this)" class="btn btn-sm btn-primary mb-1">Editar</button>
                            <button onclick="company.delete_company(this)" class="btn btn-danger btn-sm mb-1">Eliminar</button>
                        `;
                    },
                },
            ],
            language: {
                url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
            },
            pageLength: 10,
        });
    }

    // Cargar las empresas en el select
    loadCompanys() {
        $.ajax({
            url: "/get_companys/",
            type: "GET",
            dataType: "json",
            success: (response) => {
                if (response.data) {
                    let select = $('select[name="company_id"]');
                    select.empty();
                    select.append('<option value="">Seleccione una empresa</option>');

                    response.data.forEach((company) => {
                        select.append(`<option value="${company.id}">${company.name}</option>`);
                    });
                }
            },
            error: (error) => {
                console.error("Error cargando empresas:", error);
            },
        });
    }

    // Mostrar el modal para agregar una empresa
    add_companys(button) {
        $("#mdl_crud_company").modal("show");
        let row = $(button).closest("tr");
        let data = this.table.row(row).data();
    }

    // Función para agregar una empresa
    add_company() {
        let form = $("#form_add_company")[0];
        let formData = new FormData(form);

        $.ajax({
            url: "/add_company/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            headers: { "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val() },
            success: (response) => {
                if (response.success) {
                    $("#form_add_company")[0].reset();
                    $("#mdl_crud_company").modal("hide");
                    Swal.fire("¡Éxito!", response.message, "success");
                    this.reloadTable(); // Recargar la tabla
                    this.loadCompanys(); // Recargar el select
                } else {
                    Swal.fire("¡Error!", response.message, "error");
                }
            },
            error: (error) => {
                console.error("Error al guardar la empresa:", error);
                Swal.fire("¡Error!", "Hubo un error al guardar la empresa.", "error");
            },
        });
    }

    // Mostrar el modal para editar una empresa
    edit_companys(button) {
        let row = $(button).closest("tr");
        let data = this.table.row(row).data();
        $("#mdl_crud_company").modal("show");
        $("#mdl_crud_company .modal-title").text("Editar Empresa");

        $('#form_add_company [name="id"]').val(data.id);
        $('#form_add_company [name="name"]').val(data.name);
        $('#form_add_company [name="address"]').val(data.address);
        $('#form_add_company [name="email_company"]').val(data.email_company);
        $("#form_add_company").attr("onsubmit", "company.edit_company(); return false;");
    }

    // Función para editar una empresa
    edit_company() {
        let form = $("#form_add_company")[0];
        let formData = new FormData(form);

        $.ajax({
            url: "/edit_company/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            headers: { "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val() },
            success: (response) => {
                if (response.success) {
                    $("#form_add_company")[0].reset();
                    $("#mdl_crud_company").modal("hide");
                    Swal.fire("¡Éxito!", response.message, "success");
                    this.reloadTable();
                    this.loadCompanys();
                } else {
                    Swal.fire("¡Error!", response.message, "error");
                }
            },
            error: (xhr, error) => {
                let errorMessage =
                    xhr.responseJSON?.message || "Hubo un error al actualizar la empresa.";
                console.error("Error al actualizar la empresa:", errorMessage);
                Swal.fire("¡Error!", errorMessage, "error");
            },
        });
    }

    // Función para eliminar una empresa
    delete_company(button) {
        let row = $(button).closest("tr");
        let data = this.table.row(row).data();

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
                $.ajax({
                    url: "/delete_company/",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ id: data.id }),
                    headers: { "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val() },
                    success: (response) => {
                        if (response.success) {
                            Swal.fire("¡Eliminado!", response.message, "success").then(() => {
                                this.reloadTable(); // Recargar la tabla
                                this.loadCompanys(); // Recargar el select
                            });
                        } else {
                            Swal.fire("Error", response.message, "error");
                        }
                    },
                    error: (error) => {
                        console.error("Error al eliminar la empresa:", error);
                        Swal.fire("Error", "Hubo un error al eliminar la empresa.", "error");
                    },
                });
            }
        });
    }

    // Función para recargar la tabla
    reloadTable() {
        this.table.ajax.reload(null, false); // Mantener la página actual
    }
}

const company = new Company();
