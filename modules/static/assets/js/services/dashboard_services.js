$(document).ready(function () {
    contadoresDashboard(); //contadores
    graficaEgresos(); //grafica principal
    get_service_dashboard(); //servicios
    get_services_provider(); //proveedores
    get_services_locations(); //ubicaciones
    graficas_filtros(); //mostrar las graficas
});

function graficas_filtros() {
    aplicarFiltrosCombinados();
}

// Función para cargar los datos de los contadores en el dashboard
function contadoresDashboard() {
    $.ajax({
        url: "/get_dashboard_data/",
        type: "GET",
        success: function (response) {
            if (response.status === "success") {
                // Actualizar el total de servicios
                $("#servicesTotal").text(response.data.total_services);

                // Actualizar el total de egresos
                var totalEgresos = parseFloat(response.data.total_egresos);
                if (!isNaN(totalEgresos)) {
                    $("#egresosTotal").text(totalEgresos.toFixed(2));
                } else {
                    $("#egresosTotal").text("0.00");
                }

                // Actualizar el total de pagos no pagados
                $("#paymentsTotal").text(response.data.total_non_paid_payments);
            } else {
                console.error("Error al obtener los datos del dashboard:", response.message);
            }
        },
        error: function (xhr, status, error) {
            console.error("Error en la llamada AJAX:", error);
        },
    });
}

// Función para cargar la gráfica
function graficaEgresos() {
    $.ajax({
        url: "/get_dashboard_grafica/",
        type: "GET",
        success: function (response) {
            if (response.status === "success") {
                var categories = [];
                var payments = [];

                response.data.forEach(function (item) {
                    categories.push(item.category);
                    payments.push(Number(item.total_payment));
                });

                if (typeof graficaEgresos !== "undefined") {
                    graficaEgresos.destroy();
                }

                var canvas = document.getElementById("graficaEgresos");
                var container = canvas.parentElement;

                var containerWidth = container.offsetWidth;
                var containerHeight = container.offsetHeight;

                canvas.width = containerWidth * 0.6;
                canvas.height = containerHeight * 0.6;

                canvas.style.marginLeft = (containerWidth - canvas.width) / 2 + "px";
                canvas.style.marginTop = (containerHeight - canvas.height) / 2 + "px";

                // Crear la gráfica
                var ctx = canvas.getContext("2d");
                var graficaEgresos = new Chart(ctx, {
                    type: "pie",
                    data: {
                        labels: categories,
                        datasets: [
                            {
                                label: "Total de Egresos por Categoría",
                                data: payments,
                                backgroundColor: [
                                    "#a5c334",
                                    "#2CB2F5",
                                    "#E24747",
                                    "#EED675",
                                    "#F2B252",
                                ],
                                borderColor: "#fff",
                                borderWidth: 2,
                                fill: true,
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: "top",
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        var value = tooltipItem.raw;
                                        if (typeof value === "number" && !isNaN(value)) {
                                            return "$" + value.toFixed(2);
                                        } else {
                                            return "$0.00";
                                        }
                                    },
                                },
                            },
                        },
                    },
                });
            } else {
                console.error("Error al obtener los datos para la gráfica:", response.message);
            }
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        },
    });
}

// Función para cargar las categorías en el select
function get_service_dashboard(selectedCategoryId) {
    $.ajax({
        url: "/get_services_categories/",
        type: "GET",
        success: function (response) {
            var select = $("#category");
            select.html(null);
            select.append("<option value=''>Seleccione una categoría</option>");

            $.each(response.data, function (index, value) {
                var selected = value.id == selectedCategoryId ? "selected" : "";
                select.append(
                    `<option value="${value.id}" ${selected}>${value.name_category}</option>`
                );
            });
        },
        error: function (error) {
            console.error("Error al cargar categorías:", error);
            alert("Hubo un error al cargar las categorías.");
        },
    });
}

//Función para cargar los nombres de los proveedores han sido registrados
function get_services_provider(selectedProviderId) {
    $.ajax({
        url: "/get_services_providers/",
        type: "GET",
        success: function (response) {
            var select = $("#provider_services");
            select.html("<option value=''>Seleccione proveedor</option>");
            $.each(response.data, function (index, provider) {
                var selected = provider.id == selectedProviderId ? "selected" : "";
                select.append(
                    `<option value="${provider.id}" ${selected}>${provider.name}</option>`
                );
            });
            select.val(selectedProviderId);
        },
        error: function (error) {
            console.error("Error al cargar los proveedores:", error);
            alert("Hubo un error al cargar los proveedores.");
        },
    });
}

//funcion para mostrar las opciones en el select al momento de cargar el modal para agregar una nueva ubicacion
function get_services_locations(selectedLocationId) {
    $.ajax({
        url: "/get_services_locations/",
        type: "GET",
        success: function (response) {
            const select = $("#ubication_services");
            select.empty(); // Limpia correctamente
            select.html("<option value=''>Seleccione una ubicación</option>");

            $.each(response.data, function (index, value) {
                const selected = value.id == selectedLocationId ? "selected" : "";
                select.append(`<option value="${value.id}" ${selected}>${value.name}</option>`);
            });
            select.val(selectedLocationId);
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar las ubicaciones:", error);
            alert("Hubo un error al cargar las ubicaciones. Inténtelo de nuevo más tarde.");
        },
    });
}

function hideGraphics() {
    $("#graficaFiltradaContainer").hide();
}

function aplicarFiltrosCombinados() {
    const categoryId = $("#category").val();
    const providerId = $("#provider_services").val();
    const locationId = $("#ubication_services").val();
    const startDate = $("#start_date_service").val();
    const endDate = $("#end_date_service").val();

    // Si todos los filtros están vacíos, no mostrar nada
    if (!categoryId && !providerId && !locationId && !startDate && !endDate) {
        $("#graficaFiltradaContainer").hide();
        return;
    }

    hideGraphics(); // Oculta otras gráficas si las hubiera
    $("#graficaFiltradaContainer").show();

    $.ajax({
        url: "/get_services_filtered/",
        type: "GET",
        data: {
            category_id: categoryId,
            provider_id: providerId,
            location_id: locationId,
            start_date: startDate,
            end_date: endDate,
        },
        success: function (response) {
            if (response.status === "success") {
                var serviceNames = [];
                var payments = [];

                response.data.forEach(function (item) {
                    serviceNames.push(item.service_name);
                    payments.push(Number(item.total_payment));
                });

                // Si no hay resultados, ocultar gráfica
                if (serviceNames.length === 0) {
                    if (
                        typeof graficaEgresosFiltradaInstance !== "undefined" &&
                        graficaEgresosFiltradaInstance !== null
                    ) {
                        graficaEgresosFiltradaInstance.destroy();
                    }

                    // Mostrar el contenedor, ocultar canvas y mostrar mensaje
                    $("#graficaFiltradaContainer").show();
                    $("#graficaEgresosFiltrada").hide();
                    $("#mensajeSinDatos").show();
                    $("#tituloGraficaFiltrada").text("Gráfica por combinación de filtros");
                    return;
                }
                $("#graficaEgresosFiltrada").show();
                $("#mensajeSinDatos").hide();
                var ctx = document.getElementById("graficaEgresosFiltrada").getContext("2d");

                if (
                    typeof graficaEgresosFiltradaInstance !== "undefined" &&
                    graficaEgresosFiltradaInstance !== null
                ) {
                    graficaEgresosFiltradaInstance.destroy();
                }

                graficaEgresosFiltradaInstance = new Chart(ctx, {
                    type: "bar",
                    data: {
                        labels: serviceNames,
                        datasets: [
                            {
                                label: "Egresos por Servicio (Filtros combinados)",
                                data: payments,
                                backgroundColor: "#8E44AD",
                                borderColor: "#6C3483",
                                borderWidth: 2,
                                fill: true,
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: "top" },
                            tooltip: {
                                callbacks: {
                                    label: function (tooltipItem) {
                                        return "$" + tooltipItem.raw.toFixed(2);
                                    },
                                },
                            },
                        },
                    },
                });
            } else {
                console.error("Error:", response.message);
            }
        },
        error: function (xhr, status, error) {
            console.error("Error AJAX:", error);
        },
    });
}

$("#category, #provider_services, #ubication_services, #start_date_service, #end_date_service").on(
    "change",
    function () {
        aplicarFiltrosCombinados();
    }
);
