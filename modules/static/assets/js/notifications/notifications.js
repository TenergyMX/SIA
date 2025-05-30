let table = "";
$(document).ready(function () {
    init_select();

    /*table system notifications ajax*/
    table = new DataTable("#table-notifications", {
        ajax: {
            url: "/notifications/get-notification-system/",
            type: "GET",
            dataSrc: "data",
        },
        columns: [
            {
                render: function (data, type, row) {
                    return row.usuario.includes("area-")
                        ? row.usuario.replace(/area-/g, "")
                        : row.usuario;
                },
            },
            { data: "mods" },
            {
                render: function (data, type, row) {
                    return row.cats === "todos" ? "Todos los submódulos" : row.cats;
                },
            },
            {
                render: function (data, type, row) {
                    let flag =
                        row.itemsID === "0" ? "Todos los registros" : `Registros ${row.itemsID}`;
                    return flag;
                },
            },
            {
                render: function (data, type, row) {
                    return row.active === true ? "Activo" : "Inactivo";
                },
            },
            {
                render: function (data, type, row) {
                    return row.status;
                },
            },
            {
                render: function (data, type, row) {
                    buttons = `<button class="btn btn-success btn-sm" onclick="updateNotification(${row.id})"><i class="fa-solid fa-pen-to-square"></i></button>`;
                    buttons += `<button class="btn btn-danger btn-sm" onclick="deleteNotification(${row.id})"><i class="fa-solid fa-trash"></i></button>`;
                    return buttons;
                },
            },
        ],
        createdRow: function (row, data, dataIndex) {
            $(row).prop("id", `e-${data.id}`);
        },
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
    });

    //insert the information options in each select from the modal
    $("#swal-form-data-information").on("submit", function (e) {
        e.preventDefault();
        //MODULO PRINCIPAL
        let main = $("#swal-form-data-information input:first").val();

        //SUBMODULOS
        let modulos = $("#mci-slt-submodulos")
            .select2("data")
            .map((item) => item.text);
        let modulosID = $("#mci-slt-submodulos").val();

        //REGISTROS
        let items = $("#mci-slt-items")
            .select2("data")
            .map((item) => item.text);
        let itemsID = $("#mci-slt-items").val();

        if (modulosID.length == 0 || itemsID.length == 0) {
            Swal.fire("Error", "Alguno de los campos deben tener información", "error");
            return;
        }

        let option_class = main.replaceAll(" ", "-");
        span = `<span class="badge text-bg-secondary text-wrap mt-1 span__${option_class}" data-area='${main}' data-mods='${modulosID}' data-items='${itemsID}'>${main} >> ${modulos} >> ${items}</span>`;
        if ($(`.span__${option_class}`).length == 0) {
            $("#placeholder-notifications").append(span);
            $(`.chbox-${option_class}`).prop("checked", true);
        } else {
            $(`.span__${option_class}`)
                .html(`${main} >> ${modulos} >> ${items}`)
                .attr("data-items", itemsID)
                .attr("data-mods", modulosID);
        }
        $("#mdl-category-items").modal("hide");
    });

    //
    $("#swal_buttonNotifications").on("click", function (e) {
        e.preventDefault();
        notification = "";
        html_notifications = "";
        /*Conseguir la información de los módulos*/
        $("#placeholder-notifications span").each(function (index, element) {
            notification += `${this.dataset.area}||${this.dataset.mods}||${this.dataset.items}|//|`;
            noti_txt = $(this).text().split(" >> ");
            html_notifications += `
                <strong>${noti_txt[0]}</strong>
                <p class="m-0" style="padding-left:1.5rem;">${noti_txt[1]}</p>
                <p class="m-0" style="padding-left:3rem;">${noti_txt[2]}</p>
            `;
        });
        users = "";
        html_user = "";
        /*Conseguir la información de los usuarios*/
        $("#placeholder-users span").each(function (index, element) {
            txt_email = $(this).text();
            users += `${txt_email}|//|`;
            html_user += `<p class="m-0">${txt_email}</p>`;
        });

        data = {
            notification: notification,
            users: users,
        };

        Swal.fire({
            title: "<strong>¿Estás seguro de los siguientes registros?</strong>",
            icon: "info",
            html: `
            <div class="row text-start"><h6 class="m-0"><strong>Acceso a los siguientes usuarios</strong></h6></div>
            <div class="row text-start"><div class="col container">${html_user}</div></div>
            <div class="row text-start"><h6 class="m-0"><strong>Acceso a los siguientes registros</strong></h6></div>
            <div class="row text-start"><div class="col container">${html_notifications}</div></div>`,
            showCloseButton: true,
            showCancelButton: true,
            focusConfirm: false,
            confirmButtonText: `Confirmar`,
            confirmButtonColor: "#198754",
            cancelButtonText: `No`,
            cancelButtonColor: "#dc3545",
        }).then((result) => {
            if (result.isConfirmed) {
                swal_wait();
                $.ajax({
                    type: "GET",
                    url: "/notifications/create-notification/",
                    data: data,
                    success: function (result) {
                        if (result.status == "error") {
                            Swal.fire("Error", result.message, result.status);
                            return;
                        }
                        table.ajax.reload();
                        $("#forms-notifications-system input[type='checkbox']").prop(
                            "checked",
                            false
                        );
                        $("#placeholder-notifications, #placeholder-users").html(null);
                        Swal.fire("", result.message, result.status);
                    },
                    error: function (xhr, status, error) {
                        Swal.fire(
                            "Error del servidor",
                            "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                            "error"
                        );
                    },
                });
            }
        });
    });
});

//Function display the information-users
function mci_selects_users(checkbox) {
    let email = checkbox.dataset.email.includes("area-")
        ? checkbox.dataset.email.replace(/area-/g, "")
        : checkbox.dataset.email;

    let userClass = checkbox.dataset.id == null ? email : checkbox.dataset.id;

    if (checkbox.checked) {
        let span = `<span class="badge text-bg-secondary text-wrap mt-1 span__${userClass}">${email}</span>`;
        $("#placeholder-users").append(span);
    } else {
        $(`.span__${userClass}`).remove();
    }
}

//Function display the information-areas
function mci_selects_all(option, checkbox) {
    let option_class = option.replaceAll(" ", "-");
    if (checkbox.checked) {
        let span = `<span class="badge text-bg-secondary text-wrap mt-1 span__${option_class}" data-area='${option}' data-mods='0' data-items='0'>${option} >> Todos los módulos >> Todos los registros</span>`;
        $("#placeholder-notifications").append(span);
    } else {
        $(`.span__${option_class}`).remove();
    }
}

//Function to display the data-information of submodules and items-register for each submodule
function mci_selects_items(option) {
    swal_wait();
    $.ajax({
        type: "GET",
        url: "/notifications/mci-read-moduls/",
        data: { option: option },
        success: function (result) {
            if (result.status == "error") {
                Swal.fire("Error", result.message, result.status);
                return;
            }
            /*Clean selects*/
            $("#mci-slt-submodulos").empty().trigger("change");
            $("#mci-slt-items").empty().trigger("change");

            /*Draw select->options items*/
            let items = JSON.parse(result.items);
            $("#mci-slt-items")
                .append(new Option("Todos los registros", "0", false, false))
                .trigger("change");
            items.forEach((e) => {
                let name = "";
                if ("name" in e.fields) {
                    name = e.fields.name;
                } else if ("name_service" in e.fields) {
                    name = e.fields.name_service;
                } else if ("equipment_name" in e.fields) {
                    name = e.fields.equipment_name;
                }

                let data = {
                    id: e.pk,
                    text: name,
                };
                var newOption = new Option(data.text, data.id, false, false);
                $("#mci-slt-items").append(newOption).trigger("change");
            });

            /*Draw select->options submodules*/
            $("#mci-slt-submodulos")
                .append(new Option("Todos los módulos", "0", false, false))
                .trigger("change");
            result.modules.forEach((e) => {
                let data = {
                    id: e.id,
                    text: e.name,
                };
                var newOption = new Option(data.text, data.id, false, false);
                $(newOption).attr("data-mod-name", e.name);
                $("#mci-slt-submodulos").append(newOption).trigger("change");
            });

            $("#swal-form-data-information input:first").val(option);

            /*In case an span is selected get the options*/
            let span = $(`.span__${option.replaceAll(" ", "-")}`);
            let tempVal = [];
            if (span.length != 0) {
                let tempMod = span.html().split(" &gt;&gt; ")[1];
                tempMod.split(",").forEach((e) => {
                    if ($(`option[data-mod-name='${e}']`).length == 0) {
                        tempVal.push(0);
                    } else {
                        tempVal.push($(`option[data-mod-name='${e}']`).val());
                    }
                });
                $("#mci-slt-submodulos").val(tempVal).trigger("change");
                $("#mci-slt-items").val(span.attr("data-items").split(",")).trigger("change");
            }

            Swal.close();
            $("#mdl-category-items").modal("show");
        },
        error: function (xhr, status, error) {
            Swal.fire(
                "Error del servidor",
                "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde.",
                "error"
            );
        },
    });
}

//init selects2
function init_select() {
    const sltItems = $("#mci-slt-items");
    sltItems.select2({
        placeholder: "Seleccione acciones",
        width: "100%",
        dropdownParent: $("#mdl-category-items"),
        closeOnSelect: false,
    });

    sltItems.on("change", function (e) {
        setTimeout(() => {
            $(
                ".select2-container--default .select2-selection--multiple .select2-selection__choice"
            ).css({
                "background-color": "var(--primary-color)",
                border: "1px solid var(--primary-color)",
                color: "#fff",
            });
        }, 0);
    });

    const sltSubmodulos = $("#mci-slt-submodulos");
    sltSubmodulos.select2({
        placeholder: "Seleccione acciones",
        width: "100%",
        dropdownParent: $("#mdl-category-items"),
        closeOnSelect: false,
    });

    sltSubmodulos.on("change", function (e) {
        setTimeout(() => {
            $(
                ".select2-container--default .select2-selection--multiple .select2-selection__choice"
            ).css({
                "background-color": "var(--primary-color)",
                border: "1px solid var(--primary-color)",
                color: "#fff",
            });
        }, 0);
    });
}

function deleteNotification(id) {
    Swal.fire({
        title: "¿Estás seguro?",
        text: "Una vez eliminado, no podrás recuperar este registro",
        icon: "warning",
        showCancelButton: true,
        cancelButtonColor: "#d33",
        cancelButtonText: "Cancelar",
        confirmButtonText: "Sí, eliminar",
    }).then((result) => {
        if (!result.isConfirmed) {
            reject("Operación cancelada");
            return;
        }
        swal_wait();
        $.ajax({
            type: "GET",
            url: "/notifications/delete-notification/",
            data: { id: id },
            success: function (result) {
                console.log(result);
                if (result.status == "error") {
                    Swal.fire("Error", result.message, result.status);
                    return;
                }
                table.ajax.reload();
                Swal.fire("", result.message, result.status);
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
}

function swal_wait() {
    Swal.fire({
        title: "Por favor, espera...",
        html: "Estamos procesando tu solicitud. <br/> Esto puede tomar unos segundos...",
        allowOutsideClick: false,
        showConfirmButton: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });
}

function updateNotification(id) {
    let mod = $(`#e-${id} td:eq(1)`).html().replaceAll(" ", "-");

    $("#placeholder-notifications, #placeholder-users").html(null);
    //Check the checkbox if is not CHECKED
    $(`.chbox-${mod}`).prop("checked", true);
    /*Aqui despliego el modal, pero incluyendo toda la información, falta acomodar*/
    mci_selects_all(mod, $(`.chbox-${mod}`).get(0));

    //Prepare new html
    main = $(`#e-${id} td:eq(2)`).html();
    items = $(`#e-${id} td:eq(3)`).html();
    $(`.span__${mod}`).html(`${mod.replaceAll("-", " ")} >> ${main} >> ${items}`);

    if (items.includes(",")) {
        $(`.span__${mod}`).attr("data-items", items.replaceAll("Registros ", "").split(","));
    } else {
        $(`.span__${mod}`).attr("data-items", [0]);
    }

    //Delpoy information to insert the email selected
    let email = $(`#e-${id} td:eq(0)`).html();
    if (!email.includes("@")) {
        email = `area-${email}`;
    }

    let checkbox = $(`input[type="checkbox"][data-email="${email}"]`);
    checkbox.prop("checked", true);
    mci_selects_users(checkbox.get(0));
    mci_selects_items(mod.replaceAll("-", " "));

    //Hide the table and show the create-form
    hideShow("#table-notifications-system", "#forms-notifications-system");
}
