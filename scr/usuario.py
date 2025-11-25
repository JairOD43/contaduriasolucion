# usuario.py  ← VERSIÓN FINAL CORREGIDA (FUNCIONA AL 100%)
from db_connection import get_conn
import hashlib

def hash_password(password):
    if not password:
        return None
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class Usuario:
    def __init__(self, id_, nombre, role="cliente"):
        self.id = id_
        self.nombre = nombre
        self.role = role

    @classmethod
    def crear(cls, nombre, role="cliente", password=None):
        conn = get_conn()  # ← Viene del pool
        cur = None
        try:
            cur = conn.cursor()
            pwd_hash = hash_password(password)
            cur.execute(
                "INSERT INTO usuarios (nombre, role, password) VALUES (%s, %s, %s)",
                (nombre, role, pwd_hash)
            )
            conn.commit()
            return cls(cur.lastrowid, nombre, role)
        finally:
            if cur:
                cur.close()
            # ¡IMPORTANTE! Con pool, usamos close() para devolverla al pool
            conn.close()   # ← Esto SÍ devuelve la conexión al pool

    @classmethod
    def autenticar(cls, nombre, password):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role, password FROM usuarios WHERE nombre = %s", (nombre,))
            row = cur.fetchone()
            if row and row[3] and hash_password(password) == row[3]:
                return cls(row[0], row[1], row[2])
            return None
        finally:
            if cur:
                cur.close()
            conn.close()   # ← Correcto: devuelve al pool

    @classmethod
    def buscar_por_nombre(cls, nombre):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role FROM usuarios WHERE nombre = %s", (nombre,))
            row = cur.fetchone()
            if row:
                return cls(row[0], row[1], row[2])
            return None
        finally:
            if cur:
                cur.close()
            conn.close()   # ← Correcto

    @classmethod
    def listar_todos(cls):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre, role FROM usuarios ORDER BY nombre")
            rows = cur.fetchall()
            return [cls(row[0], row[1], row[2]) for row in rows]
        finally:
            if cur:
                cur.close()
            conn.close()

    def __str__(self):
        return f"{self.nombre} ({self.role})"