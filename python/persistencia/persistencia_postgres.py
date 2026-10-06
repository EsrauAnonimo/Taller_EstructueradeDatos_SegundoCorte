# -*- coding: utf-8 -*-
import os
import json

from dotenv import load_dotenv
from .persistencia import PersistenciaBase
from ..modelos.multilista import Multilist
from ..entidades.grupo import Grupo
from ..entidades.investigador import Investigador
from ..entidades.producto import Producto

load_dotenv()


class PersistenciaPostgres(PersistenciaBase):
    """Persistencia de datos en PostgreSQL."""

    def __init__(self, host=None, port=None, dbname=None, user=None, password=None):
        """Inicializa la persistencia con credenciales de PostgreSQL."""
        self.host = host or os.getenv('DB_HOST')
        self.port = port or os.getenv('DB_PORT')
        self.dbname = dbname or os.getenv('DB_NAME')
        self.user = user or os.getenv('DB_USER')
        self.password = password or os.getenv('DB_PASSWORD')
        self.conn = None
        try:
            import psycopg2
            self.psycopg2 = psycopg2
        except Exception as e:
            raise Exception('psycopg2 no está instalado') from e

    def connect(self):
        """Abre la conexión si no está abierta."""
        if self.conn is None or self.conn.closed:
            try:
                self.conn = self.psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password
                )
            except Exception as e:
                raise Exception(f'Error al conectar a PostgreSQL: {e}')
        return self.conn

    def close(self):
        """Cierra la conexión."""
        if self.conn is not None and not self.conn.closed:
            self.conn.close()
            self.conn = None

    def exists(self):
        """Verifica si la conexión es exitosa y las tablas existen."""
        try:
            conn = self.connect()
            cur = conn.cursor()
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'grupos')")
            has_grupos = cur.fetchone()[0]
            cur.close()
            return has_grupos
        except Exception:
            return False

    def clear_all(self):
        """Elimina todas las filas en orden correcto."""
        conn = self.connect()
        cur = conn.cursor()
        cur.execute('DELETE FROM productos')
        cur.execute('DELETE FROM investigadores')
        cur.execute('DELETE FROM grupos')
        conn.commit()
        cur.close()

    @classmethod
    def from_multilist(cls, multilist):
        """Serializa una multilista a diccionarios para inserción."""
        grupos = []
        current_group = multilist.head_group
        while current_group is not None:
            grupo_data = current_group.data.to_dict() if hasattr(current_group.data, 'to_dict') else current_group.data
            investigadores = []
            current_inv = current_group.sublist
            while current_inv is not None:
                inv_data = current_inv.data.to_dict() if hasattr(current_inv.data, 'to_dict') else current_inv.data
                productos = []
                current_prod = current_inv.sublist
                while current_prod is not None:
                    prod_data = current_prod.data.to_dict() if hasattr(current_prod.data, 'to_dict') else current_prod.data
                    productos.append(prod_data)
                    current_prod = current_prod.next
                investigadores.append({
                    "investigador": inv_data,
                    "productos": productos
                })
                current_inv = current_inv.next
            grupos.append({
                "grupo": grupo_data,
                "investigadores": investigadores
            })
            current_group = current_group.next
        return {"grupos": grupos}

    @classmethod
    def to_multilist(cls, data):
        """Reconstruye una multilista desde resultados."""
        multilist = Multilist()
        if not data or not isinstance(data, dict):
            return multilist
        grupos_list = data.get("grupos", [])
        for grupo_info in grupos_list:
            grupo_dict = grupo_info.get("grupo", {})
            grupo = Grupo.from_dict(grupo_dict) if hasattr(Grupo, 'from_dict') else Grupo(**grupo_dict)
            group_node = multilist.add_group(grupo)
            if group_node is None:
                continue
            for inv_info in grupo_info.get("investigadores", []):
                inv_dict = inv_info.get("investigador", {})
                investigador = Investigador.from_dict(inv_dict) if hasattr(Investigador, 'from_dict') else Investigador(**inv_dict)
                inv_node = multilist.add_investigador(getattr(grupo, 'id', None), investigador)
                if inv_node is None:
                    continue
                for prod_dict in inv_info.get("productos", []):
                    producto = Producto.from_dict(prod_dict) if hasattr(Producto, 'from_dict') else Producto(**prod_dict)
                    multilist.add_producto(getattr(investigador, 'cedula', None), producto)
        return multilist
    def save(self, multilist):
        """Guarda toda la multilista en PostgreSQL."""
        conn = self.connect()
        cur = conn.cursor()
        try:
            data = self.from_multilist(multilist)
            for grupo_info in data.get("grupos", []):
                g = grupo_info.get("grupo", {})
                try:
                    cur.execute("""
                        INSERT INTO grupos (id, codigo_gruplac, nombre, categoria, lider, activo, fecha_creacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            codigo_gruplac = EXCLUDED.codigo_gruplac,
                            nombre = EXCLUDED.nombre,
                            categoria = EXCLUDED.categoria,
                            lider = EXCLUDED.lider,
                            activo = EXCLUDED.activo,
                            fecha_creacion = EXCLUDED.fecha_creacion
                    """, (
                        g.get("id"),
                        g.get("codigo_gruplac"),
                        g.get("nombre"),
                        g.get("categoria"),
                        g.get("lider"),
                        g.get("activo") if "activo" in g else True,
                        g.get("fecha_creacion")
                    ))
                except Exception:
                    pass
                for inv_info in grupo_info.get("investigadores", []):
                    inv = inv_info.get("investigador", {})
                    try:
                        cur.execute("""
                            INSERT INTO investigadores (id, cedula, nombres, apellidos, email, activo, grupo_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO UPDATE SET
                                cedula = EXCLUDED.cedula,
                                nombres = EXCLUDED.nombres,
                                apellidos = EXCLUDED.apellidos,
                                email = EXCLUDED.email,
                                activo = EXCLUDED.activo,
                                grupo_id = EXCLUDED.grupo_id
                        """, (
                            inv.get("id"),
                            inv.get("cedula"),
                            inv.get("nombres"),
                            inv.get("apellidos"),
                            inv.get("email"),
                            inv.get("activo") if "activo" in inv else True,
                            inv.get("grupo_id") or g.get("id")
                        ))
                    except Exception:
                        pass
                    for prod in inv_info.get("productos", []):
                        try:
                            raw_json = json.dumps(prod.get("raw")) if prod.get("raw") is not None else None
                            cur.execute("""
                                INSERT INTO productos (id, titulo, tipo, categoria, validado, anio, investigador_id, grupo_id, raw)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (id) DO UPDATE SET
                                    titulo = EXCLUDED.titulo,
                                    tipo = EXCLUDED.tipo,
                                    categoria = EXCLUDED.categoria,
                                    validado = EXCLUDED.validado,
                                    anio = EXCLUDED.anio,
                                    investigador_id = EXCLUDED.investigador_id,
                                    grupo_id = EXCLUDED.grupo_id,
                                    raw = EXCLUDED.raw
                            """, (
                                prod.get("id"),
                                prod.get("titulo"),
                                prod.get("tipo"),
                                prod.get("categoria"),
                                prod.get("validado") if "validado" in prod else False,
                                prod.get("anio") if prod.get("anio") is not None else 0,
                                prod.get("investigador_id") or inv.get("id"),
                                prod.get("grupo_id") or g.get("id"),
                                raw_json
                            ))
                        except Exception:
                            pass
            conn.commit()
        finally:
            cur.close()

    def load(self):
        """Carga datos desde PostgreSQL."""
        conn = self.connect()
        cur = conn.cursor()
        grupos_dict = {}
        try:
            cur.execute("SELECT id, codigo_gruplac, nombre, categoria, lider, activo, fecha_creacion FROM grupos")
            for row in cur.fetchall():
                gid = row[0]
                grupos_dict[gid] = {
                    "grupo": {
                        "id": row[0],
                        "codigo_gruplac": row[1],
                        "nombre": row[2],
                        "categoria": row[3],
                        "lider": row[4],
                        "activo": row[5] if row[5] is not None else True,
                        "fecha_creacion": row[6]
                    },
                    "investigadores": {}
                }
            cur.execute("SELECT id, cedula, nombres, apellidos, email, activo, grupo_id FROM investigadores")
            for row in cur.fetchall():
                iid = row[0]
                gid = row[6]
                inv_data = {
                    "investigador": {
                        "id": row[0],
                        "cedula": row[1],
                        "nombres": row[2],
                        "apellidos": row[3],
                        "email": row[4],
                        "activo": row[5] if row[5] is not None else True,
                        "grupo_id": row[6]
                    },
                    "productos": []
                }
                if gid in grupos_dict:
                    grupos_dict[gid]["investigadores"][iid] = inv_data
            cur.execute("SELECT id, titulo, tipo, categoria, validado, anio, investigador_id, grupo_id, raw FROM productos")
            for row in cur.fetchall():
                pid = row[0]
                iid = row[6]
                gid = row[7]
                raw_data = None
                try:
                    if row[8]:
                        raw_data = json.loads(row[8]) if isinstance(row[8], str) else row[8]
                except Exception:
                    raw_data = None
                prod = {
                    "id": row[0],
                    "titulo": row[1],
                    "tipo": row[2],
                    "categoria": row[3],
                    "validado": row[4] if row[4] is not None else False,
                    "anio": row[5] if row[5] is not None else 0,
                    "investigador_id": row[6],
                    "grupo_id": row[7],
                    "raw": raw_data
                }
                for g in grupos_dict.values():
                    if iid in g["investigadores"]:
                        g["investigadores"][iid]["productos"].append(prod)
                        break
            grupos_list = []
            for gdata in grupos_dict.values():
                invs_list = []
                for idata in gdata["investigadores"].values():
                    invs_list.append(idata)
                grupos_list.append({
                    "grupo": gdata["grupo"],
                    "investigadores": invs_list
                })
            return {"grupos": grupos_list}
        finally:
            cur.close()
