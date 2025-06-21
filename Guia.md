## 👥 **Guía Detallada por Roles – Trabajo Independiente en NetSnap**

| Rol | Nombre sugerido         | Responsabilidad                                  |
| --- | ----------------------- | ------------------------------------------------ |
| A   | Automatizador (Ansible) | Conexión a routers y extracción de configuración |
| B   | Backend Developer       | Almacenamiento y lógica API para los backups     |
| C   | Frontend Developer      | Interfaz web y presentación de datos             |

---

### 🛠️ **Integrante A – Automatizador Ansible (dispositivos y extracción)**

✅ **Meta**: Tener un *playbook* funcional que se conecta por SSH a routers virtuales y guarda sus configuraciones localmente.

#### Día 1–2: Simulación de red

* Instala **VirtualBox** y configura **2 routers VyOS**
* En cada router:

  ```bash
  configure
  set service ssh
  set interfaces ethernet eth0 address 192.168.56.101/24  # Router1
  commit; save; exit
  ```

#### Día 3–4: Automatización independiente

* Prepara `inventario.ini`
* Crea y prueba `backup.yml`
* Almacena los `.txt` en una carpeta `backups/` que luego será compartida
* Agrega fecha y nombre del host en el nombre del archivo
* Simula fallos de red para registrar errores

#### Día 5–6: Exportar resultados

* Genera un pequeño script Python para convertir cada archivo `.txt` en un JSON que el backend pueda consumir si se lo pide:

  ```python
  {
    "device": "192.168.56.101",
    "timestamp": "2025-06-20T10:23:00",
    "content": "<configuración aquí>"
  }
  ```

---

### 🧩 **Integrante B – Backend Flask + DB (API REST)**

✅ **Meta**: Tener una API REST completa que reciba backups, los almacene y permita consultar y comparar versiones.

#### Día 1–2: Preparar entorno

* Inicia el proyecto Flask, instala dependencias
* Usa SQLite o PostgreSQL local (tu elección)

#### Día 3–4: Modelo y estructura

* Crea modelo `Backup`
* Genera funciones para guardar backups desde JSON

#### Día 5–6: API REST independiente

* Endpoints:

  * `POST /api/backups` → Guarda backup recibido
  * `GET /api/backups` → Lista todos
  * `GET /api/backups/<id>` → Devuelve contenido
  * `GET /api/backups/<id>/diff` → Devuelve comparación con anterior
* Usa backups simulados desde archivos `.json` de prueba si el integrante A aún no entrega los reales

#### Día 7: Pruebas

* Prueba todo con Postman o `curl`
* Documenta con Swagger o README simple

---

### 🌐 **Integrante C – Frontend Flask + Bootstrap**

✅ **Meta**: Crear un dashboard funcional y atractivo que consulte a la API REST (cuando esté lista) y permita descargar y comparar configuraciones.

#### Día 1–2: Diseño independiente

* Estructura base con Bootstrap y Flask
* Crea plantilla general (`base.html`) con navbar

#### Día 3–4: Mockups y simulación

* Muestra tabla con dispositivos y fechas de respaldo desde un archivo JSON local
* Simula botón de descarga y sección de comparación

#### Día 5–6: Integración flexible

* Usa `fetch()` o `axios` para conectarte a los endpoints reales del backend si ya existen
* Si aún no están, sigue usando tus datos mock

#### Día 7: Enlaces reales

* Muestra backups reales
* Botón para disparar `run-backup` si está disponible (opcional)

---

### ✅ Independencia garantizada:

| Tarea                         | A (Ansible)    | B (Backend) | C (Frontend)   |
| ----------------------------- | -------------- | ----------- | -------------- |
| Simulación de red             | ✔️             | ❌           | ❌              |
| Generar backups               | ✔️             | 🔜          | 🔜             |
| Crear estructura Flask        | ❌              | ✔️          | ✔️             |
| Probar API sin backups reales | ❌              | ✔️          | ✔️ (mock data) |
| Mostrar backups en tabla      | ❌              | ❌           | ✔️             |
| Comparación de versiones      | ✔️ (por línea) | ✔️          | ✔️ (render)    |

---

### 📦 Integración final (Día 8–10)

Cuando cada uno termine su parte:

* **A** comparte los backups
* **B** los carga en la base de datos
* **C** muestra la información desde la API

