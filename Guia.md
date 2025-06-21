## 👥 División de Trabajo por Roles

| Integrante | Rol                    | Responsabilidades                                          |
| ---------- | ---------------------- | ---------------------------------------------------------- |
| **A**      | Ansible y dispositivos | Automatización de backups y conexión con routers virtuales |
| **B**      | Backend (Flask + DB)   | API REST, base de datos, y lógica de auditoría             |
| **C**      | Frontend (Web)         | Dashboard web con Bootstrap, visualización y descargas     |

---

## 📅 Guía Paso a Paso – Proyecto NetSnap (con VirtualBox)

---

### 🗂️ **Día 1 – Preparación inicial (Todos)**

**Todos:**

* Revisión de objetivos, división de tareas, elección de VyOS en VirtualBox como entorno.
* Diagrama del sistema:
  `Ansible ←→ Routers` ↔ `Flask API` ↔ `Base de datos` ↔ `Dashboard web`

**A** instala y configura:

* VirtualBox + VyOS (o CSR1000v)
* Habilita interfaz y SSH:

  ```bash
  set interfaces ethernet eth0 address 192.168.56.101/24
  set service ssh
  commit; save; exit
  ```

**B** instala:

* Python 3, Flask, SQLAlchemy, SQLite/PostgreSQL

**C** prepara:

* Bootstrap 5 y diseño del dashboard inicial (`base.html`)

---

### ⚙️ **Día 2–3 – Automatización con Ansible (Responsable: A)**

#### **A:**

1. Crear archivo `inventario.ini`
2. Escribir playbook `backup.yml`:

   ```yaml
   - name: Obtener configuración
     hosts: routers
     tasks:
       - name: Ejecutar show configuration
         ansible.netcommon.cli_command:
           command: show configuration
         register: config_output
       - name: Guardar
         copy:
           content: "{{ config_output.stdout }}"
           dest: "backups/{{ inventory_hostname }}_{{ ansible_date_time.iso8601 }}.txt"
   ```
3. Probar conexión:

   ```bash
   ansible -i inventario.ini routers -m ping
   ansible-playbook -i inventario.ini backup.yml
   ```
4. Guardar backups en carpeta compartida `backups/`

---

### 🖥️ **Día 4 – Backend inicial (Responsable: B)**

#### **B:**

1. Crear estructura:

   ```
   netsnap/
   ├── app.py
   ├── config.py
   ├── models.py
   ├── backups/
   ```
2. Crear modelo Backup:

   ```python
   class Backup(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       device = db.Column(db.String(100))
       timestamp = db.Column(db.DateTime)
       content = db.Column(db.Text)
   ```
3. Inicializar base de datos y conexión

---

### 🔌 **Día 5 – API REST (Responsable: B)**

#### **B:**

1. Crear rutas:

   * `GET /api/backups`: lista de backups
   * `POST /api/backups`: registrar backup
   * `GET /api/backups/<id>/diff`: ver diferencias

2. Probar con `curl` o Postman

---

### 🌐 **Día 6–7 – Interfaz Web (Responsable: C)**

#### **C:**

1. Diseñar interfaz con Bootstrap
2. Crear vistas:

   * Lista de backups (`backups.html`)
   * Comparación de backups
   * Botón para "Ejecutar respaldo"
3. Conectarse a API REST del backend

---

### 🔄 **Día 8 – Integración de todo (Todos)**

#### **A**:

* Expone ejecución del playbook desde Flask:

  ```python
  subprocess.run(["ansible-playbook", "backup.yml", "-i", "inventario.ini"])
  ```

#### **B**:

* Conecta llamada desde frontend → API → ejecución del backup
* Asegura que los nuevos backups se guarden en DB

#### **C**:

* Muestra mensajes de éxito o error en el dashboard
* Permite ver comparación de configuraciones

---

### 🧪 **Día 9 – Pruebas y documentación (Todos)**

#### **A**:

* Simula errores de conexión, prueba dispositivos caídos

#### **B**:

* Documenta endpoints de API, pruebas unitarias

#### **C**:

* Captura pantallas, documenta interfaz

---

### 🎤 **Día 10 – Presentación y entrega (Todos)**

* Preparan presentación:

  * Diagrama general
  * Demo (video o en vivo)
  * GitHub completo:

    * `README.md`
    * Instrucciones de ejecución:

      ```bash
      python -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      flask run
      ```
