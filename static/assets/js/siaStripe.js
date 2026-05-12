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

                const company = prompt("Por favor escribe el nombre de tu empresa");
                if (!company) return;

                const address = prompt("Escribe la dirección de la empresa");
                if (!address) return;

                const email = prompt("Escribe un correo electrónico válido");
                if (!email) return;

                console.log("company:", company);
                console.log("address:", address);
                console.log("email:", email);

                const fd = new FormData();
                fd.append("plan", this.dataset.stripe);
                fd.append("company", company);
                fd.append("address", address);
                fd.append("email", email);

                $.ajax({
                    type: "POST",
                    url: "/stripe/get-plan/",
                    data: fd,
                    processData: false,
                    contentType: false,
                    headers: {
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
