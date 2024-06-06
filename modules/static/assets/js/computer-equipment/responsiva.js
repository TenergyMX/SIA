class ComputerEquipment_responsiva {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {},
            list: {
                id: null,
                ajax: {},
            },
            table: {
                id: "",
                ajax: {
                    url: "/get-computer-equipment-responsivas/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
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
                    },
                    {
                        title: "Creado",
                        data: "created_at",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                    },
                    {
                        title: "Ultima actualización",
                        data: "updated_at",
                        render: function (data, type, row) {
                            if (type === "display" || type === "filter") {
                                return moment(data).locale("es").format("D [de] MMMM [de] YYYY");
                            }
                            return data;
                        },
                    },
                    {
                        title: "Responsiva",
                        data: function (d) {
                            if (d["responsibility_letter"]) {
                                return `<a href="/${d["responsibility_letter"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Responsiva
                                </a>`;
                            } else {
                                return "Sin Responsiva";
                            }
                        },
                        orderable: false,
                    },
                    {
                        title: "Historial",
                        data: function (d) {
                            return `<button
                                type="button"
                                class="btn btn-sm btn-outline-primary"
                                data-sia-computer-equipment-responsiva="record"
                            >
                                Historial
                            </button>`;
                        },
                        orderable: false,
                    },
                    { title: "Acciones", data: "btn_action", orderable: false },
                ],
            },
        };

        self.data = { ...defaultOptions.data, ...options.data };

        if (options.computer) {
            self.computer = options.computer;
            self.data = { ...self.data, ...self.computer.data };
        }

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get-computer-equipment-responsivas/",
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
                                `<option value="${value["id"]}" data-sia-user-id="${
                                    value["responsible_id"]
                                }">
                                ${
                                    value["responsible__first_name"] +
                                    " " +
                                    value["responsible__last_name"]
                                }
                            </option>`
                            );
                        });
                    },
                    error: function (xhr, status, error) {},
                });
            };
        }

        if (options.table) {
            self.table = { ...defaultOptions.table, ...options.table };
        }

        self.init();
    }

    init() {
        const self = this;
        var obj_modal = $("#mdl-crud-computer-equipment-responsiva");

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_responsiva = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: function () {
                        return self.data;
                    },
                },
                columns: self.table.columns,
                order: [
                    [0, "asc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                dom:
                    "<'row justify-content-between'<'col-md-auto'l><'col-md-auto'f>>" +
                    "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
                    "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
                initComplete: function (settings, json) {
                    delete self.table;
                },
            });
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl-crud-computer-equipment-responsiva");
        var obj_modal2 = $("#mdl-crud-computer-equipment-responsiva-record");

        $(document).on("click", "[data-sia-computer-equipment-responsiva]", function (e) {
            var obj = $(this);
            var option = obj.data("sia-computer-equipment-responsiva");

            switch (option) {
                case "refresh-table":
                    self.tbl_responsiva.ajax.reload();
                    break;
                case "add-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Agregar responsiva");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='add']").show();
                    obj_modal.find("[name='responsible_id']").trigger("change");
                    break;
                case "update-item":
                    obj_modal.modal("show");
                    obj_modal.find("form")[0].reset();
                    obj_modal.find(".modal-header .modal-title").html("Actualizar Responsiva");
                    obj_modal.find("[type='submit']").hide();
                    obj_modal.find("[name='update']").show();

                    var fila = $(this).closest("tr");
                    var datos = self.tbl_responsiva.row(fila).data();

                    $.each(datos, function (index, value) {
                        var isFileInput = obj_modal.find(`[name='${index}']`).is(":file");
                        if (!isFileInput) {
                            obj_modal.find(`[name='${index}']`).val(value || "");
                        }
                    });

                    obj_modal.find("[name='responsible_id']").trigger("change");
                    break;
                case "delete-item":
                    var url = "/delete-computer-equipment-responsiva/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_responsiva.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            self.tbl_responsiva.ajax.reload();
                        })
                        .catch((error) => {
                            var message = "Se ha producido un problema en el servidor.";
                            message += " Por favor, inténtalo de nuevo más tarde.";
                            if (typeof error === "string") {
                                message = error;
                            }

                            Swal.fire("Error", error, "error");
                        });
                    break;
                case "record":
                    obj_modal2.modal("show");

                    // Obtener la fila más cercana al botón clickeado
                    var fila = $(this).closest("tr");
                    // Obtener los datos de la fila usando DataTables
                    var datos = self.tbl_responsiva.row(fila).data();
                    // Parsear el registro JSON a un array de objetos
                    var record = JSON.parse(datos["record"]);
                    // Obtener el cuerpo de la tabla en el modal
                    var tbody = obj_modal2.find("table tbody");

                    // Limpiar cualquier contenido anterior en el cuerpo de la tabla
                    tbody.empty();

                    // Iterar sobre cada registro en el array
                    $.each(record, function (index, value) {
                        // Formatear la fecha usando moment.js
                        var formattedDate = value["date"]
                            ? moment(value["date"]).format("D [de] MMMM [de] YYYY")
                            : "-----";
                        // Crear una nueva fila de la tabla con los datos
                        var tr = `<tr>
                            <td>${value["id"]}</td>
                            <td>${formattedDate}</td>
                            <td>
                                <a href="/${value["file_path"]}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    Responsiva
                                </a>
                            </td>
                        </tr>`;
                        // Añadir la nueva fila al cuerpo de la tabla
                        tbody.append(tr);
                    });
                    break;
                default:
                    console.log("Opcion dezconocida:", option);
                    break;
            }
        });

        obj_modal.find("form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url =
                "/" + (submit == "add" ? "add" : "update") + "-computer-equipment-responsiva/";
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
                    message = response.message || "Se han guardado los datos con éxito";
                    obj_modal.modal("hide");
                    Swal.fire("Éxito", message, "success");
                    self.tbl_responsiva.ajax.reload();
                },
                error: function (xhr, status, error) {
                    let errorMessage = "Ocurrió un error inesperado";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    }
                    Swal.fire("Error", errorMessage, "error");
                    console.log("Error en la petición AJAX:");
                    console.error("xhr:", xhr);
                },
            });
        });

        obj_modal.find("[name='responsible_id']").on("change", function () {
            var valor = $(this).val().toLowerCase();

            if (valor == "") {
                obj_modal.find("a").closest("div").hide();
            } else {
                obj_modal.find("a").closest("div").show();

                var ruta = `/computers-equipment/responsiva/pdf/?user_id=${valor}`;
                obj_modal.find("a").attr("href", ruta);
            }
        });
    }
}
