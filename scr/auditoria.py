from db_connection import get_conn
from datetime import date

class Auditoria:
    def __init__(self, id_, transaccion_id, usuario_id, fecha_auditoria, descripcion, resultado):
        self.id = id_
        self.transaccion_id = transaccion_id
        self.usuario_id = usuario_id
        self.fecha_auditoria = fecha_auditoria
        self.descripcion = descripcion
        self.resultado = resultado

    @classmethod
    def crear(cls, transaccion_id, usuario_id, fecha_auditoria, descripcion, resultado='pendiente'):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO auditorias (transaccion_id, usuario_id, fecha_auditoria, descripcion, resultado)
                VALUES (%s, %s, %s, %s, %s)
            """, (transaccion_id, usuario_id, fecha_auditoria, descripcion, resultado))
            conn.commit()
            return cls(cur.lastrowid, transaccion_id, usuario_id, fecha_auditoria, descripcion, resultado)
        finally:
            if cur: cur.close()
            conn.close()

    @classmethod
    def listar_por_transaccion(cls, transaccion_id):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM auditorias WHERE transaccion_id = %s ORDER BY created_at DESC", (transaccion_id,))
            return [cls(*row) for row in cur.fetchall()]
        finally:
            if cur: cur.close()
            conn.close()

    @classmethod
    def listar_por_usuario(cls, usuario_id):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM auditorias WHERE usuario_id = %s ORDER BY created_at DESC", (usuario_id,))
            return [cls(*row) for row in cur.fetchall()]
        finally:
            if cur: cur.close()
            conn.close()

    def actualizar_resultado(self, resultado):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("UPDATE auditorias SET resultado = %s WHERE id = %s", (resultado, self.id))
            conn.commit()
            self.resultado = resultado
        finally:
            if cur: cur.close()
            conn.close()

    def eliminar(self):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM auditorias WHERE id = %s", (self.id,))
            conn.commit()
        finally:
            if cur: cur.close()
            conn.close()