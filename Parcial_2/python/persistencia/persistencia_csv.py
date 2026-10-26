# -*- coding: utf-8 -*-
"""Módulo de persistencia interoperable en formato CSV (compatible con el formato de C++)."""

import os
from typing import Optional
from persistencia import PersistenciaBase
from modelos.multilista import Multilist
from entidades.grupo import Grupo
from entidades.investigador import Investigador
from entidades.producto import Producto


class PersistenciaCSV(PersistenciaBase):
    """Persistencia de datos en formato CSV con el mismo esquema utilizado por C++:
    GRUPO,idGrupo,nombre,plan,activo
    INVESTIGADOR,idGrupo,id,nombre,area,categoria,activo
    PRODUCTO,idGrupo,id,titulo,anio,categoria,validado,peso_rel,puntaje,idInvestigador,activo
    """

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            py_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            root_dir = os.path.dirname(py_dir)
            cand_root = os.path.join(root_dir, "datos", "datos.csv")
            cand_local = os.path.join(py_dir, "datos", "datos.csv")
            if os.path.exists(cand_root):
                filepath = cand_root
            elif os.path.exists(cand_local):
                filepath = cand_local
            else:
                filepath = cand_root
        self.filepath = filepath
        self._ensure_dir()

    def _ensure_dir(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def exists(self) -> bool:
        return os.path.exists(self.filepath)

    @staticmethod
    def _sanitizar(texto: str) -> str:
        return str(texto).replace(",", ";")

    def save(self, multilist: Multilist, filepath: Optional[str] = None) -> bool:
        """Exporta la multilista en el formato CSV compatible con C++."""
        target_path = filepath or self.filepath
        lines = []

        curr_g = multilist.head_group
        while curr_g is not None:
            g = curr_g.data
            gid = getattr(g, "id", 0)
            gnom = self._sanitizar(getattr(g, "nombre", ""))
            gplan = self._sanitizar(getattr(g, "plan", ""))
            gact = 1 if getattr(curr_g, "active", True) and getattr(g, "activo", True) else 0
            lines.append(f"GRUPO,{gid},{gnom},{gplan},{gact}")

            curr_i = curr_g.sublist
            while curr_i is not None:
                inv = curr_i.data
                iid = getattr(inv, "id", None) or getattr(inv, "cedula", 0)
                inom = self._sanitizar(getattr(inv, "nombres", "") or getattr(inv, "nombre", ""))
                iarea = self._sanitizar(getattr(inv, "area", "") or getattr(inv, "areaConocimiento", "General"))
                icat = self._sanitizar(getattr(inv, "categoria", "Investigador"))
                iact = 1 if getattr(curr_i, "active", True) and getattr(inv, "activo", True) else 0
                lines.append(f"INVESTIGADOR,{gid},{iid},{inom},{iarea},{icat},{iact}")

                curr_p = curr_i.sublist
                while curr_p is not None:
                    p = curr_p.data
                    pid = getattr(p, "id", 0)
                    ptit = self._sanitizar(getattr(p, "titulo", ""))
                    panio = getattr(p, "anio", 0)
                    pcat = self._sanitizar(getattr(p, "categoria", "Nuevo conocimiento"))
                    pval = 1 if getattr(p, "validado", True) else 0
                    pw = getattr(p, "peso_relativo", 0.0)
                    psc = getattr(p, "puntaje", 0.0)
                    pact = 1 if getattr(curr_p, "active", True) and getattr(p, "activo", True) else 0
                    lines.append(f"PRODUCTO,{gid},{pid},{ptit},{panio},{pcat},{pval},{pw},{psc},{iid},{pact}")
                    curr_p = curr_p.next

                curr_i = curr_i.next

            curr_g = curr_g.next

        with open(target_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return True

    def load(self, filepath: Optional[str] = None) -> Multilist:
        """Carga datos desde archivo CSV e inicializa una Multilist completa."""
        src_path = filepath or self.filepath
        multilist = Multilist()
        if not os.path.exists(src_path):
            return multilist

        with open(src_path, "r", encoding="utf-8", errors="replace") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                partes = line.split(",")
                if not partes:
                    continue

                tipo = partes[0].upper()
                try:
                    if tipo == "GRUPO" and len(partes) >= 4:
                        gid = int(partes[1])
                        gnom = partes[2]
                        gplan = partes[3]
                        gact = (partes[4] == "1") if len(partes) >= 5 else True
                        grupo = Grupo(id=gid, nombre=gnom, plan=gplan, activo=gact)
                        multilist.add_group(grupo)

                    elif tipo == "INVESTIGADOR" and len(partes) >= 6:
                        gid = int(partes[1])
                        iid = partes[2]
                        inom = partes[3]
                        iarea = partes[4]
                        icat = partes[5]
                        iact = (partes[6] == "1") if len(partes) >= 7 else True
                        inv = Investigador(id=iid, cedula=str(iid), nombres=inom, activo=iact, grupo_id=gid)
                        inv.area = iarea
                        inv.categoria = icat
                        multilist.add_investigador_to_group(gid, inv)

                    elif tipo == "PRODUCTO" and len(partes) >= 7:
                        gid = int(partes[1])
                        pid = partes[2]
                        ptit = partes[3]
                        panio = int(partes[4]) if partes[4].isdigit() else 0
                        pcat = partes[5]
                        pval = (partes[6] == "1")
                        pw = float(partes[7]) if len(partes) >= 8 else 0.0
                        psc = float(partes[8]) if len(partes) >= 9 else 0.0
                        id_inv = partes[9] if len(partes) >= 10 else ""
                        pact = (partes[10] == "1") if len(partes) >= 11 else True

                        prod = Producto(
                            id=pid,
                            titulo=ptit,
                            categoria=pcat,
                            validado=pval,
                            anio=panio,
                            investigador_id=id_inv,
                            grupo_id=gid,
                            peso_relativo=pw,
                            puntaje=psc,
                            activo=pact,
                        )
                        prod.investigador_cedula = str(id_inv)
                        multilist.add_producto(str(id_inv), prod)
                except Exception:
                    continue

        return multilist
