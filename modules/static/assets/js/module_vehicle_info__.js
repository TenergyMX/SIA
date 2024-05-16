$(document).ready(function () {
    var calendario_de_verificacion;

    // calendario
    $.ajax({
        type: "GET",
        url: "/static/assets/json/calendario_de_verificacion.json/",
        success: function (response) {
            if (!response.success) {
                return;
            }
            calendario_de_verificacion = response["data"];
        },
        error: function (xhr, status, error) {},
    });

    $.ajax({
        type: "GET",
        url: "/get_vehicle_info/",
        data: {
            id: $("[name='vehicle_id']").val(),
        },
        success: function (response) {
            if (!response.success && response.error) {
                Swal.fire("Error", response.error["message"], "error");
                return;
            } else if (!response.success && response.warning) {
                Swal.fire("Advertencia", response.warning["message"], "warning");
                return;
            } else if (!response.success) {
                console.log(response);
                Swal.fire("Error", "Ocurrio un error inesperado", "error");
                return;
            }
            var form = $(".card-vehicle-info");
            Object.entries(response.data).forEach(function ([clave, valor]) {
                form.find("[name='" + clave + "']").val(valor);
            });
            form.find("img").attr("src", response.data["image_path"]);
        },
        error: function (xhr, status, error) {},
    });

    // Usuarios
    $.ajax({
        type: "GET",
        url: "/get_users_with_access/",
        data: {
            id: $("[name='vehicle_id']").val(),
        },
        success: function (response) {
            if (!response.success && response.error) {
                Swal.fire("Error", response.error["message"], "error");
                return;
            } else if (!response.success && response.warning) {
                Swal.fire("Advertencia", response.warning["message"], "warning");
                return;
            } else if (!response.success) {
                console.log(response);
                Swal.fire("Error", "Ocurrio un error inesperado", "error");
                return;
            }

            $.each(response["data"], function (index, value) {
                let name =
                    value["user__first_name"] +
                    (value["user__last_name"] != "" ? " " + value["user__last_name"] : "");
                $("select[name='responsible']").append(
                    `<option value="${value["user_id"]}">${name}</option>`
                );
            });
        },
        error: function (xhr, status, error) {},
    });

    var tbl_tenencia = $("#table_tenencia").DataTable({
        ajax: {
            url: "/get_vehicle_tenencia/",
            dataSrc: function (d) {
                return d["data"];
            },
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "ID", data: "id", visible: false },
            { title: "Fecha de pago", data: "fecha_pago" },
            { title: "Monto", data: "monto" },
            {
                title: "Comprobante",
                data: function (d) {
                    if (d["comprobante_pago"] == "") {
                        return "---";
                    }
                    return `
                        <a href="/${d["comprobante_pago"]}" class="btn btn-sm btn-info" download>pago</a>
                    `;
                },
            },
            { title: "Acciones", data: "btn_action", orderable: false },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
    });

    var tbl_refrendo = $("#table_refrendo").DataTable({
        ajax: {
            url: "/get_vehicle_refrendo/",
            dataSrc: function (d) {
                return d["data"];
            },
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "ID", data: "id", visible: false },
            { title: "Fecha de pago", data: "fecha_pago" },
            { title: "Monto", data: "monto" },
            {
                title: "Comprobante",
                data: function (d) {
                    if (d["comprobante_pago"] == "") {
                        return "---";
                    }
                    return `
                        <a href="/${d["comprobante_pago"]}" class="btn btn-sm btn-info" download>pago</a>
                    `;
                },
            },
            { title: "Acciones", data: "btn_action" },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
    });

    var tbl_verificacion = $("#table_verificacion").DataTable({
        ajax: {
            url: "/get_vehicle_verificacion/",
            dataSrc: function (d) {
                return d["data"];
            },
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "ID", data: "id", visible: false },
            { title: "Engomado", data: "engomado" },
            { title: "Periodo", data: "periodo" },
            { title: "Fecha de pago", data: "fecha_pago" },
            { title: "lugar", data: "lugar" },
            { title: "Monto", data: "monto" },
            {
                title: "Comprobante",
                data: function (d) {
                    if (d["comprobante_pago"] == "") {
                        return "---";
                    }
                    return `
                        <a href="/${d["comprobante_pago"]}" class="btn btn-sm btn-info" download>pago</a>
                    `;
                },
            },
            { title: "Acciones", data: "btn_action" },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
    });

    var tbl_responsiva = $("#table_responsiva").DataTable({
        ajax: {
            url: "/get_vehicle_responsiva/",
            dataSrc: function (d) {
                return d["data"];
            },
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            { title: "ID", data: "id", visible: false },
            {
                title: "Responsable",
                data: function (d) {
                    return (
                        d["responsible__first_name"] +
                        (d["responsible__last_name"] != "" ? " " + d["responsible__last_name"] : "")
                    );
                },
            },
            { title: "Kilometraje Inicial", data: "initial_mileage" },
            { title: "Kilometraje Final", data: "final_mileage" },
            { title: "Fecha Inicio", data: "start_date" },
            { title: "fecha Final Final", data: "end_date" },
            { title: "Acciones", data: "btn_action" },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
    });

    var tbl_insurance = $("#table_insurance").DataTable({
        ajax: {
            url: "/get_vehicle_insurance/",
            dataSrc: function (d) {
                return d["data"];
            },
            data: function (d) {
                d.vehicle_id = vehicle_id;
            },
        },
        columns: [
            // "id", "responsible_id", "responsible__first_name", "responsible__last_name",
            // "policy_number", "insurance_company", "cost", "validity", "start_date", "end_date"
            { title: "ID", data: "id", visible: false },
            { title: "Num. Poliza", data: "policy_number" },
            { title: "Aseguradora", data: "insurance_company" },
            { title: "Fecha de inicio", data: "start_date" },
            { title: "Fecha final", data: "end_date" },
            {
                title: "vigencia",
                data: function (d) {
                    if (d["validity"]) {
                        return d["validity"] + " meses";
                    } else {
                        return "---";
                    }
                },
            },
            { title: "costo", data: "cost" },
            {
                title: "Responsable",
                data: function (d) {
                    return (
                        d["responsible__first_name"] +
                        (d["responsible__last_name"] != "" ? " " + d["responsible__last_name"] : "")
                    );
                },
            },
            { title: "Acciones", data: "btn_action", orderable: false },
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
    });

    // Inicialización del objeto
    var canvas_signature = new CanvasDrawing("canvas-signature");

    $(".modal [name='vehicle_id']").val(vehicle_id);
    $(".modal [name='vehicle_id']").prop("hidden", true);
    $(".modal [name='vehicle_id']").closest(".col-12").hide();

    $("[data-refresh-table]").on("click", function (e) {
        e.preventDefault();
        var obj = $(this);
        var option = obj.data("refresh-table");
        switch (option) {
            case "table_tenencia":
                tbl_tenencia.ajax.reload();
                break;
            case "table_responsiva":
                tbl_responsiva.ajax.reload();
                break;
            case "table_insurance":
                tbl_insurance.ajax.reload();
                break;
            case "table_audit":
                tbl_audit.ajax.reload();
                break;
        }
    });

    $(document).on("click", "[data-option]", function (e) {
        var obj = $(this);
        var option = obj.data("option");
        switch (option) {
            case "add-tenencia":
                var obj_modal = $("#mdl_crud_tenencia");
                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Agregar tenencia");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='add']").show();
                break;
            case "update-tenencia":
                var obj_modal = $("#mdl_crud_tenencia");
                var form = $("#mdl_crud_tenencia form");
                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Actualizar tenencia");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='update']").show();

                var fila = $(this).closest("tr");
                var datos = tbl_tenencia.row(fila).data();

                form.find("[type='file']").prop("required", false);
                $.each(datos, function (index, value) {
                    if (index != "comprobante_pago") {
                        form.find(`[name="${index}"]`).val(value);
                    }
                });
                $("[name='vehicle_id']").val(vehicle_id);
                break;
            case "delete-tenencia":
                Swal.fire({
                    title: "Deseas eliminar este registro?",
                    text: "No se podra recuperar el registro",
                    icon: "warning",
                    showCancelButton: true,
                    cancelButtonColor: "#d33",
                    cancelButtonText: "Cancelar",
                    confirmButtonText: "Si, estoy seguro",
                }).then((result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    var fila = $(this).closest("tr");
                    var datos = tbl_tenencia.row(fila).data();
                    var data = {
                        csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                        id: datos["id"],
                    };
                    $.ajax({
                        type: "GET",
                        url: "/delete_vehicle_tenencia/",
                        data: data,
                        success: function (response) {
                            if (!response.success && response.error) {
                                Swal.fire("Error", response.error["message"], "error");
                                return;
                            } else if (!response.success && response.warning) {
                                Swal.fire("Advertencia", response.warning["message"], "warning");
                                return;
                            } else if (!response.success) {
                                console.log(response);
                                Swal.fire("Error", "Ocurrio un error inesperado", "error");
                                return;
                            }
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            $("#mdl_crud_tenencia").modal("hide");
                            tbl_tenencia.ajax.reload();
                        },
                        error: function (xhr, status, error) {
                            Swal.fire(
                                "Error del servidor",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        },
                    });
                });
                break;
            case "add-refrendo":
                var obj_modal = $("#mdl_crud_refrendo");
                var form = obj_modal.find("form");
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Agregar refrendo");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='add']").show();
                break;
            case "update-refrendo":
                var obj_modal = $("#mdl_crud_refrendo");
                var form = $("#mdl_crud_refrendo form");
                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Actualizar refrendo");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='update']").show();

                var fila = $(this).closest("tr");
                var datos = tbl_refrendo.row(fila).data();

                form.find("[type='file']").prop("required", false);
                $.each(datos, function (index, value) {
                    if (index != "comprobante_pago") {
                        form.find(`[name="${index}"]`).val(value);
                    }
                });
                $("[name='vehicle_id']").val(vehicle_id);
                break;
            case "delete-refrendo":
                Swal.fire({
                    title: "Deseas eliminar este registro?",
                    text: "No se podra recuperar el registro",
                    icon: "warning",
                    showCancelButton: true,
                    cancelButtonColor: "#d33",
                    cancelButtonText: "Cancelar",
                    confirmButtonText: "Si, estoy seguro",
                }).then((result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    var fila = $(this).closest("tr");
                    var datos = tbl_refrendo.row(fila).data();
                    var data = {
                        csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                        id: datos["id"],
                    };
                    $.ajax({
                        type: "GET",
                        url: "/delete_vehicle_refrendo/",
                        data: data,
                        success: function (response) {
                            if (!response.success && response.error) {
                                Swal.fire("Error", response.error["message"], "error");
                                return;
                            } else if (!response.success && response.warning) {
                                Swal.fire("Advertencia", response.warning["message"], "warning");
                                return;
                            } else if (!response.success) {
                                console.log(response);
                                Swal.fire("Error", "Ocurrio un error inesperado", "error");
                                return;
                            }
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            $("#mdl_crud_refrendo").modal("hide");
                            tbl_refrendo.ajax.reload();
                        },
                        error: function (xhr, status, error) {
                            Swal.fire(
                                "Error del servidor",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        },
                    });
                });
                break;
            case "add-verificacion":
                var obj_modal = $("#mdl_crud_verificacion");
                var form = obj_modal.find("form");
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Agregar Verificacion");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='add']").show();

                form[0].reset();
                $("[name='vehicle_id']").val(vehicle_id);
                $(".engomado-color-bg").css("background-color", "");

                var placa = $("[name='plate']").val();
                var d = placa.charAt(placa.length - 3);

                var valorEngomado = calendario_de_verificacion[d]["engomado_ES"];
                $("[name='engomado']").val(valorEngomado).change();

                let month_1 = calendario_de_verificacion[d]["s1"][0]["month_name_ES"];
                let month_2 = calendario_de_verificacion[d]["s1"][1]["month_name_ES"];
                let month_3 = calendario_de_verificacion[d]["s2"][0]["month_name_ES"];
                let month_4 = calendario_de_verificacion[d]["s2"][1]["month_name_ES"];
                $(".message").html(
                    `Las fechas de verificación: 1er semestre (${month_1} - ${month_2}), 2do semestre (${month_3} - ${month_4}).`
                );
                break;
            case "update-verificacion":
                var obj_modal = $("#mdl_crud_verificacion");
                var form = obj_modal.find("form");
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Actualizar Verificacion");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='update']").show();

                var fila = $(this).closest("tr");
                var datos = tbl_verificacion.row(fila).data();

                form.find("[type='file']").prop("required", false);
                $.each(datos, function (index, value) {
                    if (index != "comprobante_pago") {
                        form.find(`[name="${index}"]`).val(value);
                    }
                });
                $("[name='vehicle_id']").val(vehicle_id);
                break;
            case "delete-verificacion":
                Swal.fire({
                    title: "Deseas eliminar este registro?",
                    text: "No se podra recuperar el registro",
                    icon: "warning",
                    showCancelButton: true,
                    cancelButtonColor: "#d33",
                    cancelButtonText: "Cancelar",
                    confirmButtonText: "Si, estoy seguro",
                }).then((result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    var fila = $(this).closest("tr");
                    var datos = tbl_verificacion.row(fila).data();
                    var data = {
                        csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                        id: datos["id"],
                    };
                    $.ajax({
                        type: "GET",
                        url: "/delete_vehicle_verificacion/",
                        data: data,
                        success: function (response) {
                            if (!response.success && response.error) {
                                Swal.fire("Error", response.error["message"], "error");
                                return;
                            } else if (!response.success && response.warning) {
                                Swal.fire("Advertencia", response.warning["message"], "warning");
                                return;
                            } else if (!response.success) {
                                console.log(response);
                                Swal.fire("Error", "Ocurrio un error inesperado", "error");
                                return;
                            }
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            $("#mdl_crud_verificacion").modal("hide");
                            tbl_verificacion.ajax.reload();
                        },
                        error: function (xhr, status, error) {
                            Swal.fire(
                                "Error del servidor",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        },
                    });
                });
                break;
            case "add-responsiva":
            case "record_exit":
                var obj_modal = $("#mdl_crud_responsiva");
                var form = $("#mdl_crud_responsiva form");
                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Registrar Salida");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='add']").show();
                obj_modal.find(".final").hide();
                obj_modal.find(".inicial").show();
                obj_modal.find(".final :input").prop("disabled", true);
                obj_modal.find(".inicial :input").prop("disabled", false);
                break;
            case "record_entry":
                var obj_modal = $("#mdl_crud_responsiva");
                var form = $("#mdl_crud_responsiva form");

                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Registrar Entrada");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='update']").show();
                obj_modal.find(".final").show();
                obj_modal.find(".inicial").hide();
                obj_modal.find(".final :input").prop("disabled", false);
                obj_modal.find(".inicial :input").prop("disabled", true);

                var fila = $(this).closest("tr");
                var datos = tbl_responsiva.row(fila).data();

                form.find("[name='id']").val(datos["id"]);
                form.find("[name='responsible']").val(datos["responsible_id"]);
                break;
            case "show-info":
                hideShow("#v-responsiva-pane .info", "#v-responsiva-pane .info-details");
                var fila = $(this).closest("tr");
                var datos = tbl_responsiva.row(fila).data();

                var obj_div = $("#v-responsiva-pane .info-details");
                obj_div.find(".initial_mileage").html(datos["initial_mileage"] || "---");
                obj_div.find(".final_mileage").html(datos["final_mileage"] || "---");
                obj_div.find(".initial_fuel").html(datos["initial_fuel"] || "---");
                obj_div.find(".final_fuel").html(datos["final_fuel"] || "---");
                obj_div.find(".destination").html(datos["destination"] || "---");
                obj_div.find(".trip_purpose").html(datos["trip_purpose"] || "---");
                obj_div
                    .find(".responsible_fullname")
                    .html(datos["responsible__first_name"] + " " + datos["responsible__last_name"]);

                if (datos["start_date"]) {
                    const startDate = new Date(datos["start_date"]);
                    obj_div.find(".start_date").html(startDate.toLocaleString());
                }
                if (datos["end_date"]) {
                    const endDate = new Date(datos["end_date"]);
                    obj_div.find(".end_date").html(endDate.toLocaleString());
                }
                $("img[alt='firma']").attr("src", "/" + datos["signature"]);
                break;
            case "delete-responsive":
                Swal.fire({
                    title: "Deseas eliminar este registro?",
                    text: "No se podra recuperar el registro",
                    icon: "warning",
                    showCancelButton: true,
                    cancelButtonColor: "#d33",
                    cancelButtonText: "Cancelar",
                    confirmButtonText: "Si, estoy seguro",
                }).then((result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    var fila = $(this).closest("tr");
                    var datos = tbl_responsiva.row(fila).data();
                    var data = {
                        csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                        id: datos["id"],
                    };
                    $.ajax({
                        type: "GET",
                        url: "/delete_vehicle_responsiva/",
                        data: data,
                        success: function (response) {
                            if (!response.success && response.error) {
                                Swal.fire("Error", response.error["message"], "error");
                                return;
                            } else if (!response.success && response.warning) {
                                Swal.fire("Advertencia", response.warning["message"], "warning");
                                return;
                            } else if (!response.success) {
                                console.log(response);
                                Swal.fire("Error", "Ocurrio un error inesperado", "error");
                                return;
                            }
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            $("#mdl_crud_responsiva").modal("hide");
                            tbl_responsiva.ajax.reload();
                        },
                        error: function (xhr, status, error) {
                            Swal.fire(
                                "Error del servidor",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        },
                    });
                });
                break;
            case "add-insurance":
                var obj_modal = $("#mdl_crud_insurance");
                var form = $("#mdl_crud_insurance form");
                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Agregar poliza de seguro");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='add']").show();
                obj_modal.find("[name='vehicle_id']").val(vehicle_id);
                break;
            case "update-insurance":
                var obj_modal = $("#mdl_crud_insurance");
                var form = $("#mdl_crud_insurance form");
                obj_modal.find("form")[0].reset();
                obj_modal.modal("show");
                obj_modal.find(".modal-header").html("Agregar poliza de seguro");
                obj_modal.find("[type='submit']").hide();
                obj_modal.find("[name='update']").show();
                obj_modal.find("[name='vehicle_id']").val(vehicle_id);

                var fila = $(this).closest("tr");
                var datos = tbl_insurance.row(fila).data();

                $.each(datos, function (index, value) {
                    if (index != "doc") {
                        form.find(`[name="${index}"]`).val(value);
                    }
                });
                break;
            case "delete-insurance":
                Swal.fire({
                    title: "Deseas eliminar este registro?",
                    text: "No se podra recuperar el registro",
                    icon: "warning",
                    showCancelButton: true,
                    cancelButtonColor: "#d33",
                    cancelButtonText: "Cancelar",
                    confirmButtonText: "Si, estoy seguro",
                }).then((result) => {
                    if (!result.isConfirmed) {
                        return;
                    }
                    var fila = $(this).closest("tr");
                    var datos = tbl_insurance.row(fila).data();
                    var data = {
                        csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                        id: datos["id"],
                    };
                    $.ajax({
                        type: "GET",
                        url: "/delete_vehicle_insurance/",
                        data: data,
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
                            Swal.fire("Exito", "Se ha borrado el registro", "success");
                            $("#mdl_crud_insurance").modal("hide");
                            tbl_insurance.ajax.reload();
                        },
                        error: function (xhr, status, error) {
                            Swal.fire(
                                "Error del servidor",
                                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                                "error"
                            );
                        },
                    });
                });
                break;
        }
    });

    $("[name='engomado']").on("change", function (e) {
        e.preventDefault();
        let color = $(this).val();
        let bg = {
            Amarillo: "yellow",
            Rosa: "pink",
            Rojo: "red",
            Verde: "green",
            Azul: "blue",
        };
        $(".engomado-color-bg").css("background-color", color ? bg[color] : "");
    });

    $('#mdl_crud_insurance [name="start_date"]').on("change", function (e) {
        e.preventDefault();
        var startDate = new Date($(this).val());
        var months = parseInt($('#mdl_crud_insurance [name="validity"]').val()) || 1;
        console.log(months);

        // Clonar la fecha de inicio para no modificarla directamente
        var endDate = new Date(startDate.getTime());

        // Sumar los meses
        endDate.setMonth(endDate.getMonth() + months);

        // Corregir la fecha si el día de finalización es menor al día de inicio
        if (endDate.getDate() < startDate.getDate()) {
            // Establecer el día de finalización al último día del mes anterior
            endDate.setDate(0);
        }

        var formattedDate = endDate.toISOString().slice(0, 10);
        $('#mdl_crud_insurance [name="end_date"]').val(formattedDate);
    });

    $("#mdl_crud_tenencia form").on("submit", function (e) {
        e.preventDefault();
        var submit = $("button[type='submit']:focus", this).attr("name");
        var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_tenencia/";
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
                    console.log(response);
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    return;
                }
                Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                tbl_tenencia.ajax.reload();
                $("#mdl_crud_tenencia").modal("hide");
            },
            error: function (xhr, status, error) {
                Swal.fire(
                    "Error del servidor",
                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                    "error"
                );
            },
        });
    });

    $("#mdl_crud_refrendo form").on("submit", function (e) {
        e.preventDefault();
        var submit = $("button[type='submit']:focus", this).attr("name");
        var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_refrendo/";
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
                    console.log(response);
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    return;
                }
                Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                tbl_refrendo.ajax.reload();
                $("#mdl_crud_refrendo").modal("hide");
            },
            error: function (xhr, status, error) {
                Swal.fire(
                    "Error del servidor",
                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                    "error"
                );
            },
        });
    });

    $("#mdl_crud_verificacion form").on("submit", function (e) {
        e.preventDefault();
        var submit = $("button[type='submit']:focus", this).attr("name");
        var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_verificacion/";
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
                    console.log(response);
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    return;
                }
                Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                tbl_verificacion.ajax.reload();
                $("#mdl_crud_verificacion").modal("hide");
            },
            error: function (xhr, status, error) {
                Swal.fire(
                    "Error del servidor",
                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                    "error"
                );
            },
        });
    });

    $("#mdl_crud_responsiva form").on("submit", function (e) {
        e.preventDefault();
        var url = "/";
        var submit = $("button[type='submit']:focus", this).attr("name");
        var datos = new FormData(this);

        if (submit == "add" && !canvas_signature.hasDrawing()) {
            Swal.fire("Sin firma", "El responsable debe firmar", "warning");
            return;
        }

        if (submit == "add") {
            url += "add_vehicle_responsiva/";

            canvas_signature
                .getCanvasBlob()
                .then((blob) => {
                    datos.append("signature", blob, "signature.png");

                    sendData("POST", url, datos)
                        .then((response) => {
                            canvas_signature.clearCanvas();
                            $("#mdl_crud_responsiva").modal("hide");
                            Swal.fire("Exito", "Salida Registrada", "success");
                            tbl_responsiva.ajax.reload();
                        })
                        .catch((error) => {
                            custom_alert_error(error);
                        });
                })
                .catch((error) => {
                    custom_alert_error(error);
                });
        } else {
            url += "update_vehicle_responsiva/";
            sendData("POST", url, datos)
                .then((response) => {
                    $("#mdl_crud_responsiva").modal("hide");
                    Swal.fire("Exito", "Salida Registrada", "success");
                    tbl_responsiva.ajax.reload();
                })
                .catch((error) => {
                    custom_alert_error(error);
                });
        }
    });

    $("#mdl_crud_insurance form").on("submit", function (e) {
        e.preventDefault();
        var submit = $("button[type='submit']:focus", this).attr("name");
        var url = "/" + (submit == "add" ? "add" : "update") + "_vehicle_insurance/";
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
                    console.log(response);
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    return;
                }
                Swal.fire("Exito", "Se han guardado los datos con exito", "success");
                tbl_insurance.ajax.reload();
                $("#mdl_crud_insurance").modal("hide");
            },
            error: function (xhr, status, error) {
                Swal.fire(
                    "Error del servidor",
                    "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                    "error"
                );
            },
        });
    });

    getVehicles();

    function getVehicles() {
        $.ajax({
            type: "GET",
            url: "/get_vehicles_info/",
            success: function (response) {
                if (!response.success && response.error) {
                    Swal.fire("Error", response.error["message"], "error");
                    return;
                } else if (!response.success && response.warning) {
                    Swal.fire("Advertencia", response.warning["message"], "warning");
                    return;
                } else if (!response.success) {
                    console.log(response);
                    Swal.fire("Error", "Ocurrio un error inesperado", "error");
                    return;
                }
                var select_users = $("form select[name='vehicle_id']");
                select_users.html(`<option value="" seleted>-----</option>`);
                $.each(response["data"], function (index, value) {
                    select_users.append(`<option value="${value.id}">${value.name}</option>`);
                });
            },
            error: function (xhr, status, error) {
                alertify.notify("No se ha podido cargar los vehiculos", "error", 3);
                console.error("Error en la petición AJAX:", error);
            },
        });
    }
});
