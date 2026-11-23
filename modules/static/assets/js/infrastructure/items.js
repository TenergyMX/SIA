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
                    category__name: "",
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
                    {
                        title: "ID",
                        data: "id",
                        className: "toggleable",
                    },
                    {
                        title: "Categoría",
                        data: "category__name",
                        className: "toggleable",
                    },
                    {
                        title: "Nombre",
                        data: "name",
                        className: "toggleable",
                    },
                    {
                        title: "Tipo de activo",
                        data: "item_type",
                        className: "toggleable",
                        render: function (data) {
                            if (data === "donado") return "Donado";
                            if (data === "comprado") return "Comprado";
                            return "";
                        },
                    },
                    {
                        title: "Marca",
                        data: "item_brand",
                        className: "toggleable",
                    },
                    {
                        title: "Cantidad",
                        data: "quantity",
                        className: "toggleable",
                    },
                    {
                        title: "Costo",
                        data: "cost",
                        className: "toggleable",
                        render: function (data, type, row) {
                            if (data === null || data === "") return "$0.00";

                            if (type === "display") {
                                return (
                                    "$" +
                                    Number(data).toLocaleString("es-MX", {
                                        minimumFractionDigits: 2,
                                        maximumFractionDigits: 2,
                                    })
                                );
                            }

                            return data;
                        },
                    },
                    {
                        title: "Descripción",
                        data: "description",
                        defaultContent: "",
                        className: "toggleable",
                    },
                    {
                        title: "Área",
                        data: "item_area__name",
                        defaultContent: "Sin área",
                        className: "toggleable",
                    },
                    {
                        title: "Responsable",
                        data: "responsible_name",
                        defaultContent: "Sin responsable",
                        className: "toggleable",
                    },
                    {
                        title: "Fecha de adquisición",
                        data: "start_date",
                        defaultContent: "",
                        render: function (data, type, row) {
                            if (!data) return "Sin fecha";

                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }

                            return data;
                        },
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "Comentarios",
                        data: "comments",
                        defaultContent: "",
                        className: "toggleable",
                    },
                    {
                        title: "Ficha técnica",
                        data: "technical_sheet",
                        orderable: false,
                        className: "toggleable",
                        render: function (data, type, row) {
                            if (!data) return "Sin ficha técnica";

                            return `<a href="${data}"
                                class="btn btn-sm btn-outline-primary"
                                target="_blank"
                                rel="noopener noreferrer">
                                    Ver ficha
                                </a>`;
                        },
                    },

                    {
                        title: "Factura",
                        data: function (d) {
                            if (d["invoice"]) {
                                return `
                                    <a href="${d["invoice"]}"
                                    class="btn btn-sm btn-outline-primary"
                                    target="_blank">
                                        Ver factura
                                    </a>
                                `;
                            } else {
                                return "Sin factura";
                            }
                        },
                        orderable: false,
                        className: "toggleable invoice-column",
                    },

                    {
                        title: "Fotografía",
                        data: "image",
                        orderable: false,
                        searchable: false,
                        className: "toggleable",
                        render: function (data, type, row) {
                            if (!data) return "Sin fotografía";

                            return `<a href="${data}"
                                target="_blank"
                                rel="noopener noreferrer">
                                    <img src="${data}"
                                        alt="Fotografía del activo"
                                        style="width:60px;height:50px;
                                                object-fit:cover;border-radius:5px;">
                                </a>`;
                        },
                    },
                    {
                        title: "Desglose",
                        data: "btn_identifiers",
                        orderable: false,
                        searchable: false,
                        className: "toggleable",
                        defaultContent: "",
                    },
                    {
                        title: "Acciones",
                        data: "btn_action",
                        orderable: false,
                        searchable: false,
                    },
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

            self.table.ajax.reload = function () {
                self.tbl_infraesstructure_items.ajax.reload(null, false);
            };
        }

        self.init();
        window.infrastructureItem = self;
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
                initComplete: function (settings, json) {
                    const api = this.api();

                    const invoiceColumn = api.column(".invoice-column");

                    const select = $(`
                        <select class="form-select form-select-sm mt-1">
                            <option value="">Todas</option>
                            <option value="con_factura">Con factura</option>
                            <option value="sin_factura">Sin factura</option>
                        </select>
                    `);

                    // Insertar el filtro debajo del título
                    $(invoiceColumn.header()).append(select);

                    // Evento de filtrado
                    select.on("change", function () {
                        const value = $(this).val();

                        if (value === "con_factura") {
                            invoiceColumn.search("Ver factura", true, false).draw();
                        } else if (value === "sin_factura") {
                            invoiceColumn.search("Sin factura", true, false).draw();
                        } else {
                            invoiceColumn.search("").draw();
                        }
                    });
                },
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
                    get_item_areas(null);
                    get_responsible_users_item(null);

                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                case "update-item":
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infraesstructure_items.row(fila).data();

                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar item de infraestructura");

                    get_items_locations(datos["location_id"]);
                    get_item_areas(datos["item_area_id"]);
                    get_responsible_users_item(datos["item_responsible_id"]);

                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name="${index}"]`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name="${index}"]`).val(value || null);
                        }
                    });

                    obj_modal.find('[name="type"]').val(datos["item_type"] ?? "");
                    obj_modal.find('[name="equipment_brand"]').val(datos["item_brand"] ?? "");

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

// Función para abrir el desglose
function verDesgloseInfraestructura(itemId) {
    // Guardar el ID del activo
    $("#mdl-crud-detaill").data("item-id", itemId);

    cargarDetallesInfraestructura(itemId);

    $("#mdl-crud-detaill").modal("show");
}

// Evento para abrir el desglose
$(document).on("click", "button[data-infrastructure-item='view-identifiers']", function () {
    const itemId = $(this).data("id");

    verDesgloseInfraestructura(itemId);
});

//mostrar modal para asignar responsable
$(document).on("click", ".assign-responsible", function () {
    const id = $(this).data("id");
    const responsableId = $(this).data("responsable-id");

    $("#detalle_id").val(id);

    // Cambiar el título del modal
    const modalTitle = responsableId ? "Editar responsable" : "Asignar responsable";
    $("#modalAsignarResponsableLabel").text(modalTitle);

    // Limpiar selección anterior
    $("#tipo_responsable").val("").trigger("change");

    $("#responsable").html(`
        <option value="" disabled selected>Seleccione un usuario</option>
    `);

    $("#area_responsable").html(`
        <option value="" disabled selected>Seleccione un área</option>
    `);

    $("#activo_comunitario").html(`
        <option value="" disabled selected>Seleccione un activo comunitario</option>
    `);

    $("#mdl-crud-responsable").modal("show");
});

// Detectar el tipo de asignación
$("#tipo_responsable").on("change", function () {
    const tipo = $(this).val();

    // Ocultar todos los contenedores
    $("#container_usuario, #container_area, #container_activo_comunitario").addClass("d-none");

    // Quitar required de los campos
    $("#responsable, #area_responsable").prop("required", false);

    // Limpiar valores anteriores
    $("#responsable, #area_responsable").val("");

    if (tipo === "usuario") {
        $("#container_usuario").removeClass("d-none");
        $("#responsable").prop("required", true);

        cargarUsuarios();
    } else if (tipo === "area") {
        $("#container_area").removeClass("d-none");
        $("#area_responsable").prop("required", true);

        cargarAreas();
    } else if (tipo === "activo_comunitario") {
    }
});

// Cargar usuarios
function cargarUsuarios() {
    $.get("/obtener_usuarios/", function (data) {
        const select = $("#responsable");

        select.empty().append(`
            <option value="" disabled selected>Seleccione un usuario</option>
        `);

        data.forEach(function (u) {
            select.append(`<option value="${u.id}">${u.name}</option>`);
        });
    }).fail(function () {
        console.error("Error al obtener los usuarios.");
    });
}

// Cargar áreas
function cargarAreas() {
    $.get("/get_item_areas/", function (response) {
        const select = $("#area_responsable");

        select.empty().append(`
            <option value="" disabled selected>Seleccione un área</option>
        `);

        response.data.forEach(function (area) {
            select.append(`<option value="${area.id}">${area.name}</option>`);
        });
    }).fail(function () {
        console.error("Error al obtener las areas.");
    });
}

// Asignar responsable
$("#formAsignarResponsable").submit(function (e) {
    e.preventDefault();

    const detalleId = $("#detalle_id").val();
    const tipo = $("#tipo_responsable").val();

    // Obtener el valor según el tipo de asignación
    const responsableId = tipo === "usuario" ? $("#responsable").val() : null;

    const areaId = tipo === "area" ? $("#area_responsable").val() : null;

    // Validar selección
    if (!tipo) {
        Swal.fire("Atención", "Seleccione un tipo de asignación.", "warning");
        return;
    }

    if (tipo === "usuario" && !responsableId) {
        Swal.fire("Atención", "Seleccione un usuario.", "warning");
        return;
    }

    if (tipo === "area" && !areaId) {
        Swal.fire("Atención", "Seleccione un área.", "warning");
        return;
    }

    $.ajax({
        url: "/asignar_responsable/",
        method: "POST",
        data: {
            id: detalleId,
            tipo_responsable: tipo,
            responsable: responsableId,
            area_responsable: areaId,
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
        },
        success: function (res) {
            if (res.success) {
                $("#formAsignarResponsable")[0].reset();

                // Ocultar los campos dinámicos
                $("#container_usuario, #container_area").addClass("d-none");

                $("#mdl-crud-responsable").modal("hide");

                Swal.fire({
                    title: "¡Éxito!",
                    text: res.message,
                    icon: "success",
                    timer: 1500,
                });

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
                        title: "Ubicación",
                        data: null,
                        orderable: false,
                        searchable: false,
                        className: "text-center",

                        render: function (data, type, row) {
                            if (!row.is_active) {
                                if (row.tiene_ubicacion) {
                                    return `
                                        <span>
                                            ${row.location_item}
                                        </span>
                                    `;
                                }

                                return `
                                    <span class="text-muted">
                                        Sin ubicación
                                    </span>
                                `;
                            }

                            if (row.tiene_ubicacion) {
                                return `
                                    <span>
                                        ${row.location_item}
                                    </span>

                                    <button
                                        class="btn btn-sm btn-warning edit-ubicacion"
                                        data-id="${row.id}"
                                        data-location-id="${row.location_item_id}">
                                        <i class="fa-solid fa-location-dot me-1"></i>
                                        Editar ubicación
                                    </button>
                                `;
                            } else {
                                return `

                                    <button
                                        class="btn btn-sm btn-primary assign-ubicacion"
                                        data-id="${row.id}">
                                        <i class="fa-solid fa-location-dot me-1"></i>
                                        Asignar ubicación
                                    </button>
                                `;
                            }
                        },
                    },

                    {
                        title: "Responsable",
                        data: null,
                        orderable: false,
                        searchable: false,
                        className: "text-center",

                        render: function (data, type, row) {
                            // Determinar el icono según el tipo de asignación
                            let icono = "";

                            if (row.assignment_type === "comunitario") {
                                icono = '<i class="fa-solid fa-users me-1"></i>';
                            } else if (row.assignment_type === "area") {
                                icono = '<i class="fa-solid fa-building-user me-1"></i>';
                            } else {
                                // Usuario específico
                                icono = '<i class="fas fa-user-edit me-1"></i>';
                            }

                            if (!row.is_active) {
                                return row.tiene_responsable
                                    ? `<span>${row.responsable}</span>`
                                    : `<span class="text-muted">Sin responsable</span>`;
                            }

                            if (row.tiene_responsable) {
                                return `
                                    <span>${row.responsable}</span>

                                    <button
                                        class="btn btn-sm btn-warning ms-2 assign-responsible"
                                        
                                        data-id="${row.id}"
                                        data-assignment-type="${row.assignment_type || ""}"
                                        data-responsable-id="${row.responsable_id || ""}"
                                        data-area-id="${row.area_responsable_id || ""}">

                                        ${icono}
                                        Editar responsable
                                    </button>
                                `;
                            }

                            return `
                                <button
                                    class="btn btn-sm btn-primary assign-responsible"
                                    data-id="${row.id}">

                                    <i class="fas fa-user-plus me-1"></i>
                                    Asignar responsable
                                </button>
                            `;
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
                if (window.infrastructureItem) {
                    window.infrastructureItem.tbl_infraesstructure_items.ajax.reload(null, false);
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

//Función para cargar las areas
function get_item_areas(selectedAreaId) {
    $.ajax({
        url: "/get_item_areas/",
        type: "GET",
        success: function (response) {
            var select = $("#item_area");
            select.html(null);
            select.append(
                "<option value='' disabled selected>Seleccione una de las areas existentes</option>"
            );
            $.each(response.data, function (index, value) {
                var selected = value.id == selectedAreaId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las areas existentes:", error);
            alert("Hubo un error al cargar las areas existentes.");
        },
    });
}

//Función para cargar los nombres de los usuarios
function get_responsible_users_item(selectedUserId) {
    $.ajax({
        url: "/get_responsible_users_item/",
        type: "GET",
        success: function (response) {
            var select = $("#responsible_item");
            select.html("<option value='' disabled selected>Seleccione responsable</option>");
            $.each(response.data, function (index, user) {
                var selected = user.id == selectedUserId ? "selected" : "";
                select.append(`<option value="${user.id}" ${selected}>${user.username}</option>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);
            alert("Hubo un error al cargar los usuarios.");
        },
    });
}

//Exportar excel
$(document).on("click", "#btn_download_items", function () {
    $.ajax({
        url: "/get-infrastructure-categorys/",
        type: "GET",
        dataType: "json",
        beforeSend: function () {
            Swal.fire({
                title: "Cargando categorías",
                text: "Preparando las opciones de descarga...",
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: function () {
                    Swal.showLoading();
                },
            });
        },
        success: function (response) {
            if (response.status !== "success" || !Array.isArray(response.data)) {
                Swal.fire("Error", "No fue posible obtener las categorías.", "error");
                return;
            }

            const categorias = response.data || [];
            const checks = categorias
                .map(
                    (c) =>
                        `<label class="d-flex align-items-center gap-2 text-start border rounded p-2 mb-2"><input type="checkbox" class="form-check-input m-0 download-category-check" value="${c.id}"><span>${$(
                            "<div>"
                        )
                            .text(c.name || "Sin nombre")
                            .html()}</span></label>`
                )
                .join("");
            Swal.fire({
                title: "Descargar catálogo XLSX",
                width: 500,
                html: `<div class="text-start mb-3">Selecciona que activos deseas exportar.</div>
                    <label class="form-label fw-semibold text-start d-block">Contenido del catálogo</label>
                    <select id="download_type" class="form-select mb-3">
                        <option value="all">Descargar todo el catálogo</option>
                        <option value="category">Seleccionar categorías</option>
                    </select>
                    <label class="form-label fw-semibold text-start d-block">Estado de los equipos</label>
                    <select id="download_status" class="form-select mb-3">
                        <option value="all">Todos (habilitados y deshabilitados)</option>
                        <option value="active">Solo habilitados</option>
                        <option value="inactive">Solo deshabilitados</option>
                    </select>
                    <div id="download_categories_container" class="text-start" style="display:none;">
                        <div class="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-2">
                            <span class="fw-semibold">Categorías</span>
                            <button type="button" id="select_all_download_categories" class="btn btn-sm btn-outline-primary">Seleccionar todas</button>
                        </div>
                        <div style="max-height:250px;overflow-y:auto;overflow-x:hidden;padding-right:5px;">${checks || '<p class="text-muted">No hay categorías disponibles.</p>'}</div>
                    </div>`,
                showCancelButton: true,
                confirmButtonText: "Descargar XLSX",
                cancelButtonText: "Cancelar",
                confirmButtonColor: "#198754",
                didOpen: function () {
                    const type = document.getElementById("download_type");
                    const container = document.getElementById("download_categories_container");
                    const selectAllButton = document.getElementById(
                        "select_all_download_categories"
                    );
                    type.addEventListener("change", function () {
                        container.style.display = this.value === "category" ? "block" : "none";
                    });
                    selectAllButton.addEventListener("click", function () {
                        const categoryChecks = [
                            ...document.querySelectorAll(".download-category-check"),
                        ];
                        const selectAll = categoryChecks.some((check) => !check.checked);
                        categoryChecks.forEach((check) => (check.checked = selectAll));
                        this.textContent = selectAll ? "Deseleccionar todas" : "Seleccionar todas";
                    });
                },
                preConfirm: function () {
                    const type = document.getElementById("download_type").value;
                    const status = document.getElementById("download_status").value;
                    const categoryIds = [
                        ...document.querySelectorAll(".download-category-check:checked"),
                    ].map((check) => check.value);
                    if (type === "category" && !categoryIds.length) {
                        Swal.showValidationMessage("Selecciona al menos una categoría.");
                        return false;
                    }
                    return { type: type, status: status, category_ids: categoryIds };
                },
            }).then(function (result) {
                if (!result.isConfirmed) return;
                Swal.fire({
                    title: "Generando reporte",
                    text: "Preparando los registros y sus identificadores...",
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    showConfirmButton: false,
                    didOpen: function () {
                        Swal.showLoading();
                    },
                });
                $.ajax({
                    url: "/download_items_xlsx/",
                    type: "GET",
                    data: result.value,
                    traditional: true,
                    xhrFields: { responseType: "blob" },
                    success: function (data, textStatus, xhr) {
                        const contentType = xhr.getResponseHeader("Content-Type") || "";
                        if (contentType.includes("application/json")) {
                            const reader = new FileReader();
                            reader.onload = function () {
                                try {
                                    const error = JSON.parse(reader.result);
                                    Swal.fire(
                                        "Error",
                                        error.message || "No fue posible generar el reporte.",
                                        "error"
                                    );
                                } catch (e) {
                                    Swal.fire(
                                        "Error",
                                        "La respuesta del servidor no es válida.",
                                        "error"
                                    );
                                }
                            };
                            reader.readAsText(data);
                            return;
                        }
                        const blob = new Blob([data], {
                            type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        });
                        const downloadUrl = URL.createObjectURL(blob);
                        const link = document.createElement("a");
                        link.href = downloadUrl;
                        link.download = "reporte_infraestructura.xlsx";
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000);
                        Swal.fire({
                            icon: "success",
                            title: "Reporte generado",
                            text: "La descarga del archivo XLSX ha comenzado.",
                            confirmButtonColor: "#198754",
                            timer: 2200,
                            timerProgressBar: true,
                        });
                    },
                    error: function (xhr) {
                        if (xhr.response instanceof Blob) {
                            const reader = new FileReader();
                            reader.onload = function () {
                                try {
                                    const error = JSON.parse(reader.result);
                                    Swal.fire(
                                        "Error",
                                        error.message || "No fue posible generar el reporte.",
                                        "error"
                                    );
                                } catch (e) {
                                    Swal.fire(
                                        "Error",
                                        "No fue posible generar el archivo XLSX.",
                                        "error"
                                    );
                                }
                            };
                            reader.readAsText(xhr.response);
                        } else {
                            Swal.fire(
                                "Error",
                                "No fue posible generar el archivo XLSX. Intenta nuevamente.",
                                "error"
                            );
                        }
                    },
                });
            });
        },
        error: function () {
            Swal.fire(
                "Error",
                "No fue posible cargar las categorías. Intenta nuevamente.",
                "error"
            );
        },
    });
});

// Función reutilizable para asignar o editar ubicación
function abrirModalAsignarUbicacion(id, locationId = "") {
    $("#detalle_id").val(id);
    const modalTitle = locationId ? "Editar ubicación" : "Asignar ubicación";
    $("#modalAsignarUbicacion").text(modalTitle);
    get_locations(locationId);
    $("#mdl-crud-location").modal("show");
}

// Evento único para abrir el modal
$(document).on("click", ".assign-ubicacion, .edit-ubicacion", function () {
    const id = $(this).data("id");
    const locationId = $(this).data("location-id") || "";
    const origen = $(this).data("origen") || "infraestructura";

    abrirModalAsignarUbicacion(id, locationId, origen);
});

//funcion para mostrar las opciones en el select al momento de cargar el modal para agregar una nueva ubicacion
function get_locations(selectedLocationId) {
    $.ajax({
        url: "/get_items_locations/",
        type: "GET",
        success: function (response) {
            const select = $("#location");
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
            select.append(
                '<option value="add_new_location">Agregar otra ubicación no existente</option>'
            );
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las ubicaciones:", error);
            alert("Hubo un error al cargar las ubicaciones. Inténtelo de nuevo más tarde.");
        },
    });
}

//funcion para mostrar formulario de nueva ubicación
function mostrarModalNuevaUbicacion() {
    const newLocationModal = document.getElementById("mdl-crud-item-location");

    const modal = new bootstrap.Modal(newLocationModal, {
        backdrop: "static",
        keyboard: false,
    });
    modal.show();
}

// Evento para detectar cuando se selecciona agregar ubicación
$(document).on("change", "#location", function () {
    if (this.value === "add_new_location") {
        mostrarModalNuevaUbicacion();

        this.value = "";
    }
});

// Colocar el modal de nueva ubicación por encima del modal principal
$(document).on("show.bs.modal", "#mdl-crud-item-location", function () {
    const modal = $(this);

    setTimeout(function () {
        modal.css("z-index", 1060);

        $(".modal-backdrop").last().css("z-index", 1055);
    }, 0);
});

// Restaurar el orden cuando se cierre el modal secundario
$(document).on("hidden.bs.modal", "#mdl-crud-item-location", function () {
    $("#mdl-crud-location").css("z-index", "");
});

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
                var select = $("#location");

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

// Asignar ubicación
$(document).on("submit", "#formAsignarUbicacion", function (e) {
    e.preventDefault();

    const detalleId = $("#detalle_id").val();
    const locationId = $("#location").val();

    Swal.fire({
        title: "Guardando información...",
        text: "Espera un momento.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: function () {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/asignar_location/",
        method: "POST",
        data: {
            id: detalleId,
            location: locationId,
            csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
        },

        success: function (res) {
            if (res.success) {
                $("#formAsignarUbicacion")[0].reset();

                //const verification = $("#mdl-crud-location").data("verification");
                const verification = $("#mdl-crud-location").data("origen") === "verificacion";
                const itemId = $("#mdl-crud-detaill").data("item-id");

                $("#mdl-crud-location").one("hidden.bs.modal", function () {
                    Swal.fire({
                        title: "¡Éxito!",
                        text: res.message,
                        icon: "success",
                        timer: 2500,
                        showConfirmButton: false,
                    });

                    if (verification) {
                        if (
                            window.infrastructureVerification &&
                            window.infrastructureVerification.tbl_infraesstructure_items
                        ) {
                            window.infrastructureVerification.tbl_infraesstructure_items.ajax.reload(
                                null,
                                false
                            );
                        }
                    } else if (itemId) {
                        setTimeout(function () {
                            cargarDetallesInfraestructura(itemId);
                        }, 2500);
                    }

                    //$("#mdl-crud-location").removeData("verification");
                    $("#mdl-crud-location").removeData("origen");
                });

                $("#mdl-crud-location").modal("hide");
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: res.message,
                    icon: "error",
                });
            }
        },

        error: function (xhr, status, error) {
            console.error("Error al asignar ubicación:", error);

            Swal.fire({
                title: "¡Error!",
                text: "Hubo un error inesperado. Intenta nuevamente.",
                icon: "error",
            });
        },
    });
});
