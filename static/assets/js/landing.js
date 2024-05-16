(function ($) {
    "use strict";

    $(".testimonial-carousel").slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 3000,
        arrows: true,
        dots: false,
        pauseOnHover: false,
        responsive: [
            {
                breakpoint: 768,
                settings: {
                    slidesToShow: 1,
                },
            },
            {
                breakpoint: 520,
                settings: {
                    slidesToShow: 1,
                },
            },
        ],
    });
})(jQuery);

/* back to top */
var $scrollToTop = $(".scrollToTop");

$(window).scroll(function () {
    var scrollTop = $(window).scrollTop();
    var clientHt = $("html")[0].scrollHeight - $("html").height();

    if (scrollTop > 100) {
        $scrollToTop.css("display", "flex");
    } else {
        $scrollToTop.css("display", "none");
    }
});

$scrollToTop.click(function () {
    $("html, body").scrollTop(0);
});

/* back to top */
