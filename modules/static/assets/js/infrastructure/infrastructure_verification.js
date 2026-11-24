class Infraestructure_Verification {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            infoCard: {
                id: null,
                ajax: {
                    url: function () {
                        return "/get-infrastructure-audit/";
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
                id: "#tbl_infraestructure_audit",
                ajax: {
                    url: "/get-infrastructure-audit/",
                    dataSrc: "data",
                    data: {},
                },

                columns: [
                    {
                        title: "ID",
                        data: "id",
                        className: "toggleable text-center",
                    },
                    {
                        title: "Nombre de la auditoría",
                        data: "name",
                        className: "toggleable",
                    },
                    {
                        title: "Descripción",
                        data: "description",
                        defaultContent: "",
                        className: "toggleable",
                    },
                    {
                        title: "Fecha de inicio",
                        data: "start_date",
                        className: "toggleable text-center",
                    },
                    {
                        title: "Fecha fin",
                        data: "end_date",
                        className: "toggleable text-center",
                    },
                    {
                        title: "Creada por",
                        data: "responsible_name",
                        defaultContent: "Sin información",
                        className: "toggleable",
                    },
                    {
                        title: "Categorías a evaluar",
                        data: "categories",
                        defaultContent: "Sin categorías",
                        className: "toggleable",
                    },
                    {
                        title: "Cantidad de activos",
                        data: "total_assets",
                        className: "toggleable text-center",
                        render: function (data) {
                            return `<span class="badge bg-primary">${data || 0}</span>`;
                        },
                    },
                    {
                        title: "Avance",
                        data: "progress",
                        className: "toggleable text-center",
                        orderable: false,
                        render: function (data, type, row) {
                            const progress = Math.min(100, Math.max(0, Number(data) || 0));

                            const total = Number(row.total_audit_items) || 0;
                            const verified = Number(row.verified_items) || 0;

                            let progressClass = "bg-danger";

                            if (progress >= 100) {
                                progressClass = "bg-success";
                            } else if (progress >= 50) {
                                progressClass = "bg-info";
                            } else if (progress > 0) {
                                progressClass = "bg-warning";
                            }

                            return `
                                <div style="min-width: 120px;">
                                    <div class="d-flex justify-content-between mb-1">
                                        <small>${verified} de ${total} activos</small>
                                        <small class="fw-semibold">${progress}%</small>
                                    </div>

                                    <div class="progress progress-sm">
                                        <div class="progress-bar ${progressClass}"
                                            role="progressbar"
                                            style="width: ${progress}%"
                                            aria-valuenow="${progress}"
                                            aria-valuemin="0"
                                            aria-valuemax="100">
                                        </div>
                                    </div>
                                </div>
                            `;
                        },
                    },
                    {
                        title: "Estado",
                        data: "status",
                        className: "toggleable text-center",
                        render: function (data, type, row) {
                            let badgeClass = "bg-secondary";

                            switch (data) {
                                case "BORRADOR":
                                    badgeClass = "bg-light text-dark";
                                    break;

                                case "EN_PROCESO":
                                    badgeClass = "bg-primary";
                                    break;

                                case "CERRADA":
                                    badgeClass = "bg-success";
                                    break;

                                case "CANCELADA":
                                    badgeClass = "bg-danger";
                                    break;
                            }

                            const statusNames = {
                                BORRADOR: "Borrador",
                                EN_PROCESO: "En proceso",
                                CERRADA: "Cerrada",
                                CANCELADA: "Cancelada",
                            };

                            return `
                                <span class="badge ${badgeClass}">
                                    ${statusNames[data] || data || "Sin estado"}
                                </span>
                            `;
                        },
                    },
                    {
                        title: "Auditar",
                        data: null,
                        orderable: false,
                        searchable: false,
                        className: "text-center",
                        render: function (data, type, row) {
                            // Si la auditoría ya finalizó, mostrar botón de reporte
                            if (row.status === "CERRADA") {
                                return `
                                    <button type="button"
                                        class="btn btn-sm btn-success"
                                        data-infrastructure-audit="generate-report"
                                        data-id="${row.id}"
                                        title="Generar reporte general">
                                        <i class="fa-solid fa-file-pdf me-1"></i>
                                        Generar reporte
                                    </button>
                                `;
                            }

                            // Si está en proceso o en borrador, permitir auditar
                            if (row.status === "BORRADOR" || row.status === "EN_PROCESO") {
                                return `
                                    <button type="button"
                                        class="btn btn-sm btn-primary"
                                        data-infrastructure-audit="start-audit"
                                        data-id="${row.id}"
                                        title="Iniciar o continuar auditoría">
                                        <i class="fa-solid fa-clipboard-check"></i>
                                        Auditar
                                    </button>
                                `;
                            }

                            return `
                                <span class="badge bg-secondary">No disponible</span>
                            `;
                        },
                    },
                    {
                        title: "Acciones",
                        data: "btn_action",
                        orderable: false,
                        searchable: false,
                        className: "text-center",
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
                    url: "/get-infrastructure-audit/",
                    data: self.list.data,
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
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
                self.tbl_infraestructure_audit.ajax.reload(null, false);
            };
        }

        self.init();
        window.infrastructureVerification = self;
    }

    init() {
        const self = this;
        if (self.list) {
            self.list.ajax.reload();
        }
        if (self.table) {
            self.tbl_infraestructure_audit = $(self.table.id).DataTable({
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
                },
            });
            delete self.table;
        }
        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-infrastructure-audit");

        $(document).on("click", "[data-infrastructure-audit]", function (e) {
            var obj = $(this);
            var option = obj.data("infrastructure-audit");

            switch (option) {
                case "refresh-table":
                    self.tbl_infraestructure_audit.ajax.reload(null, false);
                    break;
                case "add-audit":
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-title").text("Registrar auditoría de infraestructura");
                    obj_modal.find("[type='submit']").hide();

                    obj_modal.find("[name='add']").show();
                    get_categories_audit();
                    get_responsible_users_audit();
                    obj_modal.modal("show");

                    break;
                case "update-audit":
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_infraestructure_audit.row(fila).data();

                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find(".modal-header").html("Actualizar auditoria de infraestructura");

                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name="${index}"]`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name="${index}"]`).val(value || null);
                        }
                    });

                    obj_modal.find('[name="type"]').val(datos["item_type"] ?? "");

                    obj_modal
                        .find("[name='is_active']")
                        .val(datos["is_active"] == true ? "1" : "0");

                    // Cargar usuarios y seleccionar el responsable guardado
                    get_responsible_users_audit(function () {
                        $("#responsible_audit")
                            .val(
                                datos.responsible_audit != null
                                    ? String(datos.responsible_audit)
                                    : ""
                            )
                            .trigger("change");
                    });

                    // Cargar cartegorías
                    get_categories_audit(datos.categories_ids || []);

                    obj_modal.find('[name="start_date"]').val(datos.start_date || "");

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

                case "start-audit":
                    break;

                case "back-audit":
                    hideShow("#v-deliverie-pane .info-details", "#v-deliverie-pane .info");

                    break;
                case "add-session": {
                    const auditId = window.currentInfrastructureAuditId;

                    console.log("ID de auditoría para crear sesión:", auditId);

                    if (!auditId) {
                        Swal.fire("Atención", "No se identificó la auditoría.", "warning");
                        break;
                    }

                    $("#form-create-audit-session")[0].reset();
                    $("#session_audit_id").val(auditId);
                    $("#mdl-create-audit-session").modal("show");
                    get_responsible_users_audit_sesion();
                    break;
                }

                case "open-session": {
                    const sessionId = obj.data("id");

                    if (!sessionId) {
                        Swal.fire("Atención", "No se encontró el ID de la sesión.", "warning");
                        break;
                    }

                    // Guardar el ID de la sesión seleccionada
                    window.currentInfrastructureSessionId = sessionId;

                    // Ocultar tabla de sesiones
                    $("#audit-sessions-table_wrapper").hide();

                    // Mostrar tabla de activos
                    $("#audit-assets-container").show();

                    // Cambiar título
                    $("#audit-assets-container .card-title").text(
                        "Activos de la sesión de auditoría"
                    );

                    // Cargar información de los activos
                    initAuditInfrastructureTable(sessionId);

                    break;
                }

                case "back-sessions": {
                    $("#audit-assets-container").hide();
                    $("#audit-sessions-table_wrapper").show();
                    window.currentInfrastructureSessionId = null;
                    loadInfrastructureAuditSessions(window.currentInfrastructureAuditId);

                    break;
                }

                case "save-detail": {
                    saveAuditSessionDetail(obj);
                    break;
                }

                case "finish-audit":
                    finishInfrastructureAudit();
                    break;

                case "generate-report": {
                    const auditId = obj.data("id");

                    if (!auditId) {
                        Swal.fire("Atención", "No se encontró el ID de la auditoría.", "warning");
                        break;
                    }

                    window.open(`/generate-infrastructure-audit-report/${auditId}/`, "_blank");

                    break;
                }

                default:
                    console.log("Opción dezconocida: " + option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "-infrastructure-audit/";
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
                    self.tbl_infraestructure_audit.ajax.reload();
                    message = response.message || "Se han guardado los datos con éxito";
                    Swal.fire("Éxito", message, "success");
                    $("#audit_categories").val([]).trigger("change");

                    $("#audit_assets_body").html(`
                        <tr>
                            <td colspan="4" class="text-center text-muted">
                                Seleccione una o varias categorías para cargar los activos.
                            </td>
                        </tr>
                    `);

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

//función para cargar las categorias
function get_categories_audit(selectedCategories = [], callback = null) {
    $.ajax({
        url: "/get_categories_audit/",
        type: "GET",
        success: function (response) {
            var select = $("#audit_categories");
            select.html(null);

            select.append(`
                <option value="" disabled>
                    Seleccione las categorías a auditar
                </option>
            `);

            selectedCategories = selectedCategories.map(String);

            $.each(response.data, function (index, value) {
                var selected = selectedCategories.includes(String(value.id)) ? "selected" : "";

                select.append(`
                    <option value="${value.id}" ${selected}>
                        ${value.name}
                    </option>
                `);
            });

            // Actualizar Select2 y disparar el evento change
            select.trigger("change");

            if (typeof callback === "function") {
                callback();
            }
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las areas existentes:", error);
            alert("Hubo un error al cargar las areas existentes.");
        },
    });
}

//Función para cargar los nombres de los usuarios
function get_responsible_users_audit() {
    $.ajax({
        url: "/get_responsible_users_item/",
        type: "GET",

        success: function (response) {
            var select = $("#responsible_audit");

            select.empty();

            select.append(`
                <option value="" disabled>Seleccione el responsable</option>
            `);

            $.each(response.data, function (index, user) {
                var selected = user.is_current_user ? "selected" : "";

                select.append(`
                    <option value="${user.id}" ${selected}>
                        ${user.username}
                    </option>
                `);
            });

            select.trigger("change");

            if (typeof callback === "function") {
                callback();
            }
        },

        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);
        },
    });
}

// Cargar activos de las categorias seleccionadas para la auditoría
function get_infrastructure_audit_assets() {
    const selectedCategories = $("#audit_categories").val();

    const tbody = $("#audit_assets_body");

    // Validar que existan áreas seleccionadas
    if (!selectedCategories || selectedCategories.length === 0) {
        tbody.html(`
            <tr>
                <td colspan="4" class="text-center text-muted">
                    Seleccione una o varias categorías para cargar los activos.
                </td>
            </tr>
        `);
        return;
    }

    $.ajax({
        url: "/get_infrastructure_audit_assets/",
        type: "GET",
        data: {
            categories: selectedCategories,
        },
        traditional: true,

        beforeSend: function () {
            tbody.html(`
                <tr>
                    <td colspan="4" class="text-center">
                        <i class="fa-solid fa-spinner fa-spin me-1"></i>
                        Cargando activos...
                    </td>
                </tr>
            `);
        },

        success: function (response) {
            tbody.empty();

            if (response.status !== "success" || response.data.length === 0) {
                tbody.html(`
                    <tr>
                        <td colspan="4" class="text-center text-muted">
                            No se encontraron activos en las categorías seleccionadas.
                        </td>
                    </tr>
                `);

                return;
            }

            $.each(response.data, function (index, asset) {
                tbody.append(`
                    <tr data-asset-id="${asset.id}">
                        <td>${asset.id}</td>
                        <td>${asset.name}</td>
                        <td>${asset.category}</td>
                        <td class="text-center">${asset.quantity}</td>
                    </tr>
                `);
            });
        },

        error: function (xhr, status, error) {
            console.error("Error al cargar los activos:", error);

            tbody.html(`
                <tr>
                    <td colspan="4" class="text-center text-danger">
                        Error al cargar los activos.
                    </td>
                </tr>
            `);
        },
    });
}

// Detectar cambios en las áreas seleccionadas
$(document).on("change", "#audit_categories", function () {
    get_infrastructure_audit_assets();
});

//Llamar a la función para iniciar la auditoria
$(document).on("click", '[data-infrastructure-audit="start-audit"]', function (e) {
    e.preventDefault();

    const auditId = $(this).data("id");

    openInfrastructureAudit(auditId);
});

//Función para iniciar una auditoria
function openInfrastructureAudit(auditId) {
    if (!auditId) {
        Swal.fire("Atención", "No se identificó la auditoría.", "warning");
        return;
    }

    window.currentInfrastructureAuditId = auditId;

    console.log("ID de auditoría seleccionada:", window.currentInfrastructureAuditId);

    $.ajax({
        type: "GET",
        url: `/ajax/infra-info-by-audit/${auditId}/`,

        success: function (response) {
            console.log("Respuesta del servidor:", response);

            if (response.info_html) {
                $(".info-details .col-md-4").html(response.info_html);

                console.log("Tarjeta insertada correctamente");

                hideShow("#v-deliverie-pane .info", "#v-deliverie-pane .info-details");

                $("#audit-assets-container").hide();

                // Mostrar sesiones de la auditoría
                loadInfrastructureAuditSessions(auditId);
            } else {
                Swal.fire("Error", "No se pudo cargar la información de la auditoría.", "error");
            }
        },

        error: function (xhr) {
            console.error(xhr.responseText);

            Swal.fire("Error", "No se pudo cargar la auditoría.", "error");
        },
    });
}

// Calcular diferencia entre cantidad registrada y encontrada
$(document).on(
    "input",
    "#audit-infrastructure-items-table .input-cantidad-encontrada",
    function () {
        const input = $(this);

        const fila = input.closest("tr");

        const diferenciaElement = fila.find(".cantidad-diferencia");

        const cantidadRegistrada = Number(diferenciaElement.data("cantidad-registrada")) || 0;

        const valorEncontrado = input.val();

        if (valorEncontrado === "") {
            diferenciaElement
                .text("-")
                .removeClass("bg-danger-transparent bg-success-transparent bg-warning-transparent")
                .addClass("bg-secondary-transparent");

            return;
        }

        const cantidadEncontrada = Number(valorEncontrado);

        const diferencia = cantidadRegistrada - cantidadEncontrada;

        diferenciaElement.text(diferencia);

        diferenciaElement.removeClass(
            "bg-secondary-transparent bg-danger-transparent bg-success-transparent bg-warning-transparent"
        );

        if (diferencia > 0) {
            diferenciaElement.addClass("bg-danger-transparent");
        } else if (diferencia < 0) {
            diferenciaElement.addClass("bg-warning-transparent");
        } else {
            diferenciaElement.addClass("bg-success-transparent");
        }
    }
);

// Tabla para Consultar sesiones de una auditoría
function loadInfrastructureAuditSessions(auditId) {
    const tableSelector = "#audit-sessions-table";

    if ($.fn.DataTable.isDataTable(tableSelector)) {
        $(tableSelector).DataTable().destroy();
    }

    window.auditSessionsTable = $(tableSelector).DataTable({
        processing: true,
        serverSide: false,
        responsive: true,
        autoWidth: false,

        ajax: {
            url: "/get-infrastructure-audit-sessions/",
            type: "GET",
            data: {
                audit_id: auditId,
            },
            dataSrc: "data",
        },

        columns: [
            { data: "id" },
            { data: "name" },
            { data: "responsible" },
            { data: "created_at" },
            {
                data: "status",
                render: function (data) {
                    return `<span class="badge bg-warning-transparent">${data}</span>`;
                },
            },
            {
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    return `
                        <button type="button"
                                class="btn btn-sm btn-primary"
                                data-infrastructure-audit="open-session"
                                data-id="${row.id}">
                            <i class="fa-solid fa-eye"></i>
                            Abrir
                        </button>
                    `;
                },
            },
        ],
    });
}

//crear una sesion de auditoria
$("#form-create-audit-session").on("submit", function (e) {
    e.preventDefault();
    const form = this;
    const datos = new FormData(form);

    $.ajax({
        type: "POST",
        url: "/add-infrastructure-audit-session/",
        data: datos,
        processData: false,
        contentType: false,

        success: function (response) {
            if (!response.success) {
                Swal.fire("Atención", response.message, "warning");
                return;
            }

            $("#mdl-create-audit-session").modal("hide");

            form.reset();

            loadInfrastructureAuditSessions(window.currentInfrastructureAuditId);

            Swal.fire("Éxito", response.message, "success");
        },

        error: function (xhr) {
            const message = xhr.responseJSON?.message || "No fue posible crear la sesión.";

            Swal.fire("Error", message, "error");
        },
    });
});

// Cargar usuarios responsables de las sesiones
function get_responsible_users_audit_sesion(callback = null) {
    $.ajax({
        url: "/get_responsible_users_item/",
        type: "GET",

        success: function (response) {
            var select = $("#responsible_id");

            select.empty();

            select.append(`
                <option value="">Seleccione el responsable</option>
            `);

            $.each(response.data, function (index, user) {
                var selected = user.is_current_user ? "selected" : "";

                select.append(`
                    <option value="${user.id}" ${selected}>
                        ${user.username}
                    </option>
                `);
            });

            select.trigger("change");

            if (typeof callback === "function") {
                callback();
            }
        },

        error: function (xhr, status, error) {
            console.error("Error al cargar los usuarios:", error);

            Swal.fire("Error", "No fue posible cargar los usuarios responsables.", "error");
        },
    });
}

//Tabla para obnerter activos de la sesion
function initAuditInfrastructureTable(sessionId) {
    const tableSelector = "#audit-infrastructure-items-table";

    if ($.fn.DataTable.isDataTable(tableSelector)) {
        $(tableSelector).DataTable().destroy();
        $(tableSelector).empty();
    }

    window.auditInfrastructureTable = $(tableSelector).DataTable({
        processing: true,
        serverSide: false,
        responsive: true,
        autoWidth: false,

        ajax: {
            url: "/get-infrastructure-audit-session-items/",
            type: "GET",
            data: {
                session_id: sessionId,
            },
            dataSrc: "data",
        },

        columns: [
            {
                title: "ID",
                data: "item_id",
            },
            {
                title: "Categoría",
                data: "category",
            },
            {
                title: "Nombre",
                data: "name",
            },
            {
                title: "Fotografía",
                data: "image",
                orderable: false,
                searchable: false,
                render: function (data) {
                    if (!data) return "Sin fotografía";

                    return `
                        <a href="${data}" target="_blank"
                           rel="noopener noreferrer">
                            <img src="${data}"
                                alt="Fotografía del activo"
                                style="width:60px;height:50px;
                                object-fit:cover;border-radius:5px;">
                        </a>`;
                },
            },
            {
                title: "Descripción",
                data: "description",
                defaultContent: "",
            },
            {
                title: "Marca",
                data: "item_brand",
                defaultContent: "",
            },
            {
                title: "Costo",
                data: "cost",
                render: function (data, type) {
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
                title: "Desglose",
                data: "btn_identifiers",
                orderable: false,
                searchable: false,
                defaultContent: "",
            },
            {
                title: "Cantidad Registrada",
                data: "registered_quantity",
            },
            {
                title: "Cantidad Encontrada",
                data: "found_quantity",
                render: function (data, type, row) {
                    return `
                        <input
                            type="number"
                            class="form-control form-control-sm input-cantidad-encontrada"
                            data-id="${row.id}"
                            min="0"
                            step="1"
                            value="${data !== null ? data : ""}"
                            ${row.is_completed ? "disabled" : ""}
                        >
                    `;
                },
            },
            {
                title: "Cantidad Diferencia",
                data: null,
                orderable: false,
                searchable: false,
                className: "text-center",
                render: function (data, type, row) {
                    const encontrada = row.found_quantity;

                    const diferencia =
                        encontrada !== null && encontrada !== undefined
                            ? Number(row.registered_quantity) - Number(encontrada)
                            : null;

                    let color = "bg-secondary-transparent";

                    if (diferencia !== null) {
                        if (diferencia > 0) {
                            color = "bg-danger-transparent";
                        } else if (diferencia < 0) {
                            color = "bg-warning-transparent";
                        } else {
                            color = "bg-success-transparent";
                        }
                    }

                    return `
                        <span class="badge ${color} cantidad-diferencia"
                            data-id="${row.id}"
                            data-cantidad-registrada="${row.registered_quantity}">
                            ${diferencia !== null ? diferencia : "-"}
                        </span>
                    `;
                },
            },
            {
                title: "Estado",
                data: null,
                orderable: false,
                searchable: false,
                className: "text-center",
                render: function (data, type, row) {
                    const completado = row.found_quantity !== null;

                    return `
                        <span class="badge ${completado ? "bg-success-transparent" : "bg-warning-transparent"} estado-verificacion"
                            data-id="${row.id}">
                            ${completado ? "Verificado" : "Pendiente"}
                        </span>
                    `;
                },
            },
            {
                title: "Observaciones",
                data: "observations",
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    return `
                        <textarea
                            class="form-control form-control-sm input-observaciones"
                            data-audit-item-id="${row.id}"
                            rows="2"
                            ${row.is_completed ? "disabled" : ""}
                        >${data || ""}</textarea>
                    `;
                },
            },
            {
                title: "Evidencia",
                data: "evidence",
                orderable: false,
                searchable: false,
                render: function (data, type, row) {
                    if (data) {
                        return `
                            <a href="${data}"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="btn btn-sm btn-info-light">
                                <i class="fa-solid fa-eye me-1"></i>
                                Ver evidencia
                            </a>
                        `;
                    }

                    if (row.is_completed) {
                        return "Sin evidencia";
                    }

                    return `
                        <input
                            type="file"
                            class="form-control form-control-sm input-evidencia"
                            data-audit-item-id="${row.id}"
                            accept="image/*,.pdf"
                        >
                    `;
                },
            },
            {
                title: "Acciones",
                data: null,
                orderable: false,
                searchable: false,
                className: "text-center",
                render: function (data, type, row) {
                    if (row.is_completed) {
                        return `
                            <span class="badge bg-success">
                                <i class="fa-solid fa-check me-1"></i>
                                Verificado
                            </span>
                        `;
                    }

                    return `
                        <button
                            type="button"
                            class="btn btn-success btn-sm"
                            data-infrastructure-audit="save-detail"
                            data-id="${row.id}">
                            <i class="fa-solid fa-floppy-disk me-1"></i>
                            Guardar
                        </button>
                    `;
                },
            },
        ],
    });
}

//Guardar un registro de activo dentro de una sesion
function saveAuditSessionDetail(obj) {
    const auditItemId = obj.data("id");
    const sessionId = window.currentInfrastructureSessionId;

    if (!auditItemId || !sessionId) {
        Swal.fire("Atención", "No se identificó el activo o la sesión de auditoría.", "warning");
        return;
    }

    const cantidadInput = $(`.input-cantidad-encontrada[data-id="${auditItemId}"]`);

    const observacionesInput = $(`.input-observaciones[data-audit-item-id="${auditItemId}"]`);

    const evidenciaInput = $(`.input-evidencia[data-audit-item-id="${auditItemId}"]`);

    const cantidad = cantidadInput.val();

    if (cantidad === "" || cantidad === null || cantidad === undefined) {
        Swal.fire("Atención", "Debes ingresar la cantidad encontrada.", "warning");
        cantidadInput.focus();
        return;
    }

    const formData = new FormData();

    formData.append("session_id", sessionId);
    formData.append("audit_item_id", auditItemId);
    formData.append("found_quantity", cantidad);
    formData.append("observations", observacionesInput.val() || "");

    const evidencia = evidenciaInput[0]?.files[0];

    if (evidencia) {
        formData.append("evidence", evidencia);
    }

    const buttonHtml = obj.html();

    $.ajax({
        url: "/save-infrastructure-audit-session-detail/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,

        beforeSend: function () {
            obj.prop("disabled", true);
            obj.html(`
                <i class="fa-solid fa-spinner fa-spin me-1"></i>
                Guardando...
            `);
        },

        success: function (response) {
            if (response.success) {
                Swal.fire("Correcto", response.message, "success");

                window.auditInfrastructureTable.ajax.reload(null, false);
            } else {
                Swal.fire(
                    "Error",
                    response.message || "No fue posible guardar la información.",
                    "error"
                );
            }
        },

        error: function (xhr) {
            console.error("Error al guardar el detalle:", xhr.responseText);

            const message =
                xhr.responseJSON?.message ||
                "Ocurrió un error al guardar el detalle de la auditoría.";

            Swal.fire("Error", message, "error");
        },

        complete: function () {
            obj.prop("disabled", false);
            obj.html(buttonHtml);
        },
    });
}

//Finalizar auditoria
function finishInfrastructureAudit() {
    const auditId = window.currentInfrastructureAuditId;

    if (!auditId) {
        Swal.fire("Atención", "No se identificó la auditoría.", "warning");
        return;
    }

    Swal.fire({
        title: "¿Finalizar auditoría?",
        text: "Se finalizarán todas las sesiones. Esta acción no permitirá continuar verificando activos.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, finalizar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#198754",
    }).then((result) => {
        if (!result.isConfirmed) return;

        $.ajax({
            url: "/finish-infrastructure-audit/",
            type: "POST",
            data: {
                audit_id: auditId,
            },

            beforeSend: function () {
                Swal.fire({
                    title: "Finalizando auditoría...",
                    text: "Espera un momento.",
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    },
                });
            },

            success: function (response) {
                if (response.success) {
                    Swal.fire("Auditoría finalizada", response.message, "success").then(() => {
                        // Regresar al listado de auditorías
                        window.location.reload();
                    });
                } else {
                    Swal.fire("Atención", response.message, "warning");
                }
            },

            error: function (xhr) {
                const response = xhr.responseJSON || {};

                let message = response.message || "No fue posible finalizar la auditoría.";

                if (response.pending_items?.length) {
                    message += "\n\nActivos pendientes:\n" + response.pending_items.join(", ");
                }

                Swal.fire("No se puede finalizar", message, "warning");
            },
        });
    });
}
