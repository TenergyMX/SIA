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

                const plan = this.dataset.stripe;

                planInput.value = plan;

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
            return;
        }

        // validacion de contraseña
        const password = form.querySelector('[name="password"]');
        const confirm = form.querySelector('[name="password_contact"]');
        const error = document.getElementById("password-error");

        confirm.addEventListener("input", function () {
            if (confirm.value && password.value !== confirm.value) {
                error.classList.remove("hidden");
            } else {
                error.classList.add("hidden");
            }
        });

        form.addEventListener("submit", function (e) {
            e.preventDefault();

            if (password.value !== confirm.value) {
                error.classList.remove("hidden");
                return;
            }

            error.classList.add("hidden");

            const fd = new FormData(form);

            for (let pair of fd.entries()) {
            }

            const csrf = document.querySelector("#checkout-form [name=csrfmiddlewaretoken]");

            if (!csrf) {
                return;
            }

            /**Validar contraseñas*/
            const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]).{8,}$/;
            const validPassword = regex.test(password.value);

            if (!validPassword) {
                Swal.fire(
                    "La contraseña no cumple los requisitos",
                    "Debe tener más de 8 caracteres, incluir al menos una letra mayúscula, un número y un carácter especial.",
                    "error"
                );
                return;
            }

            $.ajax({
                type: "POST",
                url: "/stripe/get-plan/",
                data: fd,
                processData: false,
                contentType: false,

                headers: {
                    "X-CSRFToken": csrf.value,
                },

                beforeSend: function () {},

                success: function (r) {
                    if (r.error) {
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: r.error,
                        });
                        return;
                    }

                    Swal.fire({
                        title: "Redireccionando...",
                        text: "Serás enviado a la plataforma de pago segura de Stripe.",
                        icon: "info",
                        showConfirmButton: false,
                        didOpen: () => {
                            Swal.showLoading();

                            const stripe = Stripe(r.STP_ID);

                            stripe.redirectToCheckout({
                                sessionId: r.id,
                            });
                        },
                    });
                },

                error: function (xhr, status, error) {},

                complete: function () {},
            });
        });
    }
}

new siaStripe();
