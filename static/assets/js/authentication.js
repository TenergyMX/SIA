"use strict";

// for show password
let createpassword = (type, ele) => {
    let $input = $("#" + type);
    let $icon = $(ele).find("i");

    // Cambiar el tipo de entrada entre "password" y "text"
    $input.attr("type", $input.attr("type") === "password" ? "text" : "password");

    // Cambiar el icono del ojo
    if ($icon.hasClass("fa-eye")) {
        $icon.removeClass("fa-eye").addClass("fa-eye-slash");
    } else {
        $icon.addClass("fa-eye").removeClass("fa-eye-slash");
    }
};

$("form").on("submit", function (e) {
    e.preventDefault();
    var datos = new FormData(this);
    datos.append("redirect", redirect);
    $.ajax({
        type: "POST",
        url: "/user/login/",
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
            console.log(response);
            Swal.fire(
                "Credenciales correctas",
                "Usuario logeado con exito. En un momento sera redireccionado",
                "success"
            );
            setTimeout(function () {
                window.location.href = redirect;
            }, 2500);
        },
        error: function (xhr, status, error) {
            console.error("Error en la petición AJAX:", error);
        },
    });
});
