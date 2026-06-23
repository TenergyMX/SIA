// INICIALIZAR NAVBAR
function initNavbar() {
    const menuBtn = document.getElementById("menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");
    const menuIcon = document.getElementById("menu-icon");
    const closeIcon = document.getElementById("close-icon");

    // verificar que existan
    if (!menuBtn) return;

    menuBtn.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
        menuIcon.classList.toggle("hidden");
        closeIcon.classList.toggle("hidden");
    });
}

// ANIMACIONES SCROLL
function initScrollAnimations() {
    const sections = document.querySelectorAll(".fade-section");
    const observer = new IntersectionObserver(
        (entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.25,
            rootMargin: "0px 0px -100px 0px",
        }
    );

    sections.forEach((section) => {
        observer.observe(section);
    });
}

// SCROLL SUAVE ENTRE MÓDULOS
function initSmoothModuleScroll() {
    const links = document.querySelectorAll(".nav-scroll");

    links.forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            const targetId = this.getAttribute("href");

            const targetSection = document.querySelector(targetId);

            if (!targetSection) return;

            // reiniciar animación
            targetSection.classList.remove("visible");

            // scroll suave
            targetSection.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });

            // volver a activar animación
            setTimeout(() => {
                targetSection.classList.add("visible");
            }, 400);
        });
    });
}

// RESET FORM

function resetForm() {
    const form = document.getElementById("contact-form");

    const successMessage = document.getElementById("success-message");

    const submitBtn = document.getElementById("submit-btn");

    const btnText = document.getElementById("btn-text");

    successMessage.classList.add("hidden");

    form.classList.remove("hidden");

    submitBtn.disabled = false;

    btnText.innerHTML = `
        <span class="material-icons">
            send
        </span>

        Enviar solicitud
    `;

    form.reset();
}

// APP
async function initApp() {
    console.log("testing 2");
    // iniciar funciones
    initNavbar();

    // iniciar animaciones
    initScrollAnimations();

    initSmoothModuleScroll();
}

// iniciar aplicación
initApp();
