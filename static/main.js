// Fade-in al cargar la página
document.addEventListener("DOMContentLoaded", function() {
    const body = document.body;
    setTimeout(() => body.classList.add("visible"), 10);

    const toggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    toggle.addEventListener('click', () => {
        navLinks.classList.toggle('show');
    });

});




