$(document).ready(function () {
    setFechaActual();
});

var calendarEl = document.getElementById("calendar2");
var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "es",
    headerToolbar: {
        left: "prev,next,today",
        center: "title",
        right: "dayGridMonth,listMonth",
    },
    buttonText: {
        today: "Hoy",
        month: "Mes",
        week: "Semana",
        day: "Día",
        list: "Lista",
    },
});

calendar.render();

calendar.on("datesSet", function (info) {
    var mes, año;
    if (info.view.type === "listMonth") {
        // Si estamos en la vista de lista, usamos el mes de la primera fecha visible
        mes = info.start.getMonth() + 1;
        año = info.start.getFullYear();
    } else {
        // Si estamos en otra vista, usamos el mes actual
        mes = calendar.getDate().getMonth() + 1;
        año = calendar.getDate().getFullYear();
    }
    obtenerEventos(mes, año);
});

function obtenerEventos(month, year) {
    Swal.fire({
        title: "Procesando...",
        html: "Espere un momento por favor, mientras procesamos tu peticion",
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });
    // ajax
    $.ajax({
        url: "/get-vehicles-calendar/",
        method: "GET",
        data: {
            month: month,
            year: year,
        },
        beforeSend: function () {},
        success: function (response) {
            Swal.close();
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
            // Limpiar el calendario de eventos existentes
            calendar.removeAllEvents();
            // Agregar los nuevos eventos al calendario
            calendar.addEventSource(response.data);
            // Refrescar el calendario para mostrar los cambios
            calendar.render();
        },
        error: function (xhr, status, error) {
            Swal.close();
            let errorMessage = "Ocurrió un error inesperado";
            if (xhr.responseJSON && xhr.responseJSON.message) {
                errorMessage = xhr.responseJSON.message;
            }
            Swal.fire("Error", errorMessage, "error");
            console.log("Error en la petición AJAX:");
            console.error("xhr:", xhr);
        },
    });
}

$("#month").on("change", function (e) {
    var valor = $(this).val();
    var [year, month] = valor.split("-");
    obtenerEventos(parseInt(month), parseInt(year));
    calendar.gotoDate(new Date(parseInt(year), parseInt(month) - 1));
});

function setFechaActual() {
    var fechaActual = new Date();
    var year = fechaActual.getFullYear();
    var month = fechaActual.getMonth() + 1;
    if (month < 10) {
        month = "0" + month; // Agregar un 0 al mes si es menor que 10 para que coincida con el formato YYYY-MM
    }
    var fechaString = year + "-" + month;
    $("#month").val(fechaString).trigger("change");
}
