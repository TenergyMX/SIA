if (window.innerWidth < 992) {
    menu_action("close");
}

$(document).on("click", "[data-bs-toggle='sidebar']", function (event) {
    event.preventDefault();
    let option = $("html").attr("data-toggled");
    let isSmallScreen = $(window).width() < 992;

    menu_action(
        isSmallScreen
            ? option == "close"
                ? "open"
                : "close"
            : option == "icon-overlay-close"
            ? null
            : "icon-overlay-close"
    );
});

$(document).on("click", ".layout-setting", function (event) {
    let tema = $("html").attr("data-theme-mode") == "light" ? "dark" : "light";
    theme(tema);
});

// Función para manejar el clic en el overlay responsivo
$(document).on("click", "#responsive-overlay", function (event) {
    event.preventDefault();
    menu_action("close");
});

// Función para manejar el redimensionamiento de la pantalla
$(window).on("resize", function () {
    let isSmallScreen = $(window).width() < 992;
    menu_action(isSmallScreen ? "close" : null);
});

// Función para manejar las acciones del menú
function menu_action(option) {
    let $overlay = $("#responsive-overlay");
    let $html = $("html");

    $overlay.toggleClass("active", option === "open");
    $html.attr("data-toggled", option);
}
