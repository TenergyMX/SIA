class InfrastructureItem {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            infoCard: {
                id: null,
                ajax: {
                    url: function () {
                        return "/get-infrastructure-items/";
                    },
                    data: function () {},
                    reload: function () {},
                },
            },
            list: {
                id: null,
                ajax: {},
                data: {
                    isList: true,
                    category_id: 1,
                    category__name: "Se tenia que decir y se dijo",
                },
            },
            table: {
                id: "#computer_equipment_table",
                ajax: {
                    url: "/get-infrastructure-items/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Id", data: "id", className: "toggleable" },
                    { title: "Categoría", data: "category__name", className: "toggleable" },
                    { title: "Nombre", data: "name", className: "toggleable" },
                    { title: "Cantidad", data: "quantity", className: "toggleable" },
                    { title: "Costo", data: "cost", className: "toggleable" },
                    { title: "Descripción", data: "description", className: "toggleable" },
                    {
                        title: "Fecha de inicio",
                        data: "start_date",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "Ficha tecnica",
                        data: function (d) {
                            if (d["technical_sheet"]) {
                                return `<a href="${d["technical_sheet"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Ver Ficha
                                </a>`;
                            } else {
                                return "Sin ficha técnica";
                            }
                        },
                        orderable: false,
                        className: "toggleable",
                    },
                    {
                        title: "Factura",
                        data: function (d) {
                            if (d["invoice"]) {
                                return `<a href="${d["invoice"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Ver factura
                                </a>`;
                            } else {
                                return "Sin factura";
                            }
                        },
                        orderable: false,
                        className: "toggleable",
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.list) {
            var mergedListOptions = deepMerge(defaultOptions.list, options.list);
            self.list = { ...defaultOptions.list, ...mergedListOptions };

            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-infrastructure-items/",
                    data: self.list.data,
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        select.append("<option value='' data-category-id>-----</option>");
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}" data-category-id="${value["category_id"]}">
                                    ${value["name"]}
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
                    complete: function () {},
                });
            };
            self.dataList = {};
        }

        if (options.table) {
            var mergedTableOptions = deepMerge(defaultOptions.table, options.table);
            self.table = { ...defaultOptions.table, ...mergedTableOptions };
        }

        self.init();
    }

    init() {
        const self = this;

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_infraesstructure_items = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function (d) {
                        return self.data;
                    },
                },
                columns: self.table.columns,
                order: [[0, "desc"]],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                dom:
                    "<'row justify-content-between'<'col-md'l><'col-md text-center'B><'col-md'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
                buttons: [
                    {
                        extend: "colvis",
                        text: "Columnas",
                        columns: function (idx, data, node) {
                            return $(node).hasClass("toggleable");
                        },
                        className: "btn-sm",
                    },
                ],
                initComplete: function (settings, json) {},
            });

            delete self.table;
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-infrastructure-item");

        $(document).on("click", "[data-infrastructure-item]", function (e) {
            var obj = $(this);
            var option = obj.data("infrastructure-item");

            switch (option) {
                case "refresh-table":
                    self.tbl_infraesstructure_items.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Registrar items de infraestructura");

                    get_items_locations(null);
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                case "update-item":
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infraesstructure_items.row(fila).data();

                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar item de infraestructura");

                    get_items_locations(datos["location_id"]); //

                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name="${index}"]`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name="${index}"]`).val(value || null);
                        }
                    });

                    obj_modal
                        .find("[name='is_active']")
                        .val(datos["is_active"] == true ? "1" : "0");
                    break;

                case "delete-item":
                    var url = "/delete-infrastructure-item/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infraesstructure_items.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());

                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire({
                                title: "Éxito",
                                text: message,
                                icon: "success",
                            });

                            self.tbl_infraesstructure_items.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire({
                                title: "Error",
                                text: error,
                                icon: "error",
                            });
                        });

                    break;

                default:
                    console.log("Opción dezconocida: " + option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-infrastructure-item/";
            var datos = new FormData(this);

            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,
                success: function (response) {
                    var message = response.message || "Ocurrió un error inesperado";
                    if (response.status == "error") {
                        Swal.fire("Error", response.message, "error");
                        return;
                    } else if (response.status == "warning") {
                        Swal.fire("Advertencia", response.message, "warning");
                        return;
                    } else if (response.status != "success") {
                        Swal.fire("Oops", message, "error");
                        return;
                    }
                    self.tbl_infraesstructure_items.ajax.reload();
                    message = response.message || "Se han guardado los datos con éxito";
                    Swal.fire("Éxito", message, "success");
                    obj_modal.modal("hide");
                },
                error: function (xhr, status, error) {
                    var message =
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        message = xhr.responseJSON.message;
                    }
                    Swal.fire("Error", message, "error");
                },
            });
        });
    }
}

//funcion para mostrar las opciones en el select al momento de cargar el modal para agregar una nueva ubicacion
function get_items_locations(selectedLocationId) {
    $.ajax({
        url: "/get_items_locations/",
        type: "GET",
        success: function (response) {
            const select = $("#item_location");
            select.html(
                "<option value='' disabled selected>Seleccione una de las ubicaciones existentes</option>"
            );
            $.each(response.data, function (index, location) {
                const selected = location.id == selectedLocationId ? "selected" : "";
                select.append(
                    `<option value="${location.id}" ${selected}>${location.name}</option>`
                );
            });
            // opción para agregar una nueva ubicación
            select.append('<option value="add_new">Agregar otra ubicación no existente</option>');
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las ubicaciones:", error);
            alert("Hubo un error al cargar las ubicaciones. Inténtelo de nuevo más tarde.");
        },
    });
}

//fucion para mostrar el modal de una nueva ubicacion
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("item_location").addEventListener("change", function () {
        if (this.value === "add_new") {
            var locationModal = new bootstrap.Modal(
                document.getElementById("mdl-crud-item-location")
            );
            locationModal.show();
            this.value = ""; // Resetear el select a vacío
            get_company_items();
        }
    });
});

//funcion para mostrar las empresas en el select al momento de cargar el modal para agregar una nueva ubicacion
function get_company_items(selectedCompanyId) {
    $.ajax({
        url: "/get_company_items/",
        type: "GET",
        success: function (response) {
            var select = $("#company");
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

// Función para agregar una nueva ubicación
function add_item_location() {
    var form = $("#form_item_location")[0];
    var formData = new FormData(form);

    $.ajax({
        url: "/add_item_location/",
        type: "POST",
        data: formData,
        contentType: false,
        processData: false,

        success: function (response) {
            // Verifica la respuesta
            if (response.success) {
                $("#form_item_location")[0].reset();
                $("#mdl-crud-item-location").modal("hide");

                // Actualiza el select de ubicaciones
                var select = $("#item_location");

                var newOption = new Option(response.new_location.name, response.new_location.id);

                select.append(newOption);

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },

        error: function (xhr, status, error) {
            console.error("Error al guardar la ubicación:", error);

            console.error("Respuesta del servidor:", xhr.responseJSON);

            var message = "Hubo un error al guardar la ubicación. Intenta nuevamente.";

            if (xhr.responseJSON && xhr.responseJSON.message) {
                message = xhr.responseJSON.message;
            }

            Swal.fire({
                title: "¡Error!",
                text: message,
                icon: "error",
            });
        },

        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $('input[name="csrfmiddlewaretoken"]').val());
        },
    });
}

//Tabla de desglose de cada activo registrado
$(document).on("click", "button[data-infrastructure-item='view-identifiers']", function () {
    const itemId = $(this).data("id");

    // Guardar el ID del activo
    $("#mdl-crud-detaill").data("item-id", itemId);

    // Cargar información
    cargarDetallesInfraestructura(itemId);

    $("#mdl-crud-detaill").modal("show");
});

//mostrar modal para asignar responsable
$(document).on("click", ".assign-responsible", function () {
    const id = $(this).data("id");
    const responsableId = $(this).data("responsable-id");

    $("#detalle_id").val(id);

    // Cambiar el título del modal
    const modalTitle = responsableId ? "Editar responsable" : "Asignar responsable";
    $("#modalAsignarResponsableLabel").text(modalTitle);

    // Cargar usuarios disponibles
    $.get("/obtener_usuarios/", function (data) {
        const select = $("#responsable").empty();
        data.forEach((u) => {
            const selected = u.id === responsableId ? "selected" : "";
            select.append(`<option value="${u.id}" ${selected}>${u.name}</option>`);
        });
    });
    $("#mdl-crud-responsable").modal("show");
});

//Asignar responsable
$("#formAsignarResponsable").submit(function (e) {
    e.preventDefault();

    const detalleId = $("#detalle_id").val();
    const responsableId = $("#responsable").val();

    $.ajax({
        url: "/asignar_responsable/",
        method: "POST",
        data: {
            id: detalleId,
            responsable: responsableId,
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
        },
        success: function (res) {
            if (res.success) {
                $("#formAsignarResponsable")[0].reset();
                $("#mdl-crud-responsable").modal("hide");

                Swal.fire({
                    title: "¡Éxito!",
                    text: res.message,
                    icon: "success",
                    timer: 1500,
                });
                // Volver a cargar la tabla de informacion
                const itemId = $("#mdl-crud-detaill").data("item-id");
                if (itemId) {
                    cargarDetallesInfraestructura(itemId);
                }
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: res.message,
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al asignar responsable:", error);
            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error inesperado. Intenta nuevamente.",
                icon: "error",
            });
        },
    });
});

// Mostrar formulario para agregar fotografia
$(document).on("click", ".assign-photo-infraestructure", function () {
    const id = $(this).data("id");
    const photo_infraestructure = $(this).data("photo-infraestructure");

    console.log("ID del detalle:", id);
    console.log("Fotografía actual:", photo_infraestructure);

    $("#detalle_photo_id").val(id);

    const modalTitle = photo_infraestructure ? "Editar Fotografía" : "Asignar Fotografía";

    $("#modalPhotoInfraestructure").text(modalTitle);

    $("#mdl-crud-photo-infraestructure").modal("show");
});

// Guardar una fotografía del activo
$(document).on("submit", "#formPhotoInfraestructure", function (e) {
    e.preventDefault();

    console.log("Entramos a guardar una fotografía");

    const form = this;
    const formData = new FormData(form);

    console.log("Detalle ID:", formData.get("detalle_id"));
    console.log("Fotografía:", formData.get("photo"));

    Swal.fire({
        title: "Guardando fotografía...",
        text: "Espera un momento.",
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/save_photo_infrastructure/",
        type: "POST",

        data: formData,

        processData: false,
        contentType: false,

        success: function (response) {
            console.log("Respuesta guardar fotografía:", response);

            if (response.success) {
                $("#mdl-crud-photo-infraestructure").modal("hide");

                form.reset();
                const itemId = $("#mdl-crud-detaill").data("item-id");

                if (itemId) {
                    cargarDetallesInfraestructura(itemId);
                }

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message,
                    icon: "error",
                });
            }
        },

        error: function (xhr, status, error) {
            console.error("Error al guardar la fotografía:", error);

            console.error("Respuesta del servidor:", xhr.responseText);

            Swal.fire({
                title: "¡Error!",
                text: "No se pudo guardar la fotografía.",
                icon: "error",
            });
        },
    });
});

//Función para cargar el desglose de cada registro
function cargarDetallesInfraestructura(itemId) {
    Swal.fire({
        title: "Cargando información...",
        text: "Espera un momento.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: function () {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/get_infrastructure_item_details/",
        method: "GET",

        data: {
            id: itemId,
        },

        success: function (response) {
            console.log("RESPUESTA GET DETALLES:", response);

            if (!response.success) {
                alert("No se pudieron obtener los detalles.");
                return;
            }

            const table = $("#item-detail-table");

            if ($.fn.DataTable.isDataTable(table)) {
                table.DataTable().destroy();
            }

            table.DataTable({
                destroy: true,
                processing: true,
                responsive: true,
                autoWidth: false,

                data: response.data,

                columns: [
                    {
                        title: "Id",
                        data: "id",
                    },

                    {
                        title: "Identificador",
                        data: "identificador",
                    },

                    {
                        title: "Fecha de asignación",
                        data: "fecha_asignacion",

                        render: function (data, type, row) {
                            return data !== ""
                                ? data
                                : `
                                    <span class="text-muted">
                                        Sin fecha
                                    </span>
                                `;
                        },
                    },

                    {
                        title: "Responsable",
                        data: null,
                        orderable: false,
                        searchable: false,
                        className: "text-center",

                        render: function (data, type, row) {
                            if (!row.is_active) {
                                if (row.tiene_responsable) {
                                    return `
                                        <span>
                                            ${row.responsable}
                                        </span>
                                    `;
                                }

                                return `
                                    <span class="text-muted">
                                        Sin responsable
                                    </span>
                                `;
                            }

                            if (row.tiene_responsable) {
                                return `
                                    <span>
                                        ${row.responsable}
                                    </span>

                                    <button
                                        class="btn btn-sm btn-warning ms-2 assign-responsible"
                                        data-id="${row.id}"
                                        data-responsable-id="${row.responsable_id}">

                                        <i class="fas fa-user-edit me-1"></i>
                                        Editar responsable

                                    </button>
                                `;
                            } else {
                                return `
                                    <button
                                        class="btn btn-sm btn-primary assign-responsible"
                                        data-id="${row.id}">

                                        <i class="fas fa-user-plus me-1"></i>
                                        Asignar responsable

                                    </button>
                                `;
                            }
                        },
                    },

                    // FOTOGRAFÍA
                    {
                        title: "Fotografía",
                        data: null,
                        orderable: false,
                        searchable: false,
                        className: "text-center",

                        render: function (data, type, row) {
                            // EQUIPO DESACTIVADO
                            if (!row.is_active) {
                                // Si tiene fotografía, solo mostrarla
                                if (row.fotografia) {
                                    return `
                                        <div class="d-flex align-items-center justify-content-center">
                                            ${row.fotografia}
                                        </div>
                                    `;
                                }

                                // Si no tiene fotografía
                                return `
                                    <span class="text-muted">
                                        Sin fotografía
                                    </span>
                                `;
                            }

                            // EQUIPO ACTIVO
                            if (row.fotografia) {
                                return `
                                    <div class="d-flex align-items-center justify-content-center gap-2">

                                        ${row.fotografia}

                                        <button
                                            type="button"
                                            class="btn btn-sm btn-warning assign-photo-infraestructure"
                                            data-id="${row.id}"
                                            title="Editar fotografía">

                                            <i class="fa-regular fa-pen-to-square"></i>

                                        </button>

                                    </div>
                                `;
                            } else {
                                return `
                                    <button
                                        type="button"
                                        class="btn btn-sm btn-info-light assign-photo-infraestructure"
                                        data-id="${row.id}"
                                        title="Asignar fotografía">

                                        <i class="fa-solid fa-file-circle-plus"></i>

                                    </button>
                                `;
                            }
                        },
                    },

                    // ACCIONES
                    {
                        title: "Acciones",
                        data: null,
                        orderable: false,
                        searchable: false,
                        className: "text-center",

                        render: function (data, type, row) {
                            if (row.is_active) {
                                // ACTIVO → DESHABILITAR
                                return `
                                    <button
                                        type="button"
                                        class="btn btn-icon btn-sm btn-danger-light toggle-infrastructure-detail"
                                        data-id="${row.id}"
                                        data-action="disable"
                                        title="Deshabilitar">

                                        <i class="fa-solid fa-ban"></i>

                                    </button>
                                `;
                            } else {
                                // DESHABILITADO
                                return `
                                    <span
                                        class="badge bg-danger-transparent text-danger"
                                        title="Activo desactivado">

                                        <i class="fa-solid fa-ban me-1"></i>
                                        Desactivado

                                    </span>
                                `;
                            }
                        },
                    },
                ],

                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },

                pageLength: 10,
            });
            Swal.close();
        },

        error: function (xhr, error, thrown) {
            console.error("Error al obtener los detalles:", error);

            alert("No se pudieron cargar los detalles de la infraestructura.");
        },
    });
}

//Abrir el modal para editar fotografia de cada activo
$(document).on("click", ".assign-photo-infraestructure", function () {
    const id = $(this).data("id");
    $("#detalle_photo_id").val(id);
    $("#modalPhotoInfraestructure").text("Editar fotografía");
    $("#individual_photo_infraestructure").val("");
    $("#mdl-crud-photo-infraestructure").modal("show");
});

// Deshabilitar un activo de infraestructura (formulario)
$(document).on("click", ".toggle-infrastructure-detail", function () {
    const id = $(this).data("id");
    const action = $(this).data("action");

    // DESHABILITAR
    if (action === "disable") {
        $.ajax({
            url: "/modal_infrastructure_detail/",
            type: "GET",

            data: {
                id: id,
            },
            success: function (response) {
                if (!response.success) {
                    Swal.fire(
                        "Error",
                        response.message || "No se pudo obtener la información.",
                        "error"
                    );
                    return;
                }

                $("#disable_detail_id").val(response.data.id);
                $("#disable_identifier").val(response.data.identifier);
                $("#disable_reason").val("");
                $("#disable_description").val("");
                $("#disable_infrastructure_image").val("");

                $("#mdl-crud-enable-infrastructure").modal("show");
            },

            error: function (xhr) {
                console.error("Error:", xhr.responseText);

                Swal.fire("Error", "No se pudo obtener la información del equipo.", "error");
            },
        });

        return;
    }
});

// Dar de baja un activo de infraestructura
$(document).on("submit", "#formdisableInfrastructure", function (e) {
    e.preventDefault();

    const form = this;
    const formData = new FormData(form);

    formData.append("action", "disable");

    const detailId = $("#disable_detail_id").val();

    Swal.fire({
        title: "Guardando información...",
        text: "Espera un momento.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        didOpen: function () {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/disable_infrastructure_detail/",

        type: "POST",

        data: formData,

        processData: false,

        contentType: false,

        success: function (response) {
            if (response.success) {
                $("#mdl-crud-enable-infrastructure").modal("hide");

                form.reset();

                $("#image_preview1").attr("src", "").hide();

                $("#image_preview2").attr("src", "").hide();

                Swal.fire({
                    title: "¡Éxito!",
                    text: response.message,
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });

                const itemId = $("#mdl-crud-detaill").data("item-id");

                if (itemId) {
                    cargarDetallesInfraestructura(itemId);
                }
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message || "No se pudo deshabilitar el activo.",
                    icon: "error",
                });
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al deshabilitar:", error);
            console.error("Respuesta servidor:", xhr.responseText);

            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error al deshabilitar el activo.",
                icon: "error",
            });
        },
    });
});

// PREVISUALIZACIÓN EVIDENCIA 1
document.getElementById("evidence1").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview1");

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = "none";
    }
});

// PREVISUALIZACIÓN EVIDENCIA 2
document.getElementById("evidence2").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview2");

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(file);
    } else {
        preview.src = "";
        preview.style.display = "none";
    }
});
