from db_connection import get_conn
from datetime import datetime

class Transaccion:
    def __init__(self, id_, cliente_id, fecha, concepto, monto, tipo_transaccion):
        self.id = id_
        self.cliente_id = cliente_id
        self.fecha = fecha
        self.concepto = concepto
        self.monto = monto
        self.tipo = tipo_transaccion

    @classmethod
    def crear(cls, cliente_id, fecha, concepto, monto, tipo_transaccion):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO transacciones (cliente_id, fecha, concepto, monto, tipo_transaccion)
                VALUES (%s, %s, %s, %s, %s)
            """, (cliente_id, fecha, concepto, monto, tipo_transaccion))
            conn.commit()
            return cls(cur.lastrowid, cliente_id, fecha, concepto, monto, tipo_transaccion)
        finally:
            if cur:
                cur.close()
            conn.close()

    @classmethod
    def listar_por_cliente(cls, cliente_id):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, cliente_id, fecha, concepto, monto, tipo_transaccion FROM transacciones WHERE cliente_id = %s ORDER BY fecha DESC", (cliente_id,))
            return [cls(*row) for row in cur.fetchall()]
        finally:
            if cur:
                cur.close()
            conn.close()