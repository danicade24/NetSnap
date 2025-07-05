import psycopg2
import json
import os

#Configuración de la db
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

#Creacion de tablas
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS networks (
            id SERIAL PRIMARY KEY,
            gateway VARCHAR(100) NOT NULL UNIQUE,
            nombre VARCHAR(100),
            descripcion TEXT
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id SERIAL PRIMARY KEY,
            ip VARCHAR(50),
            status VARCHAR(100),
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            datos_json JSONB,
            network_id INTEGER REFERENCES networks(id) ON DELETE SET NULL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS backup_history (
            id SERIAL PRIMARY KEY,
            backup_id INTEGER REFERENCES backups(id) ON DELETE CASCADE,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            datos_json JSONB,
            status VARCHAR(100),
            usuario VARCHAR(100) DEFAULT 'system'
        );
    ''')

    conn.commit()
    cur.close()
    conn.close()

# Guardar o Actualizar Redes
def upsert_network(gateway, nombre=None, descripcion=None):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO networks (gateway, nombre, descripcion)
        VALUES (%s, %s, %s)
        ON CONFLICT (gateway) DO UPDATE SET nombre = EXCLUDED.nombre RETURNING id;
    ''', (gateway, nombre, descripcion))

    network_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return network_id

# Guardar Backup + Auditoría
def save_backup_with_audit(data, usuario='system'):
    conn = get_db_connection()
    cur = conn.cursor()

    gateway = data.get('gateway', 'unknown')
    ip = data.get('ip', 'unknown')
    status = data.get('status', 'unknown')
    datos_json = json.dumps(data)

    network_id = upsert_network(gateway, f'Red {gateway}')

    cur.execute('SELECT id FROM backups WHERE ip = %s;', (ip,))
    existing = cur.fetchone()

    if existing:
        backup_id = existing[0]
        cur.execute('''
            UPDATE backups
            SET status = %s,
                fecha = CURRENT_TIMESTAMP,
                datos_json = %s,
                network_id = %s
            WHERE id = %s;
        ''', (status, datos_json, network_id, backup_id))

    else:
        cur.execute('''
            INSERT INTO backups (ip, status, datos_json, network_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        ''', (ip, status, datos_json, network_id))
        backup_id = cur.fetchone()[0]

    cur.execute('''
        INSERT INTO backup_history (backup_id, datos_json, status, usuario)
        VALUES (%s, %s, %s, %s);
    ''', (backup_id, datos_json, status, usuario))

    conn.commit()
    cur.close()
    conn.close()

# Consultar Backups
def get_all_backups():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT b.id, b.ip, b.status, b.fecha, n.gateway, n.nombre, b.datos_json
        FROM backups b
        LEFT JOIN networks n ON b.network_id = n.id
        ORDER BY b.fecha DESC;
    ''')
    rows = cur.fetchall()

    backups = []
    for row in rows:
        backups.append({
            'backup_id': row[0],
            'ip': row[1],
            'status': row[2],
            'fecha': row[3].isoformat() if row[3] else None,
            'gateway': row[4],
            'nombre_red': row[5],
            'datos': row[6]  
        })

    cur.close()
    conn.close()
    return backups

def get_date_ip(ip):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT fecha FROM backups WHERE ip = %s;', (ip,))
    date = cur.fetchone()

    return date

def get_json_data_from_ip(ip):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT datos_json FROM backups WHERE ip = %s;', (ip,))
    data = cur.fetchone()

    return json.dumps(data)

def get_json_data(ip, date):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT datos_json FROM backups WHERE ip = %s AND fecha = %s;', (ip,date))
    data = cur.fetchone()

    return json.dumps(data)

# Consultar Historial por Backup
def get_backup_history(backup_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT id, fecha, status, usuario, datos_json
        FROM backup_history
        WHERE backup_id = %s
        ORDER BY fecha DESC;
    ''', (backup_id,))
    rows = cur.fetchall()

    history = []
    for row in rows:
        history.append({
            'history_id': row[0],
            'fecha': row[1].isoformat() if row[1] else None,
            'status': row[2],
            'usuario': row[3],
            'datos': row[4]  # JSON completo
        })

    cur.close()
    conn.close()
    return history

# Consultar Historial por IP
def get_backup_history_by_ip(ip):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT h.id, h.fecha, h.status, h.usuario, h.datos_json
        FROM backup_history h
        JOIN backups b ON h.backup_id = b.id
        WHERE b.ip = %s
        ORDER BY h.fecha DESC;
    ''', (ip,))
    rows = cur.fetchall()

    history = []
    for row in rows:
        history.append({
            'history_id': row[0],
            'fecha': row[1].isoformat() if row[1] else None,
            'status': row[2],
            'usuario': row[3],
            'datos': row[4]  # JSON 
        })

    cur.close()
    conn.close()
    return history

def obtener_fechas_por_ip(ip):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT a.fecha
        FROM backup_history a
        JOIN backups b ON a.backup_id = b.id
        WHERE b.ip = %s
        ORDER BY a.fecha DESC;
    ''', (ip,))

    fechas = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return fechas
