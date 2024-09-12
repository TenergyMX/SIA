$(document).ready(function () {
    setTimeout(function () {
        getNotifications();
    }, 1500);
});

function hideShow(divToHide, divToShow, options = {}) {
    const defaultOptions = {
        duration: 500,
        easing: "swing", // Puedes cambiar el tipo de easing según lo necesites
        complete: function () {}, // Puedes proporcionar una función de callback opcional
    };

    // Fusionamos las opciones proporcionadas con las opciones por defecto
    const settings = { ...defaultOptions, ...options };

    // Comprobamos si los elementos existen
    const $divToHide = $(divToHide);
    const $divToShow = $(divToShow);
    if (!$divToHide.length || !$divToShow.length) {
        console.error("Los elementos especificados no existen.");
        return;
    }

    // Ocultamos y mostramos los elementos con la animación
    $divToHide.hide(settings);
    $divToShow.show(settings);
}

function sendData(method = "GET", url, data) {
    return new Promise((resolve, reject) => {
        if (method.toLowerCase() === "post") {
            $.ajax({
                type: "POST",
                url: url,
                data: data,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (response.success) {
                        resolve(response);
                    } else {
                        reject(response);
                    }
                },
                error: function (xhr, status, error) {
                    reject(error);
                },
            });
        } else if (method.toLowerCase() === "get") {
            $.ajax({
                type: "GET",
                url: url,
                data: data,
                success: function (response) {
                    resolve(response);
                },
                error: function (xhr, status, error) {
                    reject(error);
                },
            });
        } else {
            reject("Método HTTP no válido. Debe ser 'GET' o 'POST'.");
        }
    });
}

function deleteItem(_url, _data) {
    return new Promise((resolve, reject) => {
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

            $.ajax({
                url: _url,
                method: "POST",
                data: _data,
                processData: false,
                contentType: false,
                success: function (response) {
                    if (!response.success) {
                        console.log(response);
                        if (response.error) {
                            reject(response.error["message"]);
                        } else if (response.warning) {
                            reject(response.warning["message"]);
                        } else {
                            reject("Ocurrió un error inesperado");
                        }
                        return;
                    }
                    resolve("Se ha borrado el registro");
                },
                error: function (xhr, status, error) {
                    console.error(`Error: ${status}, ${error}`);
                    reject(
                        "Se ha producido un problema en el servidor. Por favor, inténtalo de nuevo más tarde."
                    );
                },
            });
        });
    });
}

// Obtener las notificaciones
function getNotifications() {
    $.ajax({
        type: "GET",
        url: "/get-notifications/",
        success: function (response) {
            var contenedor = $("#header-notification-scroll .simplebar-content");
            contenedor.html(null);
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
            } else if (response["recordsTotal"] == 0) {
                $(".empty-item1").removeClass("d-none");
                return;
            }
            $("#notification-icon-badge, #notifiation-data").html(response["recordsTotal"]);
            $(".empty-item1").addClass("d-none");
            $.each(response["data"], function (index, value) {
                contenedor.append(`<li class="dropdown-item">
                    <div class="d-flex align-items-start">
                        <div class="pe-2">
                            <span class="avatar avatar-md bg-${
                                value["alert"]
                            }-transparent avatar-rounded">
                                ${value["icon"]}
                            </span>
                        </div>
                        <div class="flex-grow-1 d-flex align-items-center justify-content-between">
                            <div>
                                <a href="${value["link"] || "#"}" class="mb-0 fw-semibold d-block">
                                    ${value["title"]}
                                </a>
                                <span class="text-muted fw-normal fs-12 header-notification-text">
                                    ${value["text"]}
                                </span>
                            </div>
                            <div></div>
                        </div>
                    </div>
                </li>`);
            });
        },
        error: function (xhr, status, error) {
            console.error("Error en la petición AJAX:", error);
        },
    });
}

function load_vehicles_list() {
    $.ajax({
        type: "GET",
        url: "/get_vehicles_info/",
        data: {
            isList: true,
        },
        beforeSend: function () {},
        success: function (response) {
            console.log(response);
            var select = $("select[name='vehicle_id']");
            $.each(response["data"], function (index, value) {
                select.append(`<option value="${value["id"]}">${value["name"]}</option>`);
            });
            // select.select2();
        },
        error: function (xhr, status, error) {},
    });
}

function load_vehicle_info_card(vehicle_id = 1) {
    $.ajax({
        type: "GET",
        url: "/get_vehicle_info/",
        data: { id: vehicle_id },
        beforeSend: function () {},
        success: function (response) {
            if (!response["success"]) {
                Swal.fire("Oops", "Informacion del vehiculo", "error");
                return false;
            }
            let div = $(".card-vehicle-info");
            let datos = response["data"];
            $.each(datos, function (index, value) {
                div.find(`[data-key-value="${index}"]`).html(value);
            });
            div.find("img").attr("src", datos["image_path"]);
        },
        error: function (xhr, status, error) {},
    });
}

function deepMerge(target, source) {
    for (const key in source) {
        if (source.hasOwnProperty(key)) {
            if (source[key] instanceof Object && !(source[key] instanceof Array)) {
                target[key] = deepMerge(target[key] || {}, source[key]);
            } else {
                target[key] = source[key];
            }
        }
    }
    return target;
}
