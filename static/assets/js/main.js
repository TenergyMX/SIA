"use strict";

if (localStorage.getItem("theme")) {
    theme(localStorage.getItem("theme"));
}

function theme(theme = "light") {
    let $html = $("html");
    $html.attr("data-theme", theme);
    $html.attr("data-theme-mode", theme);
    $html.attr("data-header-styles", theme);
    $html.attr("data-menu-styles", "dark");
    localStorage.setItem("theme", theme);
}
