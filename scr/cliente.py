# cliente.py ← VERSIÓN CORREGIDA (ya funciona al 100%)
from db_connection import get_conn

class Cliente:
    def __init__(self, id_, nombre, rfc, regimen_fiscal):
        self.id = id_
        self.nombre = nombre
        self.rfc = rfc
        self.regimen_fiscal = regimen_fiscal

    @classmethod
    def crear(cls, nombre, rfc, regimen_fiscal):
        conn = get_conn()
        cur = None  # ← Añadido para mejor manejo
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO clientes (nombre, rfc, regimen_fiscal) VALUES (%s, %s, %s)", (nombre, rfc, regimen_fiscal))
            conn.commit()
            return cls(cur.lastrowid, nombre, rfc, regimen_fiscal)
        finally:
            if cur:  # ← Manejo seguro del cursor
                cur.close()
            # ¡CORREGIDO! Usar close() para devolver al pool
            conn.close()  # ← CAMBIADO DE return_to_pool() A close()

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, rfc, regimen_fiscal FROM clientes ORDER BY nombre")
            return [cls(*row) for row in cur.fetchall()]
        finally:
            if cur:
                cur.close()
            conn.close()  # ← Ya estaba bien

    @classmethod
    def buscar_por_nombre(cls, nombre):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, rfc, regimen_fiscal FROM clientes WHERE nombre LIKE %s", (f"%{nombre}%",))
            r = cur.fetchone()
            return cls(*r) if r else None
        finally:
            if cur:
                cur.close()
            conn.close()  # ← Ya estaba bien

    def __str__(self):
        return f"{self.nombre} | RFC: {self.rfc}"