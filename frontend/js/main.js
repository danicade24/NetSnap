document.addEventListener("DOMContentLoaded", () => {
  // Cargar navbar desde templates/
  fetch("../templates/navbar.html")
    .then(res => res.text())
    .then(html => {
      document.getElementById("navbar-container").innerHTML = html;
      inicializarNavegacion();
    });

  // Cargar vista principal (main.html)
  cargarVista("main.html");
});

function inicializarNavegacion() {
  const links = document.querySelectorAll('a[data-page]');
  links.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      const page = link.getAttribute("data-page");
      cargarVista(page);
    });
  });
}

function cargarVista(nombreVista) {
  const ruta = `../templates/${nombreVista}`;

  fetch(ruta)
    .then(res => {
      if (!res.ok) throw new Error(`Error al cargar ${ruta}`);
      return res.text();
    })
    .then(html => {
      document.getElementById("main-container").innerHTML = html;

      // Mostrar IP solo en la vista principal
      if (nombreVista === "main.html") {
        fetch("http://localhost:5000/ip")
          .then(res => res.json())
          .then(data => {
            const ipEl = document.getElementById("ip-local");
            if (ipEl) ipEl.textContent = data.ip;
          })
          .catch(() => {
            const ipEl = document.getElementById("ip-local");
            if (ipEl) ipEl.textContent = "No disponible";
          });
      }
    })
    .catch(err => {
      console.error(err);
      document.getElementById("main-container").innerHTML =
        `<div class="alert alert-danger">No se pudo cargar la vista: ${nombreVista}</div>`;
    });
}
