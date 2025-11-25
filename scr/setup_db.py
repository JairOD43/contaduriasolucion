# setup_db.py  ←  REEMPLAZA COMPLETAMENTE TU ARCHIVO CON ESTE
import mysql.connector
from mysql.connector import Error

# Tus datos reales de MySQL (cámbialos si es necesario)
HOST = "localhost"
USER = "root"
PASSWORD = "root1"        # ← Pon aquí tu contraseña real de MySQL (si no tiene, déjalo como "")
PORT = 3306

try:
    # 1. Conexión SIN especificar base de datos
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    cur = conn.cursor()

    print("Conexión exitosa a MySQL")

    # 2. Crear la base de datos
    cur.execute("CREATE DATABASE IF NOT EXISTS contabilidad_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cur.execute("USE contabilidad_db")
    print("Base de datos contabilidad_db creada o ya existe")

    # 3. Crear tablas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL UNIQUE,
        role VARCHAR(50) DEFAULT 'cliente',
        password VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        rfc VARCHAR(20) UNIQUE,
        regimen_fiscal VARCHAR(100) DEFAULT 'Régimen General',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transacciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id INT NOT NULL,
        fecha DATE DEFAULT '2025-01-01',
        concepto TEXT NOT NULL,
        monto DECIMAL(15,2) NOT NULL,
        tipo_transaccion ENUM('ingreso', 'gasto') NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """)

    # 4. Usuario admin por defecto
    from hashlib import sha256
    admin_pass = sha256("admin123".encode()).hexdigest()
    cur.execute("""
    INSERT IGNORE INTO usuarios (nombre, role, password) 
    VALUES ('admin', 'admin', %s)
    """, (admin_pass,))

    # 5. Cliente y transacciones de prueba (para que veas el CU-12 funcionando)
    cur.execute("INSERT IGNORE INTO clientes (nombre, rfc) VALUES ('ACME SA de CV', 'ACM201122ABC')")
    cur.execute("SELECT id FROM clientes WHERE nombre = 'ACME SA de CV'")
    cliente_id = cur.fetchone()[0]

    transacciones = [
        (cliente_id, '2025-01-10', 'Venta grande sin CFDI', 850000.00, 'ingreso'),
        (cliente_id, '2025-01-20', 'Cena con amigos', 12000.00, 'gasto'),
        (cliente_id, '2025-02-01', 'Honorarios', 450000.00, 'ingreso'),
        (cliente_id, '2025-02-15', 'Ingreso sospechoso', 1200000.00, 'ingreso'),
    ]
    cur.executemany("""
        INSERT INTO transacciones (cliente_id, fecha, concepto, monto, tipo_transaccion) 
        VALUES (%s, %s, %s, %s, %s)
    """, transacciones)

    conn.commit()
    print("¡TODO LISTO!")
    print("Usuario: admin")
    print("Contraseña: admin123")
    print("Ahora ejecuta: python execute.py")

except Error as e:
    print(f"Error de MySQL: {e}")
    if e.errno == 1045:
        print("Contraseña incorrecta o usuario no existe. Corrige USER y PASSWORD en este archivo.")
except Exception as e:
    print(f"Error inesperado: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()