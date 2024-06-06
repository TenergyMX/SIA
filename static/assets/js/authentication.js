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
