class siaStripe {
    constructor() {
        this.init();
    }

    init() {
        this.setEventListeners();
    }

    setEventListeners() {
        this.loadStripe();
    }

    loadStripe() {
        $("a[data-stripe]").each(function () {
            $(this).on("click", function (e) {
                e.preventDefault();
                const fd = new FormData();
                fd.append("plan", this.dataset.stripe);
                fd.append("company", prompt("Por favor escribe el nombre de tu empresa"));
                fd.append("address", prompt("Escribe la dirección de la empresa"));
                fd.append("email", prompt("Escribe un correo electrónico válido"));

                $.ajax({
                    type: "POST",
                    url: "/stripe/get-plan/",
                    data: fd,
                    processData: false,
                    contentType: false,
                    header: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                    },
                    success: function (r) {
                        if ("error" in r) {
                            alert(r.error);
                        }
                        const stripe = Stripe(r.STP_ID);
                        stripe.redirectToCheckout({ sessionId: r.id });
                    },
                    error: function (error) {
                        console.log("Error en la solicitud AJAX", error);
                    },
                });
            });
        });
    }
}
