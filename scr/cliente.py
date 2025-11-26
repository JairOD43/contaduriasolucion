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
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO clientes (nombre, rfc, regimen_fiscal) VALUES (%s, %s, %s)", (nombre, rfc, regimen_fiscal))
            conn.commit()
            return cls(cur.lastrowid, nombre, rfc, regimen_fiscal)
        finally:
            if cur:
                cur.close()
            conn.close()

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
            conn.close()

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
            conn.close()

    def actualizar(self, nuevo_nombre=None, nuevo_rfc=None, nuevo_regimen=None):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            updates = []
            params = []
            if nuevo_nombre is not None:
                updates.append("nombre = %s")
                params.append(nuevo_nombre)
                self.nombre = nuevo_nombre
            if nuevo_rfc is not None:
                updates.append("rfc = %s")
                params.append(nuevo_rfc)
                self.rfc = nuevo_rfc
            if nuevo_regimen is not None:
                updates.append("regimen_fiscal = %s")
                params.append(nuevo_regimen)
                self.regimen_fiscal = nuevo_regimen
            if updates:
                params.append(self.id)
                query = f"UPDATE clientes SET {', '.join(updates)} WHERE id = %s"
                cur.execute(query, params)
                conn.commit()
        finally:
            if cur:
                cur.close()
            conn.close()

    def eliminar(self):
        conn = get_conn()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM clientes WHERE id = %s", (self.id,))
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cur:
                cur.close()
            conn.close()

    def __str__(self):
        return f"{self.nombre} | RFC: {self.rfc}"