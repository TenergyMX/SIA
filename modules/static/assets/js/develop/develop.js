$("#file-header form").on("submit", function (e) {
    e.preventDefault();
    var form = $("#file-header form");
    var url = "/update_records/";
    var datos = new FormData(this);

    $.ajax({
        type: "POST",
        url: url,
        data: datos,
        processData: false,
        contentType: false,
        beforeSend: function () {
            form.find("[type='submit']").prop("disabled", true);
            Swal.fire({
                title: "Procesando...",
                html: "Espere un momento por favor, mientras procesamos tu peticion",
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                },
            });
        },
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
            message = response.message || "Se han guardado los datos con éxito";
            Swal.fire("Éxito", message, "success");

            // Parte dos
            var tbody = $("table#table-consola tbody");
            $.each(response.data, function (index, value) {
                var tr = `
                <tr>
                    <td class="text-${value["status"]} fw-bold">${value["status"]}</td>
                    <td>${value["model"]}</td>
                    <td>${value["message"]}</td>
                </tr>
                `;
                tbody.append(tr);
            });
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
        complete: function (data) {
            form.find("[type='submit']").prop("disabled", false);
        },
    });
});
