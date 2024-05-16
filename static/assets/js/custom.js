(function () {
    "use strict";

    /* page loader */
    function hideLoader() {
        const loader = document.getElementById("loader");
        loader.classList.add("d-none");
    }

    window.addEventListener("load", hideLoader);
    /* page loader */

    /* footer year */
    document.getElementById("year").innerHTML = new Date().getFullYear();
    /* footer year */

    /* count-up */
    var i = 1;
    setInterval(() => {
        document.querySelectorAll(".count-up").forEach((ele) => {
            if (ele.getAttribute("data-count") >= i) {
                i = i + 1;
                ele.innerText = i;
            }
        });
    }, 10);
    /* count-up */

    /* back to top */
    const scrollToTop = document.querySelector(".scrollToTop");
    const $rootElement = document.documentElement;
    const $body = document.body;
    window.onscroll = () => {
        const scrollTop = window.scrollY || window.pageYOffset;
        const clientHt = $rootElement.scrollHeight - $rootElement.clientHeight;
        if (window.scrollY > 100) {
            scrollToTop.style.display = "flex";
        } else {
            scrollToTop.style.display = "none";
        }
    };
    scrollToTop.onclick = () => {
        window.scrollTo(0, 0);
    };
    /* back to top */

    /* header dropdowns scroll */
    var myHeadernotification = document.getElementById("header-notification-scroll");
    new SimpleBar(myHeadernotification, { autoHide: true });
    /* header dropdowns scroll */
})();

/* full screen */
var elem = document.documentElement;
function openFullscreen() {
    let open = document.querySelector(".full-screen-open");
    let close = document.querySelector(".full-screen-close");

    if (
        !document.fullscreenElement &&
        !document.webkitFullscreenElement &&
        !document.msFullscreenElement
    ) {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
            /* Safari */
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
            /* IE11 */
            elem.msRequestFullscreen();
        }
        close.classList.add("d-block");
        close.classList.remove("d-none");
        open.classList.add("d-none");
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            /* Safari */
            document.webkitExitFullscreen();
            console.log("working");
        } else if (document.msExitFullscreen) {
            /* IE11 */
            document.msExitFullscreen();
        }
        close.classList.remove("d-block");
        open.classList.remove("d-none");
        close.classList.add("d-none");
        open.classList.add("d-block");
    }
}
/* full screen */

/* toggle switches */
let customSwitch = document.querySelectorAll(".toggle");
customSwitch.forEach((e) =>
    e.addEventListener("click", () => {
        e.classList.toggle("on");
    })
);
/* toggle switches */
