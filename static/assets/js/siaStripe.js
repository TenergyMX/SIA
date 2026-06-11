class siaStripe {
    constructor() {
        console.log("Constructor ejecutado");

        this.init();
    }

    init() {
        console.log("Init ejecutado");

        this.setEventListeners();
    }

    setEventListeners() {
        console.log("setEventListeners ejecutado");

        this.loadStripe();
        this.submitForm();
    }

    // loadStripe() {
    //     $("a[data-stripe]").each(function () {
    //         $(this).on("click", function (e) {
    //             e.preventDefault();

    //             const company = prompt("Por favor escribe el nombre de tu empresa");
    //             if (!company) return;

    //             const address = prompt("Escribe la dirección de la empresa");
    //             if (!address) return;

    //             const email = prompt("Escribe un correo electrónico válido");
    //             if (!email) return;

    //             console.log("company:", company);
    //             console.log("address:", address);
    //             console.log("email:", email);

    //             const fd = new FormData();
    //             fd.append("plan", this.dataset.stripe);
    //             fd.append("company", company);
    //             fd.append("address", address);
    //             fd.append("email", email);

    //             $.ajax({
    //                 type: "POST",
    //                 url: "/stripe/get-plan/",
    //                 data: fd,
    //                 processData: false,
    //                 contentType: false,
    //                 headers: {
    //                     "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    //                 },
    //                 success: function (r) {
    //                     if ("error" in r) {
    //                         alert(r.error);
    //                     }
    //                     const stripe = Stripe(r.STP_ID);
    //                     stripe.redirectToCheckout({ sessionId: r.id });
    //                 },
    //                 error: function (error) {
    //                     console.log("Error en la solicitud AJAX", error);
    //                 },
    //             });
    //         });
    //     });
    // }

    loadStripe() {
        const modal = document.getElementById("contact-modal");
        const closeBtn = document.getElementById("close-contact-modal");

        document.querySelectorAll(".btn-cotizar").forEach((button) => {
            button.addEventListener("click", function () {
                const planInput = document.getElementById("plan-selected");

                console.log("INPUT ENCONTRADO:", planInput);

                const plan = this.dataset.stripe;

                console.log("PLAN:", plan);

                planInput.value = plan;

                console.log("VALOR GUARDADO:", planInput.value);

                modal.classList.remove("hidden");
            });
        });

        closeBtn.addEventListener("click", function () {
            modal.classList.add("hidden");
        });
    }

    submitForm() {
        console.log("submitForm ejecutado");

        document.addEventListener("submit", function (e) {
            if (e.target.id !== "contact-form") {
                return;
            }

            e.preventDefault();

            console.log("SUBMIT EJECUTADO");

            const form = e.target;
            const fd = new FormData(form);

            for (let pair of fd.entries()) {
                console.log(pair[0], pair[1]);
            }

            console.log("PLAN EN FORM:", form.querySelector('[name="plan"]').value);

            $.ajax({
                type: "POST",
                url: "/stripe/get-plan/",
                data: fd,
                processData: false,
                contentType: false,

                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },

                beforeSend: function () {
                    console.log("ENVIANDO AJAX...");
                },

                success: function (r) {
                    console.log("RESPUESTA:", r);

                    if (r.error) {
                        alert(r.error);
                        return;
                    }

                    const stripe = Stripe(r.STP_ID);

                    stripe.redirectToCheckout({
                        sessionId: r.id,
                    });
                },

                error: function (xhr) {
                    console.log("ERROR AJAX:", xhr);
                    console.log("RESPUESTA:", xhr.responseText);
                },
            });
        });
    }
}

new siaStripe();
