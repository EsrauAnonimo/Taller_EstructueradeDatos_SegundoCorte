import requests
from bs4 import BeautifulSoup
import csv
import os

try:
    import pdfplumber
except Exception:
    pdfplumber = None


def download_group(url: str) -> dict:
    """Descarga y extrae datos de un grupo desde SCIENTI."""
    try:
        print("Descargando...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print("Parseando...")
        soup = BeautifulSoup(response.text, "html.parser")
        grupo = parse_group_html(soup)
        investigadores = parse_investigators_html(soup)
        productos = parse_products_html(soup)
        return {
            "grupo": grupo,
            "investigadores": investigadores,
            "productos": productos
        }
    except Exception as e:
        return {"error": str(e)}


def parse_group_html(soup):
    """Extrae información básica del grupo."""
    grupo = {"codigo_gruplac": "", "nombre": "", "categoria": "", "lider": "", "fecha_creacion": ""}
    try:
        # Intento básico de extracción
        texts = soup.get_text(separator=" | ", strip=True)
        # Placeholder: campos pueden variar según la página
        grupo["nombre"] = ""
        grupo["codigo_gruplac"] = ""
        grupo["categoria"] = ""
        grupo["lider"] = ""
        grupo["fecha_creacion"] = ""
    except Exception:
        pass
    return grupo


def parse_investigators_html(soup):
    """Extrae lista de investigadores."""
    investigadores = []
    try:
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all("th")]
            if any("nombre" in h or "investigador" in h or "cedula" in h for h in headers):
                for row in rows[1:]:
                    cells = row.find_all(["td", "th"])
                    if len(cells) < 2:
                        continue
                    inv = {"nombres": cells[0].get_text(strip=True), "cedula": cells[1].get_text(strip=True), "apellidos": "", "email": ""}
                    investigadores.append(inv)
                break
    except Exception:
        pass
    return investigadores


def parse_products_html(soup):
    """Extrae lista de productos."""
    productos = []
    try:
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all("th")]
            if any("titulo" in h or "producto" in h or "año" in h or "anio" in h for h in headers):
                for row in rows[1:]:
                    cells = row.find_all(["td", "th"])
                    if len(cells) < 2:
                        continue
                    prod = {"titulo": cells[0].get_text(strip=True), "tipo": "", "categoria": "", "anio": 0, "validado": False}
                    try:
                        if len(cells) > 4:
                            prod["anio"] = int(''.join(filter(str.isdigit, cells[4].get_text(strip=True))) or 0)
                    except Exception:
                        pass
                    productos.append(prod)
                break
    except Exception:
        pass
    return productos
def load_from_csv(filepath: str) -> dict:
    """Carga datos desde un archivo CSV."""
    if not os.path.exists(filepath):
        return {"error": "Archivo no encontrado"}
    grupos_dict = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                grupo_codigo = row.get('grupo_codigo', '')
                if grupo_codigo not in grupos_dict:
                    grupos_dict[grupo_codigo] = {
                        "grupo": {
                            "codigo_gruplac": grupo_codigo,
                            "nombre": row.get('grupo_nombre', ''),
                            "categoria": row.get('grupo_categoria', ''),
                            "lider": row.get('grupo_lider', ''),
                            "fecha_creacion": row.get('grupo_fecha_creacion', '')
                        },
                        "investigadores": {},
                        "productos": []
                    }
                inv_cedula = row.get('investigador_cedula', '')
                if inv_cedula and inv_cedula not in grupos_dict[grupo_codigo]['investigadores']:
                    grupos_dict[grupo_codigo]['investigadores'][inv_cedula] = {
                        "investigador": {
                            "cedula": inv_cedula,
                            "nombres": row.get('investigador_nombres', ''),
                            "apellidos": row.get('investigador_apellidos', ''),
                            "email": row.get('investigador_email', '')
                        },
                        "productos": []
                    }
                if row.get('producto_titulo'):
                    anio = 0
                    try:
                        anio = int(row.get('producto_anio') or 0)
                    except Exception:
                        pass
                    prod = {
                        "titulo": row.get('producto_titulo', ''),
                        "tipo": row.get('producto_tipo', ''),
                        "categoria": row.get('producto_categoria', ''),
                        "anio": anio,
                        "validado": row.get('producto_validado', '').lower() in ('s', 'si', 'true', '1', 'yes')
                    }
                    if inv_cedula and inv_cedula in grupos_dict[grupo_codigo]['investigadores']:
                        grupos_dict[grupo_codigo]['investigadores'][inv_cedula]['productos'].append(prod)
                    else:
                        grupos_dict[grupo_codigo]['productos'].append(prod)
        grupos_list = []
        for gcode, gdata in grupos_dict.items():
            invs_list = []
            for iced, idata in gdata['investigadores'].items():
                invs_list.append({
                    "investigador": idata['investigador'],
                    "productos": idata['productos']
                })
            if gdata['productos']:
                if invs_list:
                    invs_list[0]['productos'].extend(gdata['productos'])
                else:
                    invs_list.append({"investigador": {}, "productos": gdata['productos']})
            grupos_list.append({
                "grupo": gdata['grupo'],
                "investigadores": invs_list
            })
        return {"grupos": grupos_list}
    except Exception as e:
        return {"error": str(e)}

def load_from_pdf(filepath: str) -> dict:
    """Carga datos desde un archivo PDF."""
    if not os.path.exists(filepath):
        return {"error": "Archivo no encontrado"}
    if pdfplumber is None:
        return {"error": "pdfplumber not installed"}
    try:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return {"grupos": [], "raw_text": text}
    except Exception as e:
        return {"error": str(e)}


def build_entities(data: dict) -> tuple:
    """Convierte datos crudos a entidades."""
    from ..entidades.grupo import Grupo
    from ..entidades.investigador import Investigador
    from ..entidades.producto import Producto

    grupo = None
    investigadores = []
    productos = []
    try:
        grupo = Grupo.from_dict(data.get("grupo", {}))
        for inv in data.get("investigadores", []):
            inv_obj = Investigador.from_dict(inv.get("investigador", {}))
            investigadores.append(inv_obj)
            for prod in inv.get("productos", []):
                prod_obj = Producto.from_dict(prod)
                productos.append(prod_obj)
        for prod in data.get("productos", []):
            prod_obj = Producto.from_dict(prod)
            productos.append(prod_obj)
    except Exception:
        pass
    return (grupo, investigadores, productos)
