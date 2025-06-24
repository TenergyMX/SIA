$(document).ready(function () {
    $("#vehiclesTable").DataTable({
        order: [
            [0, "desc"],
            [1, "asc"],
        ],
        language: {
            url: "https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json",
        },
        dom:
            "<'row justify-content-between'<'col-md'l><'col-md text-center'B><'col-md'f>>" +
            "<'row mt-2'<'col-md-12'<'table-responsive pb-1'tr>>>" +
            "<'row mt-2 justify-content-between'<'col-md-auto me-auto'i><'col-md-auto ms-auto'p>>",
        buttons: [
            {
                extend: "colvis",
                text: "Columnas",
                className: "btn-sm",
            },
        ],
        initComplete: function (settings, json) {},
    });
});

function handleFormSubmit(event) {
    event.preventDefault();

    /*verified the timelapse it's valid*/
    const startDate = document.querySelector('[name="start_date"]').value;
    const endDate = document.querySelector('[name="end_date"]').value;

    if (!startDate && !endDate) {
        alert("Debes seleccionar una fecha inicial y una fecha final.");
        return;
    }

    if (startDate && endDate && new Date(endDate) < new Date(startDate)) {
        alert("La fecha final no puede ser menor que la fecha inicial.");
        return;
    }

    /*get the information from the form*/
    const formData = new FormData(event.target);

    /*get the vehicles from the table and include in the formdata*/
    let vehicles = [];
    const selectedCheckboxes = document.querySelectorAll(".checkbox-resaltado:checked");
    selectedCheckboxes.forEach((checkbox) => {
        vehicles.push(checkbox.getAttribute("data-vehicle-id"));
    });

    if (vehicles.length == 0) {
        alert("Ningun vehículo fue seleccionado");
        return;
    }

    formData.append("vehicles", vehicles);
    /*before send*/
    Swal.fire({
        title: "Procesando...",
        html: "Espere un momento por favor, mientras procesamos tu peticion",
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
    });

    /*prepare request*/
    fetch("/vehicles/get-statistics/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            $("#chartsContainer").empty();
            console.log(data);
            switch (data.key) {
                case "kilometer-record":
                    chart_line(data, "Kilometros Recorridos", "Vehículos", "Kilometraje");
                    break;
                case "in-out-travels":
                    chart_bar(data, "Entradas y Salidas", "Línea del tiempo", "Salidas");
                    break;
                case "kilometer-record-per-day":
                    chart_line(
                        data,
                        "Kilometros Recorridos por día",
                        "Salídas durante el día",
                        "Kilometraje",
                        " km"
                    );
                    break;
                case "refrendo":
                    chart_bar(data, "REFRENDOS", "Línea de tiempo", "Monto pagado");
                    break;
                case "tenencia":
                    chart_bar(data, "TENENCIA", "Línea de tiempo", "Monto pagado");
                    break;
                case "fuel":
                    title = `Gasolina recargada en lts del ${startDate} al ${endDate}`;
                    chart_bar(data, title, "Carros registrados", "", " lts");
                    break;
                case "verification":
                    chart_line(data, "VERIFICACIÓN", "Semestres registrados", "Monto pagado");
                    break;
                case "insurance":
                    chart_bar(data, "SEGUROS", "", "");
                    break;
                default:
                    break;
            }
            Swal.close();
        })
        .catch((error) => console.error("Error en la solicitud:", error));
}

function chart_line(data, title, x_title = "", y_title = "", ext = "") {
    var options = {
        chart: {
            type: "line",
            height: 350,
        },
        series: data.series,
        xaxis: {
            categories: data.categories,
            title: {
                text: x_title,
                style: {
                    fontSize: "14px",
                    fontWeight: "bold",
                },
            },
        },
        yaxis: {
            title: {
                text: y_title,
                style: {
                    fontSize: "14px",
                    fontWeight: "bold",
                },
            },
        },
        title: {
            text: title,
            align: "center",
        },
    };
    var chart = new ApexCharts(document.querySelector("#chartsContainer"), options);
    chart.render();
}

function chart_bar(data, title, x_title = "", y_title = "", ext = "") {
    var options = {
        chart: {
            type: "bar",
            height: 350,
        },
        series: data.series,
        xaxis: {
            categories: data.categories,
            title: {
                text: x_title,
                style: {
                    fontSize: "14px",
                    fontWeight: "bold",
                },
            },
        },
        yaxis: {
            axisBorder: {
                show: false,
            },
            axisTicks: {
                show: false,
            },
            labels: {
                show: false,
                formatter: function (val) {
                    return val + ext;
                },
            },
            title: {
                text: y_title,
                style: {
                    fontSize: "14px",
                    fontWeight: "bold",
                },
            },
        },
        title: {
            text: title,
            align: "center",
        },
    };

    var chart = new ApexCharts(document.querySelector("#chartsContainer"), options);
    chart.render();
}

function chart_radial_bar(data, title) {
    var options = {
        chart: {
            type: "radialBar",
            height: 350,
        },
        series: data.series,
        labels: data.labels,
        plotOptions: {
            radialBar: {
                min: 0,
                max: 200,
                dataLabels: {
                    value: {
                        formatter: function (val) {
                            return val + " / 200";
                        },
                    },
                },
            },
        },
        title: {
            text: title,
            align: "center",
        },
    };

    var chart = new ApexCharts(document.querySelector("#chartsContainer"), options);
    chart.render();
}

function lf_end_date(event) {
    if (event.target.value == "kilometer-record-per-day") {
        document.querySelector('[name="end_date"]').style.visibility = "hidden";
    } else {
        document.querySelector('[name="end_date"]').style.visibility = "visible";
    }
}
