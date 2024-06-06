"use strict";

theme(localStorage.getItem("theme") || "auto");

function detectSystemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
}

function theme(theme = "light") {
    let $html = $("html");
    let themeMode = theme;

    if (theme === "auto") {
        themeMode = detectSystemTheme();
        window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
            const newTheme = e.matches ? "dark" : "light";
            applyTheme(newTheme);
        });
    }

    $html.attr("data-theme", theme);
    $html.attr("data-theme-mode", themeMode);
    $html.attr("data-header-styles", themeMode);
    $html.attr("data-menu-styles", "dark");
    localStorage.setItem("theme", theme);
    localStorage.setItem("theme-mode", themeMode);
}

// Función para congelar de manera profunda
function deepFreeze(obj) {
    // Congela el objeto en el primer nivel
    Object.freeze(obj);

    // Recorre todas las propiedades del objeto
    Object.keys(obj).forEach((prop) => {
        if (typeof obj[prop] === "object" && obj[prop] !== null && !Object.isFrozen(obj[prop])) {
            deepFreeze(obj[prop]); // Congela recursivamente
        }
    });
    return obj;
}
