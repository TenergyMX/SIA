class ComputerPeripheral {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {
                computerSystem_id: null,
            },
            infoCard: {
                id: null,
                ajax: {
                    url: function () {
                        return "/get_computer_equipment/";
                    },
                    data: function () {},
                    reload: function () {},
                },
            },
            table: {
                id: "#peripherals_table",
                ajax: {
                    url: "/get_computer_peripherals/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Identificador", data: "identifier", className: "toggleable" },
                    { title: "Nombre", data: "name", className: "toggleable" },
                    { title: "Tipo.", data: "peripheral_type", className: "toggleable" },
                    { title: "Marca", data: "brand", className: "toggleable" },
                    { title: "Modelo", data: "model", className: "toggleable" },
                    { title: "N. Serie", data: "serial_number", className: "toggleable" },
                    {
                        title: "Descripción",
                        data: "description",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Fecha de Adquisición",
                        data: "acquisition_date",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Ubicación",
                        data: "location",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Responsable",
                        data: function (d) {
                            const firstName = d["responsible__first_name"]
                                ? d["responsible__first_name"]
                                : "";
                            const lastName = d["responsible__last_name"]
                                ? ` ${d["responsible__last_name"]}`
                                : "";
                            return `${firstName}${lastName}`;
                        },
                        className: "toggleable",
                    },
                    { title: "Estado", data: "peripheral_status", className: "toggleable" },
                    {
                        title: "Comentarios",
                        data: "comments",
                        visible: false,
                        className: "toggleable",
                    },
                    {
                        title: "Ver factura",
                        data: "btn_view_factura",
                        orderable: false,
                        className: "text-center",
                    },

                    {
                        title: "Imagen",
                        data: "image_peripheral",
                        orderable: false,
                        searchable: false,
                        className: "text-center",
                        render: function (data, type, row) {
                            if (type !== "display") {
                                return data || "";
                            }

                            if (!data) {
                                return `
                                    <div class="equipment-no-image">
                                        <i class="fa-solid fa-image"></i>
                                        <span>Sin fotografía</span>
                                    </div>
                                `;
                            }

                            const img = document.createElement("img");

                            img.src = data;
                            img.alt = `Fotografía de ${row.name || "Equipo"}`;
                            img.className = "rounded border";
                            img.style.cssText =
                                "width:70px;height:70px;object-fit:cover;cursor:pointer;";
                            img.loading = "lazy";
                            img.title = "Ver fotografía";

                            img.addEventListener("click", function () {
                                verFotoEquipo(this);
                            });

                            return img.outerHTML;
                        },
                    },

                    { title: "Acciones", data: "btn_action", orderable: false },

                    {
                        data: "btn_duplicate",
                        name: "duplicate",
                        title: "Duplicar",
                        orderable: false,
                        searchable: false,
                        className: "text-center",
                        defaultContent: "",
                        visible: false,
                    },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
            self.infoCard.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_computer_equipment/",
                    data: self.data,
                    beforeSend: function () {},
                    success: function (response) {
                        var card = $(".card-info");

                        $.each(response["data"], function (index, value) {
                            card.find(`[data-key="${index}"]`).html(value).removeClass();
                            card.find(`[name='${index}']`).val(value || "-----");
                        });

                        card.find(`[data-key="current_responsible__name"]`).html(`
                            ${response["data"]["current_responsible__first_name"]}
                        `);
                        card.find("picture img").attr("src", response["data"]["image_path"]);

                        self.data.id = response["data"]["id"] || null;
                        self.data.key = "";
                    },
                    error: function (xhr, status, error) {
                        console.log("error");
                    },
                });
            };
        }

        if (options.table) {
            var mergedTableOptions = deepMerge(defaultOptions.table, options.table);
            self.table = { ...defaultOptions.table, ...mergedTableOptions };
        }

        self.init();
    }

    init() {
        const self = this;

        if (self.infoCard) {
            self.infoCard.ajax.reload();
        }

        if (self.table) {
            self.tbl_computerPeripheral = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function (d) {
                        return self.data;
                    },
                },
                columns: self.table.columns,
                order: [
                    [0, "desc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                dom:
                    "<'row'<'col-md-4'l><'col-md-4 text-center'B><'col-md-4'f>>" +
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
            });

            self.tbl_computerPeripheral.on("xhr.dt", function (e, settings, json) {
                if (!json) return;

                const esSuperusuario = json.is_superuser === true;

                self.tbl_computerPeripheral.column("duplicate:name").visible(esSuperusuario);
            });
            delete self.table;
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_computerPeripheral");

        $(document).on("click", "[data-computer-peripheral]", function (e) {
            var obj = $(this);
            var option = obj.data("computer-peripheral");

            switch (option) {
                case "refresh-table":
                    self.tbl_computerPeripheral.ajax.reload();
                    break;
                case "add-item":
                    const form = obj_modal.find("form")[0];
                    form.reset();
                    obj_modal.find("input[type='file']").val("");
                    obj_modal.find("#image_preview").attr("src", "").hide();
                    bootstrap.Modal.getOrCreateInstance(obj_modal[0]).show();

                    obj_modal.find(".modal-header").html("Registrar Periferico");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();

                    break;

                case "update-item": {
                    const form = obj_modal.find("form")[0];

                    form.reset();

                    $("#image_peripheral").val("");
                    $("#image_preview").attr("src", "");
                    $("#image_preview").hide();

                    obj_modal.find(".modal-header").html("Actualizar registro");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_computerPeripheral.row(fila).data();

                    $.each(datos, function (index, value) {
                        var input = obj_modal.find(`[name='${index}']`);
                        var isFileInput = input.is(":file");

                        if (!isFileInput) {
                            input.val(value ?? "");
                        }
                    });

                    if (datos.image_peripheral) {
                        $("#image_preview").attr("src", datos.image_peripheral);

                        $("#image_preview").show();
                    }

                    obj_modal.modal("show");

                    break;
                }

                // Dar de baja un periferico
                case "deactivate-item": {
                    const fila = $(this).closest("tr");
                    const datos = self.tbl_computerPeripheral.row(fila).data();

                    if (!datos) {
                        Swal.fire(
                            "Error",
                            "No se encontró la información del periférico.",
                            "error"
                        );
                        break;
                    }

                    const modalElement = document.getElementById("mdl-crud-disable-peripheral");

                    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);

                    const form = document.getElementById("formdisablePeripheral");

                    form.reset();

                    $("#image_preview1_peripheral, #image_preview2_peripheral")
                        .attr("src", "")
                        .hide();

                    $("#disable_detail_id").val(datos.id);
                    $("#disable_identifier").val(datos.identifier || "");

                    modal.show();

                    break;
                }

                case "duplicate-item": {
                    const fila = $(this).closest("tr");
                    const datos = self.tbl_computerPeripheral.row(fila).data();

                    console.log("Datos del periférico:", datos);

                    if (!datos) {
                        Swal.fire(
                            "Error",
                            "No se encontró la información del periférico.",
                            "error"
                        );
                        break;
                    }

                    const modalElement = document.getElementById("mdl-crud-double-peripheral");

                    const form = document.getElementById("formdoublePeripheral");

                    if (!modalElement) {
                        console.error("No se encontró el modal de duplicación.");

                        Swal.fire(
                            "Error",
                            "No se encontró el modal para duplicar el equipo.",
                            "error"
                        );
                        break;
                    }
                    if (!form) {
                        console.error(
                            "No se encontró #formdoublePeripheral. Verifica dónde está incluido el HTML del modal."
                        );

                        Swal.fire("Error", "No se encontró el formulario de duplicación.", "error");
                        break;
                    }

                    form.reset();

                    const inputId = form.querySelector("[name='detail_id']");
                    // Reiniciar las listas dependientes
                    $("#double_area_id")
                        .empty()
                        .append('<option value="">Primero seleccione una empresa</option>')
                        .prop("disabled", true);

                    $("#double_current_responsible_id")
                        .empty()
                        .append('<option value="">Primero seleccione una empresa</option>')
                        .prop("disabled", true);

                    loadCompanys();

                    if (inputId) {
                        inputId.value = datos.id;
                    }

                    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                    modal.show();

                    break;
                }

                default:
                    console.log("Opción dezconocida: " + option);
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "add" ? "add" : "update") + "_computer_peripheral/";
            var datos = new FormData(this);

            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (!response.success && response.error) {
                        Swal.fire("Error", response.error["message"], "error");
                        return;
                    } else if (!response.success && response.warning) {
                        Swal.fire("Advertencia", response.warning["message"], "warning");
                        return;
                    } else if (!response.success) {
                        Swal.fire("Error", "Ocurrio un error inesperado", "error");
                        return;
                    }
                    Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                    self.tbl_computerPeripheral.ajax.reload();
                    obj_modal.modal("hide");
                },
                error: function (xhr, status, error) {
                    var message =
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        message = xhr.responseJSON.message;
                    }
                    Swal.fire("Error del servidor", message, "error");
                },
            });
        });

        // Enviar formulario de baja de Equipos de cómputo.
        $(document)
            .off("submit.computerPeripheral", "#formdisablePeripheral")
            .on("submit.computerPeripheral", "#formdisablePeripheral", function (e) {
                e.preventDefault();

                disable_computer_peripheral(this, self.tbl_computerPeripheral);
            });
    }
}

// PREVISUALIZACIÓN IMAGEN
document.getElementById("image_peripheral").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview");

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

// DAR DE BAJA UN PERIFÉRICO
function disable_computer_peripheral(form, tabla) {
    const formData = new FormData(form);

    // Obtener el ID directamente del campo del modal.
    const detailId = $("#disable_detail_id").val();

    console.log("ID del detalle antes de enviar:", detailId);
    console.log("Datos del formulario:", [...formData.entries()]);

    if (!detailId) {
        Swal.fire({
            title: "Error",
            text: "No se encontró el ID del periférico que deseas dar de baja.",
            icon: "error",
        });
        return;
    }

    formData.set("detail_id", detailId);
    formData.set("action", "disable");

    Swal.fire({
        title: "Procesando baja",
        text: "Por favor, espera mientras se procesa la solicitud.",
        allowOutsideClick: false,
        allowEscapeKey: false,
        showConfirmButton: false,
        didOpen: function () {
            Swal.showLoading();
        },
    });

    $.ajax({
        url: "/disable_computer_peripheral/",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,

        beforeSend: function (xhr) {
            const csrfToken = $(form).find("[name='csrfmiddlewaretoken']").val();

            if (csrfToken) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        },

        success: function (response) {
            if (response.success === true) {
                const message = response.message || "El periférico se dio de baja correctamente.";

                const modalElement = document.getElementById("mdl-crud-disable-peripheral");

                form.reset();

                $("#disable_detail_id, #disable_identifier").val("");
                $("#disable_reason, #disable_description").val("");
                $("#evidence1_peripheral, #evidence2_peripheral").val("");

                $("#image_preview1_peripheral, #image_preview2_peripheral").attr("src", "").hide();

                bootstrap.Modal.getOrCreateInstance(modalElement).hide();

                // Notificar al módulo para actualizar la tabla.
                tabla.ajax.reload(null, false);

                Swal.fire({
                    title: "¡Éxito!",
                    text: message,
                    icon: "success",
                    timer: 1500,
                    showConfirmButton: false,
                });
            } else {
                Swal.fire({
                    title: "¡Error!",
                    text: response.message || "No se pudo dar de baja el periférico.",
                    icon: "error",
                });
            }
        },

        error: function (xhr) {
            const message =
                xhr.responseJSON?.message ||
                "Hubo un error al dar de baja el equipo. Intenta nuevamente.";

            Swal.fire({
                title: "¡Error!",
                text: message,
                icon: "error",
            });
        },
    });
}

// PREVISUALIZACIÓN EVIDENCIA 1
document.getElementById("evidence1_peripheral").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview1_peripheral");

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
document.getElementById("evidence2_peripheral").addEventListener("change", function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image_preview2_peripheral");

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

// Cargar las empresas en el select
function loadCompanys() {
    $.ajax({
        url: "/get_companys/",
        type: "GET",
        dataType: "json",
        success: (response) => {
            if (response.data) {
                let select = $('select[name="equipment_company"]');
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

//Duplicar periférico
$(document)
    .off("submit", "#formdoublePeripheral")
    .on("submit", "#formdoublePeripheral", function (e) {
        e.preventDefault();

        const form = this;
        const formData = new FormData(form);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        Swal.fire({
            title: "Duplicando Periférico",
            text: "Por favor, espera.",
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => Swal.showLoading(),
        });

        $.ajax({
            url: "/duplicate_computer_peripheral/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,

            success: function (response) {
                Swal.close();
                if (!response.success) {
                    Swal.fire(
                        "Error",
                        response.message || "No se pudo duplicar el equipo.",
                        "error"
                    );
                    return;
                }

                const modalElement = document.getElementById("mdl-crud-double-peripheral");

                if (modalElement) {
                    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                    modal.hide();
                }

                form.reset();

                if (
                    self.tbl_computerPeripheral &&
                    $.fn.DataTable.isDataTable(self.tbl_computerPeripheral.table().node())
                ) {
                    self.tbl_computerPeripheral.ajax.reload(null, false);
                } else {
                    console.warn(
                        "La tabla tbl_computerPeripheral no está disponible para actualizarse."
                    );
                }

                Swal.fire("Éxito", response.message, "success");
            },

            error: function (xhr) {
                console.error("Error al duplicar:", xhr.responseText);

                const mensaje =
                    xhr.responseJSON?.message || "Ocurrió un error al duplicar el equipo.";

                Swal.fire("Error", mensaje, "error");
            },
        });
    });

// Cargar responsables de la empresa seleccionada
function loadCompanyResponsiblesPeripheral(companyId) {
    const selectResponsible = $("#double_peripheral_responsible_id");

    selectResponsible
        .empty()
        .append('<option value="">Cargando usuarios...</option>')
        .prop("disabled", true);

    $.ajax({
        url: "/get_company_responsibles/",
        type: "GET",
        data: {
            company_id: companyId,
            isList: true,
        },
        dataType: "json",

        success: function (response) {
            selectResponsible.empty();

            if (!response.success) {
                selectResponsible.append('<option value="">No se encontraron usuarios</option>');
                return;
            }

            const users = response.data || [];

            selectResponsible.append('<option value="">Seleccione un responsable</option>');

            users.forEach(function (user) {
                const nombre = [user.user__first_name, user.user__last_name]
                    .filter(Boolean)
                    .join(" ");

                selectResponsible.append(
                    $("<option>", {
                        value: user.user_id,
                        text: nombre || user.user__username,
                    })
                );
            });

            selectResponsible.prop("disabled", false);

            console.log("Responsables cargados:", users);
        },

        error: function (xhr) {
            console.error("Error al cargar usuarios:", xhr.responseText);

            selectResponsible
                .empty()
                .append('<option value="">Error al cargar los usuarios</option>')
                .prop("disabled", true);

            Swal.fire("Error", "No fue posible cargar los responsables de la empresa.", "error");
        },
    });
}

// Al seleccionar una empresa, cargar usuarios
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
