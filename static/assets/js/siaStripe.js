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
                const planInput = document.getElementById("checkout-plan");

                console.log("INPUT PLAN:", planInput);

                const plan = this.dataset.stripe;

                planInput.value = plan;

                console.log("PLAN GUARDADO:", planInput.value);

                modal.classList.remove("hidden");
            });
        });

        closeBtn.addEventListener("click", function () {
            modal.classList.add("hidden");
        });
    }

    submitForm() {
        console.log("submitForm ejecutado");

        const form = document.getElementById("checkout-form");

        if (!form) {
            console.log("❌ No existe checkout-form");
            return;
        }

        // validacion de contraseña
        const password = form.querySelector('[name="password"]');
        const confirm = form.querySelector('[name="password_contact"]');
        const error = document.getElementById("password-error");

        console.log("password:", password.value);
        console.log("confirm:", confirm.value);

        confirm.addEventListener("input", function () {
            if (confirm.value && password.value !== confirm.value) {
                error.classList.remove("hidden");
            } else {
                error.classList.add("hidden");
            }
        });

        console.log("✅ FORM ENCONTRADO:", form);

        form.addEventListener("submit", function (e) {
            console.log("🚀 SUBMIT DETECTADO");

            e.preventDefault();

            if (password.value !== confirm.value) {
                error.classList.remove("hidden");
                return;
            }

            error.classList.add("hidden");

            console.log("✅ preventDefault ejecutado");

            const fd = new FormData(form);

            console.log("📋 PLAN:", fd.get("plan"));

            console.log("📋 DATOS DEL FORM:");
            for (let pair of fd.entries()) {
                console.log(pair[0], pair[1]);
            }

            const csrf = document.querySelector("#checkout-form [name=csrfmiddlewaretoken]");

            console.log("🔐 CSRF:", csrf);

            if (!csrf) {
                console.log("❌ No se encontró el CSRF");
                return;
            }

            console.log("📡 ANTES DEL AJAX");

            $.ajax({
                type: "POST",
                url: "/stripe/get-plan/",
                data: fd,
                processData: false,
                contentType: false,

                headers: {
                    "X-CSRFToken": csrf.value,
                },

                beforeSend: function () {
                    console.log("📤 ENVIANDO AJAX...");
                },

                success: function (r) {
                    console.log("✅ AJAX SUCCESS");
                    console.log("RESPUESTA:", r);

                    if (r.error) {
                        console.log("❌ ERROR DEVUELTO:", r.error);
                        alert(r.error);
                        return;
                    }

                    console.log("✅ CREANDO INSTANCIA STRIPE");

                    const stripe = Stripe(r.STP_ID);

                    console.log("✅ REDIRECCIONANDO A CHECKOUT");

                    stripe.redirectToCheckout({
                        sessionId: r.id,
                    });
                },

                error: function (xhr, status, error) {
                    console.log("❌ AJAX ERROR");
                    console.log("STATUS:", status);
                    console.log("ERROR:", error);
                    console.log("RESPONSE:", xhr.responseText);
                },

                complete: function () {
                    console.log("🏁 AJAX FINALIZADO");
                },
            });
        });

        console.log("✅ EVENTO SUBMIT REGISTRADO");
    }
}

new siaStripe();
