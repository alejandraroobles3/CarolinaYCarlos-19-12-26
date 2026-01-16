// Fade-in al cargar la página
document.addEventListener("DOMContentLoaded", function() {
    const body = document.body;
    setTimeout(() => body.classList.add("visible"), 10);


    document.querySelectorAll('.mi-toggle-title').forEach(title => {
    title.addEventListener('click', () => {
    const content = title.nextElementSibling;
    const icon = title.querySelector('.icon');
    if (content.style.display === 'none') {
      content.style.display = 'block';
      icon.textContent = '▲';
    } else {
      content.style.display = 'none';
      icon.textContent = '▼';
    }
        });
    });

    const toggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    toggleInvitados(true);

    toggle.addEventListener('click', () => {
    navLinks.classList.toggle('show');
    });

    const fileInput = document.getElementById("file-input");
    const fileName = document.getElementById("file-name");

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
        } else {
        fileName.textContent = "Ningún archivo seleccionado";
        }
    });


});




