document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ NetSnap iniciado");

  fetch("../templates/navbar.html")
    .then(res => res.text())
    .then(html => {
      document.getElementById("navbar-container").innerHTML = html;
      inicializarNavegacion();
    })
    .catch(err => console.error("Error al cargar navbar:", err));

  cargarVista("main.html"); // Principal
});

function inicializarNavegacion() {
  const links = document.querySelectorAll('a[data-page]');
  links.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      const page = link.getAttribute("data-page");

      cargarVista(page)
    });
  });
}


function cargarVista(nombreVista) {
  const ruta = `../templates/${nombreVista}`;

  return fetch(ruta)
    .then(res => {
      if (!res.ok) throw new Error(`Error al cargar ${ruta}`);
      return res.text();
    })
    .then(html => {
      document.getElementById("main-container").innerHTML = html;

      switch (nombreVista) {
        case "main.html":
          cargarIP();
          break;
        case "components/backups.html":
          cargarDispositivos();
          break;
        case "components/auditoria.html":
          cargarAuditoria();
          break;
        default:
          console.warn(`No hay scripts específicos para ${nombreVista}`);
      }
    })
    .catch(err => {
      console.error("Error al cargar vista:", err);
      document.getElementById("main-container").innerHTML =
        `<div class="alert alert-danger">No se pudo cargar la vista: ${nombreVista}</div>`;
    });
}


function cargarIP() {
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

function cargarDispositivos() {
  console.log("Cargando dispositivos...");
  fetch("http://localhost:5000/devices")
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById("tabla-dispositivos");
      if (!tbody) {
        console.warn("No se encontró la tabla de dispositivos.");
        return;
      }

      tbody.innerHTML = "";
      data.devices.forEach(device => {
        const row = document.createElement("tr");

        const badgeClass = device.state === "up" ? "bg-success" : "bg-danger";
        const disabled = device.ssh === false ? "bg-danger" : "bg-success";
        const disabled_date = device.ssh === false ? "disabled" : "";

        row.innerHTML = `
          <td>${device.hostname}</td>
          <td>${device.ip}</td>
          <td>${device.date}</td>
          <td><span class="badge ${badgeClass}">${device.state}</span></td>
          <td><span class="badge ${disabled}">${device.ssh}</span></td>
          <td><button class="btn btn-sm btn-outline-primary descargar-btn" ${disabled_date}>Descargar</button></td>
          <td><button class="btn btn-sm btn-outline-secondary backup-btn" ${disabled_date}>Backup</button></td>
        `;

        tbody.appendChild(row);

        // Botón Descargar
        const botonDescargar = row.querySelector('.descargar-btn');
        if (botonDescargar) {
          botonDescargar.addEventListener('click', () => {
            descargarBackup(device.ip);
          });
        }

        // Botón Backup
        const botonBackup = row.querySelector('.backup-btn');
        botonBackup.addEventListener('click', async () => {
          try {
            botonBackup.disabled = true;
            botonBackup.innerText = "Procesando...";
            
            await generarBackup(device.ip);
            await cargarDispositivos();
            
          } catch (error) {
            console.error("Error en backup o recarga:", error);
          } finally {
            botonBackup.disabled = false;
            botonBackup.innerText = "Backup";
          }
        });
      });
    })
    .catch(error => {
      console.error("Error al obtener los dispositivos:", error);
      const tbody = document.getElementById("tabla-dispositivos");
      if (tbody) {
        tbody.innerHTML = "<tr><td colspan='6'>No se pudo cargar la información</td></tr>";
      }
    });
}

function cargarAuditoria() {
  console.log("🔍 Cargando datos de auditoría...");
  //container.innerHTML = ""
  fetch("http://localhost:5000/devices")
  .then(response => response.json())
  .then(data => {
    const devices = data.devices;

    // Hacemos un array de promesas para obtener fechas por IP
    const promesasFechas = devices.map(device => {
      return fetch("http://localhost:5000/backup-dates", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ ip: device.ip })
      })
        .then(res => res.json())
        .then(fechaData => {
          device.fechas = fechaData.fechas || [];  
          return device;
        })
        .catch(err => {
          console.error(`Error obteniendo fechas para ${device.ip}:`, err);
          device.fechas = [];
          return device;
        });
    });

    // Esperamos a que todas las fechas se hayan cargado
    Promise.all(promesasFechas).then(devicesConFechas => {
      console.log("Todos los dispositivos con sus fechas:", devicesConFechas);

      // Aquí haces el render de la tabla, por ejemplo:
      renderizarTabla(devicesConFechas);
    });
  })
  .catch(err => {
    console.error("Error al obtener dispositivos:", err);
  });


}

function renderizarTabla(devices) {
  const contenedor = document.getElementById("tabla-dispositivos");
  if (!contenedor) {
    console.warn("❗ No se encontró el contenedor #tabla-dispositivos.");
    return;
  }
  contenedor.innerHTML = "";

  const lista = document.createElement("div");
  lista.className = "list-group shadow-sm";

  devices.forEach(device => {
    const nombre = device.hostname || "Desconocido";
    const fecha = device.fechas.length > 0 ? device.fechas[0] : "Sin backups";
    const mensaje = device.fechas.length > 0 ? "Backup reciente disponible." : "Sin backups previos.";
    const hayCambios = device.fechas.length > 0;

    const bloque = crearBloqueAuditoria({
      nombre: `${nombre} (${device.ip})`,
      fecha: fecha,
      mensaje: mensaje,
      hayCambios: hayCambios,
      fechas: device.fechas,
      ip: device.ip
    });

    lista.appendChild(bloque);
  });

  contenedor.appendChild(lista);
}

function crearBloqueAuditoria({ nombre, fecha, mensaje, hayCambios, fechas = [], ip }) {
  const div = document.createElement("div");
  div.className = `list-group-item list-group-item-action ${hayCambios ? "" : "bg-light"}`;

  let botonesFechas = "";
  if (hayCambios) {
    botonesFechas = fechas.map((f, idx) => 
      `<button class="btn btn-sm btn-outline-info me-1 fecha-btn" data-idx="${idx}" data-ip="${ip}">${f}</button>`
    ).join("");
  }

  div.innerHTML = `
    <div class="d-flex w-100 justify-content-between">
      <h5 class="mb-1 fw-bold ${hayCambios ? "text-dark" : ""}">${nombre}</h5>
      <small class="text-muted">${fecha}</small>
    </div>
    <p class="mb-2 ${hayCambios ? "" : "text-muted"}">${mensaje}</p>
    ${hayCambios ? `<div class="mt-2">${botonesFechas}</div>` : ""}
  `;

  if (hayCambios) {
    const botones = div.querySelectorAll('.fecha-btn');
    let seleccionadas = [];

    botones.forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-idx'));
        const ipBtn = btn.getAttribute('data-ip');

        // Toggle selección visual
        btn.classList.toggle('active');

        if (btn.classList.contains('active')) {
          seleccionadas.push(idx);
        } else {
          seleccionadas = seleccionadas.filter(i => i !== idx);
        }

        // Mantener solo dos seleccionadas
        if (seleccionadas.length > 2) {
          const firstIdx = seleccionadas.shift();
          botones[firstIdx].classList.remove('active');
        }

        if (seleccionadas.length === 2) {
          console.log(`🔍 Auditando ${ipBtn} entre fechas [${seleccionadas.join(", ")}]`);

          auditarCambios(ipBtn, seleccionadas);
        }
      });
    });
  }

  return div;
}

function auditarCambios(ip, indices) {
  fetch("http://localhost:5000/auditar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ip: ip, indices: indices })
  })
  .then(res => res.json())
  .then(data => {
    console.log("Auditoría:", data);
    alert(`Auditoría completada para ${ip}`);
    alert(data.diferencias)
    console.log(data.diferencias)
  })
  .catch(err => {
    console.error("Error en auditoría:", err);
    alert("Error al auditar cambios.");
  });
}

function descargarBackup(ip) {
  fetch("http://localhost:5000/file-data", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ ip: ip })  
  })
    .then(res => {
      if (!res.ok) throw new Error("Error en la respuesta del servidor");
      return res.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `datos_${ip}.json`;  // ⬅ Nombre acorde al backend
      document.body.appendChild(a);
      a.click();
      a.remove();
    })
    .catch(err => console.error("❌ Error al descargar:", err));
}

function generarBackup(ip) {
  fetch("http://localhost:5000/backup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ips: [ip] })  // Enviamos un array como espera el servidor
  })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
      if (status === 200) {
        alert(`✅ Backup exitoso para ${ip}`);
        console.log(body);
      } else {
        alert(`⚠️ Backup con errores para ${ip}`);
        console.error(body);
      }
    })
    .catch(err => {
      alert(`❌ Error al generar backup para ${ip}`);
      console.error(err);
    });
}

