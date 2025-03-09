class Users {
    constructor(options) {
        "use strict";

        const self = this;
        const defaultOptions = {
            data: {
                id: null,
            },
            list: {
                id: null,
                ajax: {
                    url: function () {
                        return "/get_vehicles_info/";
                    },
                },
            },
            table: {
                id: null,
                ajax: {
                    url: "/get_users_with_access/",
                    dataSrc: "data",
                    data: {},
                },
                columns: [
                    { title: "Id", data: "id", visible: false },
                    { title: "Rol", data: "role__name", name: "role__name" },
                    { title: "Area", data: "area__name" },
                    { title: "username", data: "user__username" },
                    { title: "Nombre", data: "user__first_name" },
                    { title: "Apellido", data: "user__last_name" },
                    { title: "Email", data: "user__email" },
                    {
                        title: "Estatus",
                        data: "user__is_active",

                        render: function (d) {
                            return d
                                ? '<span class="badge bg-outline-success">Activo</span>'
                                : '<span class="badge bg-outline-danger">Inactivo</span>';
                        },
                    },
                    { title: "Acciones", data: "btn_option", orderable: false },
                ],
            },
            userPermissionsTable: {
                id: null,
                ajax: {
                    url: "/get_userPermissions/",
                    dataSrc: "data",
                    data: {
                        user_id: null,
                    },
                },
                columns: [
                    { title: "Id", data: "submodule_id", visible: false },
                    { title: "Modulo", data: "module_name" },
                    { title: "Sub modulo", data: "submodule_name" },
                    {
                        title: "Lectura",
                        data: function (d) {
                            let checked = d["read"] ? "checked" : "";
                            return `<input type="checkbox" data-toggle="toggle" data-permission-type="read" data-submodule-id="${d["submodule_id"]}" ${checked}>`;
                        },
                        orderable: false,
                    },
                    {
                        title: "Creación",
                        data: function (d) {
                            let checked = d["create"] ? "checked" : "";
                            return `<input type="checkbox" data-toggle="toggle" data-permission-type="read" data-submodule-id="${d["submodule_id"]}" ${checked}>`;
                        },
                        orderable: false,
                    },
                    {
                        title: "Modificación",
                        data: function (d) {
                            let checked = d["update"] ? "checked" : "";
                            return `<input type="checkbox" data-toggle="toggle" data-permission-type="read" data-submodule-id="${d["submodule_id"]}" ${checked}>`;
                        },
                        orderable: false,
                    },
                    {
                        title: "Eliminar",
                        data: function (d) {
                            let checked = d["delete"] ? "checked" : "";
                            return `<input type="checkbox" data-toggle="toggle" data-permission-type="read" data-submodule-id="${d["submodule_id"]}" ${checked}>`;
                        },
                        orderable: false,
                    },
                ],
            },
        };

        self.data = defaultOptions.data;

        if (options.list) {
            self.list = { ...defaultOptions.list, ...options.list };
            self.list.ajax.reload = function () {
                $.ajax({
                    type: "GET",
                    url: "/get_users_with_access/",
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
                                `<option value="${value["user_id"]}">
                                ${value["user__first_name"] + " " + value["user__last_name"]}
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

        if (options.userPermissionsTable) {
            self.userPermissionsTable = {
                ...defaultOptions.userPermissionsTable,
                ...options.userPermissionsTable,
            };
            self.userPermissionsTable.ajax.data = function () {
                return self.data;
            };
        }

        this.init();
    }

    init() {
        const self = this;

        if (self.list) {
            self.list.ajax.reload();
        }

        if (self.table) {
            self.tbl_users = $(self.table.id).DataTable({
                ajax: {
                    url: self.table.ajax.url,
                    dataSrc: self.table.ajax.dataSrc,
                    data: self.table.ajax.data,
                },
                columns: self.table.columns,
                order: [
                    [0, "desc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
                initComplete: function () {
                    delete self.table;
                },
            });

            self.tbl_users.on("draw.dt", function () {
                var adminCount = self.tbl_users
                    .cells({ column: 1, search: "applied" })
                    .data()
                    .toArray()
                    .filter((role) => role === "Administrador").length;
                var encargadoCount = self.tbl_users
                    .cells({ column: 1, search: "applied" })
                    .data()
                    .toArray()
                    .filter((role) => role === "Encargado").length;
                var usuarioCount = self.tbl_users
                    .cells({ column: 1, search: "applied" })
                    .data()
                    .toArray()
                    .filter((role) => role === "Usuario").length;
                // Mostrar los totales en la página
                $("#adminTotal").html(adminCount);
                $("#encargadoTotal").html(encargadoCount);
                $("#usuarioTotal").html(usuarioCount);
            });
        }

        if (self.userPermissionsTable) {
            self.tbl_userPermissions = $(self.userPermissionsTable.id).DataTable({
                ajax: {
                    url: self.userPermissionsTable.ajax.url,
                    dataSrc: self.userPermissionsTable.ajax.dataSrc,
                    data: self.userPermissionsTable.ajax.data,
                },
                columns: self.userPermissionsTable.columns,
                order: [
                    [0, "asc"],
                    [1, "asc"],
                ],
                language: {
                    url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
                },
            });
            delete self.userPermissionsTable;
        }

        self.setupEventHandlers();
    }

    setupEventHandlers() {
        const self = this;
        var obj_modal = $("#mdl_users");
        var obj_modal2 = $("#mdl_update_permissions");

        $(document).on("click", "[data-user]", function (e) {
            var obj = $(this);
            var option = obj.data("user");

            switch (option) {
                case "refresh-table":
                    self.tbl_users.ajax.reload();
                    break;
                case "add-user":
                    obj_modal.find("form")[0].reset();
                    obj_modal.modal("show");
                    obj_modal.find("[name='addUser']").show();
                    obj_modal.find("[name='updateUser']").hide();
                    obj_modal.find(".modal-title").html("Agregar usuario");
                    break;
                case "update-user":
                case "update-item":
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_users.row(fila).data();

                    $.each(datos, function (index, value) {
                        obj_modal.find(`[name='${index}']`).val(value);
                    });

                    obj_modal.find("[name='role']").val(datos["role__id"]);
                    obj_modal.find("[name='username']").val(datos["user__username"]);
                    obj_modal.find("[name='name']").val(datos["user__first_name"]);
                    obj_modal.find("[name='last_name']").val(datos["user__last_name"]);
                    obj_modal.find("[name='email']").val(datos["user__email"]);

                    obj_modal.modal("show");
                    obj_modal.find("[name='addUser']").hide();
                    obj_modal.find("[name='updateUser']").show();
                    obj_modal.find(".modal-title").html("Actualizar usuario");
                    break;
                case "delete-user":
                case "dalete-item":
                    var url = "/delete_user_with_access/";
                    var fila = $(this).closest("tr");
                    var datos = self.tbl_users.row(fila).data();
                    var data = new FormData();

                    data.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());
                    data.append("id", datos["id"]);

                    deleteItem(url, data)
                        .then((message) => {
                            Swal.fire("Exito", message, "success");
                            this.tbl_audit.ajax.reload();
                        })
                        .catch((error) => {
                            Swal.fire("Error", error, "error");
                        });
                    break;
                case "sh-password":
                    let $input = $("input[name='password']");
                    let $icon = $("[name='sh-password'] i");

                    $input.attr(
                        "type",
                        $("input[name='password']").attr("type") == "password" ? "text" : "password"
                    );
                    // Cambiar el icono del ojo
                    if ($icon.hasClass("fa-eye")) {
                        $icon.removeClass("fa-eye").addClass("fa-eye-slash");
                    } else {
                        $icon.addClass("fa-eye").removeClass("fa-eye-slash");
                    }
                    break;
                case "show-user-permissions":
                    obj_modal2.modal("show");

                    var fila = $(this).closest("tr");
                    var data = self.tbl_users.row(fila).data();

                    self.data["user_id"] = data["id"];
                    self.tbl_userPermissions.ajax.reload();
                    break;
                default:
                    console.log("Opcion dezconocida:", option);
                    break;
            }
        });

        $(document).on("click", "table [type='checkbox']", function (e) {
            var obj = $(this);
            var datos = new FormData();

            datos.append("checked", obj.is(":checked") || false);
            datos.append("user_id", self.data.user_id);
            datos.append("submodule_id", obj.data("submodule-id"));
            datos.append("permission_type", obj.data("permission-type"));
            datos.append("csrfmiddlewaretoken", $("[name='csrfmiddlewaretoken']").val());

            $.ajax({
                type: "POST",
                url: "/update_userPermissions/",
                data: datos,
                processData: false,
                contentType: false,
                success: function (response) {},
                error: function (xhr, status, error) {},
            });
        });

        $("#mdl_users form").on("submit", function (e) {
            e.preventDefault();
            var submit = $("button[type='submit']:focus", this).attr("name");
            var url = "/" + (submit == "addUser" ? "add" : "update") + "_user_with_access/";
            var datos = new FormData(this);

            $.ajax({
                type: "POST",
                url: url,
                data: datos,
                processData: false,
                contentType: false,
                beforeSend: function () {
                    obj_modal.find("[type='submit']").prop("disabled", true);
                },
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
                    self.tbl_users.ajax.reload();
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
                complete: function (data) {
                    obj_modal.find("[type='submit']").prop("disabled", false);
                },
            });
        });
    }
}
