class ComputerEquipment {
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
                        return "/get-computer-equipment/";
                    },
                    data: function () {},
                    reload: function () {},
                },
            },
            list: {
                id: null,
                ajax: {},
            },

            // tarjetas
            cards: {
                id: "#computer_cards",
            },

            table: {
                id: "#computer_equipment_table",

                ajax: {
                    url: "/get-computers-equipment/",
                    dataSrc: "data",
                    data: {},
                },

                columns: [
                    { title: "ID", data: "id", visible: false },
                    { title: "Identificador", data: "identifier" },
                    { title: "Área", data: "area__name", className: "toggleable" },
                    { title: "Equipo", data: "name", className: "toggleable" },
                    {
                        title: "Numero de serie",
                        data: "serial_number",
                        className: "toggleable",
                        visible: false,
                    },
                    {
                        title: "Responsable",
                        data: function (d) {
                            const firstName = d["current_responsible__first_name"]
                                ? d["current_responsible__first_name"]
                                : "";
                            const lastName = d["current_responsible__last_name"]
                                ? ` ${d["current_responsible__last_name"]}`
                                : "";
                            return `${firstName}${lastName}`;
                        },
                        className: "toggleable",
                    },
                    { title: "Tipo de equipo", data: "equipment_type", className: "toggleable" },
                    { title: "S.O.", data: "so", className: "toggleable", visible: false },
                    { title: "Marca", data: "brand", className: "toggleable" },
                    { title: "Modelo", data: "model", className: "toggleable" },
                    // {
                    //     title: "Fecha Adquisición",
                    //     data: "adquisition_date",
                    //     className: "toggleable",
                    // },
                    {
                        title: "Procesador",
                        data: "processor",
                        className: "toggleable",
                        visible: false,
                    },
                    { title: "RAM", data: "ram", className: "toggleable", visible: false },
                    {
                        title: "Actividad del Equipo",
                        data: "is_active",
                        render: function (data, type, row) {
                            return data ? "Activo" : "Inactivo";
                        },
                        className: "toggleable",
                    },
                    { title: "Estado", data: "equipment_status", className: "toggleable" },
                    {
                        title: "Comentarios",
                        data: "comments",
                        className: "toggleable",
                        visible: true,
                    },

                    {
                        title: "Ver factura",
                        data: "btn_view_factura",
                        orderable: false,
                        className: "text-center",
                    },

                    {
                        title: "Imagen",
                        data: "image_url",
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

        if (options.cards) {
            self.cards = { ...defaultOptions.cards, ...options.cards };
        } else {
            self.cards = defaultOptions.cards;
        }

        if (options.infoCard) {
            self.infoCard = { ...defaultOptions.infoCard, ...options.infoCard };
            self.infoCard.ajax.reload = function () {
                Swal.fire({
                    title: "Cargando información",
                    text: "Por favor, espera mientras se carga la información.",
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    showConfirmButton: false,
                    didOpen: () => {
                        Swal.showLoading();
                    },
                });

                $.ajax({
                    type: "GET",
                    url: "/get-computer-equipment/",
                    data: self.data,
                    beforeSend: function () {},
                    success: function (response) {
                        Swal.close();

                        var card = $(".card-info");

                        $.each(response["data"], function (index, value) {
                            card.find(`[data-key="${index}"]`).html(value).removeClass();
                            card.find(`[name='${index}']`).val(value || "-----");
                        });

                        // card.find(`[data-key="current_responsible__name"]`).html(`
                        //     ${response["data"]["current_responsible__first_name"]}
                        // `);

                        card.find(`[data-key="previous_responsible__first_name"]`).html(
                            function () {
                                var d = response["data"];
                                const firstName = d["previous_responsible__first_name"]
                                    ? d["previous_responsible__first_name"]
                                    : "";
                                const lastName = d["previous_responsible__last_name"]
                                    ? ` ${d["previous_responsible__last_name"]}`
                                    : "";
                                return `${firstName}${lastName}`;
                            }
                        );

                        card.find(`[data-key="current_responsible__first_name"]`).html(function () {
                            var d = response["data"];
                            const firstName = d["current_responsible__first_name"]
                                ? d["current_responsible__first_name"]
                                : "";
                            const lastName = d["current_responsible__last_name"]
                                ? ` ${d["current_responsible__last_name"]}`
                                : "";
                            return `${firstName}${lastName}`;
                        });

                        // card.find("picture img").attr("src", response["data"]["image_path"]);

                        self.data.id = response["data"]["id"] || null;
                        self.data.key = "";
                        self.data.name = response["data"]["name"];
                        self.data.model = response["data"]["model"];
                    },
                    error: function (xhr, status, error) {
                        console.log("error");
                    },
                });
            };
        }

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-computers-equipment/",
                    data: {
                        isList: true,
                    },
                    beforeSend: function () {},
                    success: function (response) {
                        var select = $(self.list.id);
                        select.html(null);
                        select.append("<option value=''>-----</option>");
                        $.each(response["data"], function (index, value) {
                            select.append(
                                `<option value="${value["id"]}">
                                    ${value["name"]}
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
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

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_computerEquipment = $(self.table.id).DataTable({
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
                    const tabla = this.api();
                    const esSuperusuario = json && json.is_superuser === true;
                    tabla.column("duplicate:name").visible(esSuperusuario);
                },
            });

            self.tbl_computerEquipment.on("xhr.dt", function (e, settings, json) {
                if (!json) return;

                const esSuperusuario = json.is_superuser === true;

                self.tbl_computerEquipment.column("duplicate:name").visible(esSuperusuario);
            });

            //self.loadCards();
            delete self.table;
        }
        self.setupEventHandlers();
    }

    // loadCards() {
    //     const self = this;

    //     $.ajax({
    //         type: "GET",
    //         url: self.table.ajax.url,
    //         dataType: "json",
    //         success: function (response) {
    //             let html = "";

    //             $.each(response.data, function (i, item) {
    //                 const responsable =
    //                     (item.current_responsible__first_name || "") +
    //                     " " +
    //                     (item.current_responsible__last_name || "");

    //                 html += `
    //                 <div class="col-xl-4 col-lg-6 col-md-6">

    //                     <div class="card shadow-sm h-100">

    //                         <div class="card-body">

    //                             <div class="d-flex justify-content-between">

    //                                 <div class="d-flex">

    //                                     <div class="bg-primary text-white rounded p-2 me-2">
    //                                         <i class="fa-solid fa-laptop"></i>
    //                                     </div>

    //                                     <div>
    //                                         <h5 class="fw-bold mb-0">
    //                                             ${item.name || "-"}
    //                                         </h5>

    //                                         <small class="text-muted">
    //                                             ${item.identifier || "-"}
    //                                         </small>
    //                                     </div>

    //                                 </div>

    //                                 <span class="badge bg-primary">
    //                                     ${item.brand || "-"}
    //                                 </span>

    //                             </div>

    //                         </div>

    //                         <div class="px-3 mb-3">

    //                             <span class="badge bg-info">
    //                                 ${item.equipment_type || "-"}
    //                             </span>

    //                             <span class="badge ${
    //                                 item.equipment_status == "En uso" ? "bg-success" : "bg-warning"
    //                             }">
    //                                 ${item.equipment_status || "-"}
    //                             </span>

    //                             <span class="badge ${item.is_active ? "bg-success" : "bg-danger"}">

    //                                 ${item.is_active ? "Activo" : "Inactivo"}

    //                             </span>

    //                         </div>

    //                         <div class="row px-3">

    //                             <div class="col-6">
    //                                 <small class="text-muted">
    //                                     Área
    //                                 </small>

    //                                 <h6>
    //                                     ${item.area__name || "-"}
    //                                 </h6>

    //                             </div>

    //                             <div class="col-6">
    //                                 <small class="text-muted">
    //                                     Responsable
    //                                 </small>

    //                                 <h6>
    //                                     ${responsable}
    //                                 </h6>

    //                             </div>

    //                         </div>

    //                         <div class="row px-3 mt-3">

    //                             <div class="col-6">
    //                                 <small class="text-muted">
    //                                     Modelo
    //                                 </small>

    //                                 <h6>
    //                                     ${item.model || "-"}
    //                                 </h6>

    //                             </div>

    //                             <div class="col-6">
    //                                 <small class="text-muted">
    //                                     Sistema Operativo
    //                                 </small>

    //                                 <h6>
    //                                     ${item.so || "-"}
    //                                 </h6>

    //                             </div>

    //                         </div>

    //                         <div class="mx-3 mt-3 p-2 bg-light rounded">

    //                             ${item.serial_number || "-"}

    //                         </div>

    //                         <div class="p-3">

    //                             <strong>Comentarios:</strong><br>

    //                             ${item.comments || "Sin comentarios"}

    //                         </div>

    //                         <div class="card-footer bg-white">

    //                             <div class="d-flex justify-content-center gap-2">

    //                                 ${item.btn_view_factura}

    //                                 ${item.btn_action}

    //                             </div>

    //                         </div>

    //                     </div>

    //                 </div>
    //                 `;
    //             });

    //             $(self.cards.id).html(html);
    //         },
    //     });
    // }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_crud_computerSystem");

        $(document).on("click", "[data-computer-system]", function (e) {
            var obj = $(this);
            var option = obj.data("computer-system");

            switch (option) {
                case "refresh-table":
                    self.tbl_computerEquipment.ajax.reload();
                    break;

                case "add-item": {
                    const form = obj_modal.find("form")[0];
                    form.reset();
                    obj_modal.find("input[type='file']").val("");
                    obj_modal.find("#image_preview").attr("src", "").hide();
                    bootstrap.Modal.getOrCreateInstance(obj_modal[0]).show();

                    obj_modal.find(".modal-header").html("Registrar Equipo de cómputo");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    break;
                }

                case "update-item": {
                    const form = obj_modal.find("form")[0];

                    form.reset();
                    obj_modal.find("input[type='file']").val("");
                    obj_modal.find("#image_preview").attr("src", "").hide();
                    bootstrap.Modal.getOrCreateInstance(obj_modal[0]).show();
                    obj_modal.find(".modal-header").html("Actualizar Equipo de cómputo");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    const fila = $(this).closest("tr");
                    const datos = self.tbl_computerEquipment.row(fila).data();

                    $.each(datos, function (index, value) {
                        const campo = obj_modal.find(`[name='${index}']`);

                        if (campo.length && !campo.is(":file")) {
                            campo.val(value ?? "");
                        }
                    });

                    obj_modal
                        .find("[name='is_active']")
                        .val(datos["is_active"] == true ? "1" : "0");

                    if (datos["image_url"]) {
                        obj_modal.find("#image_preview").attr("src", datos["image_url"]).show();
                    }

                    break;
                }

                // Dar de baja un equipo de cómputo.
                case "deactivate-item": {
                    const fila = $(this).closest("tr");
                    const datos = self.tbl_computerEquipment.row(fila).data();

                    if (!datos) {
                        Swal.fire("Error", "No se encontró la información del equipo.", "error");
                        break;
                    }

                    const modalElement = document.getElementById("mdl-crud-disable-computer");

                    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);

                    const form = document.getElementById("formdisableComputer");

                    form.reset();

                    $("#image_preview1, #image_preview2").attr("src", "").hide();

                    $("#disable_detail_id").val(datos.id);
                    $("#disable_identifier").val(datos.identifier || "");

                    modal.show();

                    break;
                }

                case "duplicate-item": {
                    const fila = $(this).closest("tr");
                    const datos = self.tbl_computerEquipment.row(fila).data();

                    console.log("Datos del equipo:", datos);

                    if (!datos) {
                        Swal.fire("Error", "No se encontró la información del equipo.", "error");
                        break;
                    }

                    const modalElement = document.getElementById("mdl-crud-double-computer");

                    const form = document.getElementById("formdoubleComputer");

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
                            "No se encontró #formdoubleComputer. Verifica dónde está incluido el HTML del modal."
                        );

                        Swal.fire("Error", "No se encontró el formulario de duplicación.", "error");
                        break;
                    }

                    form.reset();

                    const inputId = form.querySelector("[name='detail_id']");

                    loadCompanys();

                    if (inputId) {
                        inputId.value = datos.id;
                    }

                    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
                    modal.show();

                    break;
                }
            }
        });

        //agregar, actualizar el equipo
        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();

            const form = this;

            const boton = e.originalEvent?.submitter || document.activeElement;
            const submit = $(boton).attr("name");

            if (submit !== "add" && submit !== "update") {
                Swal.fire(
                    "Error",
                    "No se pudo identificar la operación que deseas realizar.",
                    "error"
                );
                return;
            }

            const url = "/" + submit + "-computer-system/";

            const datos = new FormData(form);

            Swal.fire({
                title: "Guardando información",
                text: "Por favor, espera mientras se guarda la información.",
                allowOutsideClick: false,
                allowEscapeKey: false,
                showConfirmButton: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });

            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,

                success: function (response) {
                    if (response.success !== true) {
                        Swal.fire(
                            "Error",
                            response.message ||
                                response.error?.message ||
                                "Ocurrió un error inesperado.",
                            "error"
                        );
                        return;
                    }

                    const message = response.message || "Se han guardado los datos con éxito.";

                    bootstrap.Modal.getOrCreateInstance(obj_modal[0]).hide();

                    form.reset();
                    obj_modal.find("input[type='file']").val("");
                    obj_modal.find("#image_preview").attr("src", "").hide();

                    self.tbl_computerEquipment.ajax.reload(null, false);

                    Swal.fire({
                        title: "Éxito",
                        text: message,
                        icon: "success",
                        confirmButtonText: "Aceptar",
                    });

                    //self.loadCards();
                },

                error: function (xhr, status, error) {
                    Swal.close();

                    let message =
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.";

                    if (xhr.responseJSON) {
                        message =
                            xhr.responseJSON.message || xhr.responseJSON.error?.message || message;
                    }

                    Swal.fire("Error del servidor", message, "error");
                },
            });
        });

        // Enviar formulario de baja de Equipos de cómputo.
        $(document)
            .off("submit.computerSystem", "#formdisableComputer")
            .on("submit.computerSystem", "#formdisableComputer", function (e) {
                e.preventDefault();

                disable_computer_system(this, self.tbl_computerEquipment);
            });
    }
}

// DAR DE BAJA EQUIPO DE CÓMPUTO
function disable_computer_system(form, tabla) {
    const formData = new FormData(form);

    // Obtener el ID directamente del campo del modal.
    const detailId = $("#disable_detail_id").val();

    console.log("ID del detalle antes de enviar:", detailId);
    console.log("Datos del formulario:", [...formData.entries()]);

    if (!detailId) {
        Swal.fire({
            title: "Error",
            text: "No se encontró el ID del equipo que deseas dar de baja.",
            icon: "error",
        });
        return;
    }

    // Garantizar que Django reciba estos campos.
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
        url: "/disable_computer_system/",
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
                const message = response.message || "El equipo se dio de baja correctamente.";

                const modalElement = document.getElementById("mdl-crud-disable-computer");

                form.reset();

                $("#disable_detail_id, #disable_identifier").val("");
                $("#disable_reason, #disable_description").val("");
                $("#evidence1, #evidence2").val("");

                $("#image_preview1, #image_preview2").attr("src", "").hide();

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
                    text: response.message || "No se pudo dar de baja el equipo.",
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

// PREVISUALIZACIÓN IMAGEN
document.getElementById("image").addEventListener("change", function (event) {
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
