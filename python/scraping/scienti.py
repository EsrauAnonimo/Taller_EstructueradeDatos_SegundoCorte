"""Módulo de scraping y extracción de datos desde SCIENTI / GrupLAC de Minciencias.

Permite descargar la información de grupos de investigación, sus integrantes
(investigadores) y productos clasificados por tipología bibliográfica y técnica.
Incluye soporte para fallback desde archivos CSV y PDF.
"""

import csv
import logging
import os
import re
import unicodedata
import urllib.parse
from typing import Dict, List, Optional, Tuple, Any

import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

import importlib

try:
    pdfplumber = importlib.import_module("pdfplumber")
except Exception:
    pdfplumber = None

# Configuración del logger del módulo
logger = logging.getLogger("scienti")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)

# Tipologías de productos esperadas en el portal GrupLAC
EXPECTED_PRODUCT_SECTIONS = [
    ("Artículos publicados", "Artículo"),
    ("Otros artículos publicados", "Artículo"),
    ("Libros publicados", "Libro"),
    ("Libros de formación", "Libro"),
    ("Otros Libros publicados", "Libro"),
    ("Capítulos de libro publicados", "Capítulo de libro"),
    ("Documentos de trabajo", "Documento de trabajo"),
    ("Softwares", "Software"),
    ("Otros productos tecnológicos", "Producto tecnológico"),
    ("Eventos Científicos", "Ponencia / Evento"),
    ("Trabajos dirigidos/turorías", "Trabajo dirigido"),
    ("Trabajos dirigidos", "Trabajo dirigido"),
    ("Jurado/Comisiones evaluadoras de trabajo de grado", "Jurado evaluador"),
    ("Consultorías científico-tecnológicas", "Consultoría"),
    ("Demás trabajos", "Otro producto"),
    ("Otra publicación divulgativa", "Publicación divulgativa"),
]


def _normalize(text: str) -> str:
    """Normaliza texto eliminando diacríticos, mayúsculas y espacios sobrantes."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFD", str(text))
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn").lower().strip()


def extract_group_code(url: str) -> str:
    """Extrae el identificador o código del grupo a partir del parámetro 'nro' de la URL."""
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        if "nro" in params and params["nro"]:
            return params["nro"][0]
        match = re.search(r"nro=(\d+)", url)
        if match:
            return match.group(1)
    except Exception:
        pass
    return ""


def download_group(url: str, timeout: int = 35, max_retries: int = 3) -> dict:
    """Descarga y extrae datos de un grupo desde SCIENTI / GrupLAC.

    Maneja codificación (ISO-8859-1 / apparent_encoding), reintentos con backoff,
    timeouts y excepciones de SSL con mensajes descriptivos.
    """
    logger.info("Iniciando descarga desde: %s", url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }

    session = requests.Session()
    retries = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = None
    try:
        try:
            # Intento inicial con verificación de certificados SSL estándar
            response = session.get(url, headers=headers, timeout=timeout, verify=True)
            response.raise_for_status()
        except requests.exceptions.SSLError as ssl_err:
            logger.warning(
                "Advertencia SSL al conectar con SCIENTI (%s). Reintentando conexión segura...",
                ssl_err,
            )
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            try:
                response = session.get(url, headers=headers, timeout=timeout, verify=False)
                response.raise_for_status()
            except requests.exceptions.SSLError as ssl_fatal:
                msg = (
                    f"Error de certificado SSL al conectar con MinCiencias: {ssl_fatal}. "
                    "Verifique su conexión de red o la configuración del certificado."
                )
                logger.error(msg)
                return {"error": msg}
        except requests.exceptions.Timeout as time_err:
            msg = (
                f"Tiempo de espera agotado ({timeout}s) al conectar con MinCiencias. "
                "El servidor no respondió a tiempo. Intente nuevamente más tarde."
            )
            logger.error("%s Detalle: %s", msg, time_err)
            return {"error": msg}
        except requests.exceptions.ConnectionError as conn_err:
            msg = f"No se pudo establecer conexión con el servidor de MinCiencias: {conn_err}"
            logger.error(msg)
            return {"error": msg}
        except requests.exceptions.HTTPError as http_err:
            status = http_err.response.status_code if http_err.response else "N/A"
            msg = f"Error HTTP {status} al solicitar el grupo a MinCiencias: {http_err}"
            logger.error(msg)
            return {"error": msg}

    except Exception as e:
        msg = f"Error inesperado al conectar con SCIENTI: {e}"
        logger.error(msg)
        return {"error": msg}

    if response is None:
        return {"error": "No se obtuvo respuesta del servidor de MinCiencias."}

    # Tratamiento de codificación: Minciencias/GrupLAC responde en ISO-8859-1 (Latin-1)
    if response.encoding and response.encoding.lower() in ("iso-8859-1", "latin-1", "windows-1252"):
        response.encoding = response.encoding
    elif response.apparent_encoding:
        response.encoding = response.apparent_encoding
    else:
        response.encoding = "iso-8859-1"

    html_content = response.text
    logger.info("Página descargada exitosamente (%d bytes). Iniciando parseo...", len(html_content))

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        grupo = parse_group_html(soup, url=url)
        investigadores = parse_investigators_html(soup)
        productos, secciones_vacias = parse_products_html(soup, investigadores=investigadores)

        nombre_grupo = grupo.get("nombre") or "Grupo Desconocido"
        resumen = f"Grupo '{nombre_grupo}': {len(investigadores)} integrantes, {len(productos)} productos"
        logger.info(resumen)

        if secciones_vacias:
            logger.warning(
                "Secciones esperadas sin registros o vacías en '%s': %s",
                nombre_grupo,
                ", ".join(secciones_vacias),
            )

        # Estadísticas por categoría
        stats: Dict[str, int] = {}
        for p in productos:
            cat = p.get("categoria", "Otros")
            stats[cat] = stats.get(cat, 0) + 1

        return {
            "grupo": grupo,
            "investigadores": investigadores,
            "productos": productos,
            "resumen": resumen,
            "secciones_vacias": secciones_vacias,
            "estadisticas": stats,
        }
    except Exception as e:
        msg = f"Error procesando la estructura HTML de SCIENTI: {e}"
        logger.error(msg)
        return {"error": msg}


def parse_group_html(soup: BeautifulSoup, url: str = "") -> dict:
    """Extrae información básica del grupo de investigación desde el HTML.

    Campos extraídos:
    - nombre, categoria, lider, fecha_creacion, codigo_gruplac
    - plan: concatenación de Plan de trabajo, Objetivos y Visión del grupo.
    """
    grupo = {
        "codigo_gruplac": extract_group_code(url),
        "nombre": "",
        "categoria": "",
        "lider": "",
        "fecha_creacion": "",
        "plan": "",
    }
    try:
        # 1. Nombre del grupo desde celdaEncabezado o título
        span_enc = soup.find("span", class_="celdaEncabezado")
        if not span_enc:
            span_enc = soup.find("td", class_="celdaEncabezado")
        if span_enc:
            grupo["nombre"] = span_enc.get_text(strip=True)
        elif soup.title:
            t = soup.title.get_text(strip=True)
            if "-" in t:
                grupo["nombre"] = t.split("-", 1)[1].strip()
            else:
                grupo["nombre"] = t

        # 2. Metadatos en tabla de datos básicos
        for tr in soup.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if len(cells) >= 2:
                label = _normalize(cells[0])
                val = cells[1].strip()
                if "lider" in label:
                    grupo["lider"] = val
                elif "clasificacion" in label:
                    # Ejemplo: 'Ccon vigencia hasta...' -> 'C'
                    clean_cat = val.split("con")[0].strip() if "con" in val.lower() else val
                    grupo["categoria"] = clean_cat or val
                elif "ano y mes de formacion" in label or (
                    "formacion" in label and "informacion" not in label
                ):
                    grupo["fecha_creacion"] = val
                elif "codigo del grupo" in label and not grupo["codigo_gruplac"]:
                    grupo["codigo_gruplac"] = val

        # 3. Extracción del Plan Estratégico (Plan de trabajo, Objetivos, Visión)
        grupo["plan"] = _extract_plan_estrategico(soup)

    except Exception as e:
        logger.warning("Error extrayendo datos del grupo: %s", e)

    return grupo


def _extract_plan_estrategico(soup: BeautifulSoup) -> str:
    """Extrae y formatea el bloque 'Plan Estratégico' de la página GrupLAC.

    Busca la sección con encabezado 'Plan Estratégico' y extrae de la siguiente
    fila las sub-secciones: 'Plan de trabajo:', 'Objetivos:' y 'Visión:'.
    Devuelve un string formateado con separadores o cadena vacía si no se encuentra.
    """
    try:
        for header_td in soup.find_all("td", class_="celdaEncabezado"):
            norm = _normalize(header_td.get_text(strip=True))
            if "plan" not in norm or "estrateg" not in norm:
                continue

            tr = header_td.parent
            if not tr:
                continue
            content_tr = tr.find_next_sibling("tr")
            if not content_tr:
                continue
            content_td = content_tr.find("td")
            if not content_td:
                continue

            # Obtener texto limpio manteniendo saltos de línea
            raw = content_td.get_text(separator="\n", strip=False)
            # Normalizar saltos de línea Windows y colapsar líneas en blanco excesivas
            raw = re.sub(r"\r\n|\r", "\n", raw)
            raw = re.sub(r"\n{3,}", "\n\n", raw).strip()

            if not raw:
                return ""

            # Dividir por las etiquetas de sub-sección conocidas
            _LABEL_PATTERN = re.compile(
                r"(Plan\s+de\s+trabajo\s*:"
                r"|Objetivos?\s*:"
                r"|Visi\u00f3n\s*:"
                r"|Vision\s*:"
                r"|Misi\u00f3n\s*:"
                r"|Mision\s*:"
                r"|Estado\s+del\s+arte\s*:)",
                re.IGNORECASE,
            )
            parts = _LABEL_PATTERN.split(raw)
            # parts = [prefix, label1, content1, label2, content2, ...]

            # Construir el campo plan a partir de las sub-secciones de interés
            _WANTED = {"plan de trabajo", "objetivo", "objetivos", "vision", "visión"}
            sections_found = {}
            i = 1
            while i < len(parts) - 1:
                label_raw = parts[i].strip().rstrip(":")
                content = parts[i + 1].strip()
                label_key = _normalize(label_raw)

                # Solo incluir las secciones deseadas (excluir 'Estado del arte', etc.)
                if any(w in label_key for w in _WANTED):
                    # Normalizar la etiqueta para el encabezado
                    if "plan" in label_key:
                        header = "PLAN DE TRABAJO"
                    elif "objetivo" in label_key:
                        header = "OBJETIVOS"
                    elif "vision" in label_key or "visión" in label_key:
                        header = "VISIÓN"
                    elif "mision" in label_key or "misión" in label_key:
                        header = "MISIÓN"
                    else:
                        header = label_raw.upper()
                    sections_found[header] = content
                i += 2

            # Si no hubo divisiones claras, usar el texto completo como plan
            if not sections_found:
                # Quitar posibles prefijos de otras secciones no deseadas
                fallback = re.sub(
                    r"(Estado\s+del\s+arte\s*:.*)",
                    "",
                    raw,
                    flags=re.IGNORECASE | re.DOTALL,
                ).strip()
                return fallback

            # Ensamblar el resultado final con separadores
            result_parts = []
            for header, content in sections_found.items():
                result_parts.append(f"{header}:\n{content}")
            return "\n\n".join(result_parts)

    except Exception as e:
        logger.warning("Error extrayendo Plan Estratégico: %s", e)

    return ""



def parse_investigators_html(soup: BeautifulSoup) -> list:
    """Extrae la lista de investigadores integrantes del grupo."""
    investigadores = []
    try:
        int_table = soup.find(
            lambda tag: tag.name == "table" and "Integrantes del grupo" in tag.get_text()
        )
        if not int_table:
            logger.info("No se encontró la tabla 'Integrantes del grupo'.")
            return []

        rows = int_table.find_all("tr")
        if len(rows) < 3:
            logger.info("La tabla 'Integrantes del grupo' no tiene filas de datos.")
            return []

        # Las filas de datos comienzan en el índice 2 (fila 0: título, fila 1: encabezados)
        for row in rows[2:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            raw_name = cells[0].get_text(strip=True)
            clean_name = re.sub(r"^\d+[\.\-]+\s*", "", raw_name).strip()
            if not clean_name:
                continue

            vinculacion = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            horas = cells[2].get_text(strip=True) if len(cells) > 2 else "0"
            periodo = cells[3].get_text(strip=True) if len(cells) > 3 else ""

            # Extraer identificador único de CvLAC si existe
            cedula = ""
            link = row.find("a", href=True)
            if link and "cod_rh=" in link["href"]:
                cedula = link["href"].split("cod_rh=")[-1].split("&")[0]

            if not cedula:
                cedula = f"INV-{len(investigadores) + 1:04d}"

            # Separar nombres y apellidos razonablemente
            parts = [p for p in clean_name.split() if p]
            if len(parts) >= 3:
                nombres = " ".join(parts[:2])
                apellidos = " ".join(parts[2:])
            elif len(parts) == 2:
                nombres = parts[0]
                apellidos = parts[1]
            else:
                nombres = clean_name
                apellidos = ""

            activo = "actual" in periodo.lower() if periodo else True

            inv = {
                "id": cedula,
                "cedula": cedula,
                "nombres": nombres,
                "apellidos": apellidos,
                "nombre_completo": clean_name,
                "vinculacion": vinculacion,
                "horas": horas,
                "periodo": periodo,
                "activo": activo,
                "email": "",
            }
            investigadores.append(inv)

    except Exception as e:
        logger.warning("Error extrayendo lista de investigadores: %s", e)

    return investigadores


def parse_products_html(soup: BeautifulSoup, investigadores: Optional[list] = None) -> Tuple[list, list]:
    """Extrae productos por tipología asociándolos al grupo y a su investigador autor."""
    productos = []
    secciones_vacias = []
    investigadores = investigadores or []

    section_map = {}
    for sec_name, cat in EXPECTED_PRODUCT_SECTIONS:
        section_map[_normalize(sec_name)] = (sec_name, cat)

    found_sections = set()

    try:
        tables = soup.find_all("table")
        for table in tables:
            first_td = table.find("td")
            if not first_td:
                continue
            title_text = first_td.get_text(strip=True)
            norm_title = _normalize(title_text)

            matched_cat = None
            matched_sec_name = None
            for key, (orig_sec, cat) in section_map.items():
                if key in norm_title:
                    matched_cat = cat
                    matched_sec_name = orig_sec
                    break

            if not matched_cat or not matched_sec_name:
                continue

            found_sections.add(matched_sec_name)
            rows = table.find_all("tr")
            data_rows = rows[1:]

            if not data_rows:
                if matched_sec_name not in secciones_vacias:
                    secciones_vacias.append(matched_sec_name)
                continue

            section_prod_count = 0
            for r in data_rows:
                cells = r.find_all("td")
                if not cells:
                    continue

                full_text = cells[-1].get_text(separator=" ", strip=True)
                if not full_text or len(full_text) < 5:
                    continue

                clean = re.sub(r"\s+", " ", full_text).strip()
                clean = re.sub(r"^\d+[\.\-]+\s*", "", clean)

                # 1. Extraer Autores / Tutores
                autores = []
                body = clean
                autores_match = re.search(
                    r"(?:Autores|Tutor\(es\)\/Cotutor\(es\)|Tutor)\s*:\s*(.*)$",
                    clean,
                    re.IGNORECASE,
                )
                if autores_match:
                    autores_str = autores_match.group(1).strip()
                    body = clean[: autores_match.start()].strip()
                    autores = [a.strip() for a in autores_str.split(",") if a.strip()]

                # 2. Extraer Año
                years = re.findall(r"\b(19\d\d|20\d\d)\b", clean)
                anio = int(years[0]) if years else 0

                # 3. Subtipo y Título
                prod_type = matched_cat
                titulo = body
                sub_match = re.match(r"^([^:]+):\s*(.*)$", body)
                if sub_match and len(sub_match.group(1).strip()) < 60:
                    sub = sub_match.group(1).strip()
                    titulo = sub_match.group(2).strip()
                    if matched_cat in ["Artículo", "Libro", "Software"]:
                        prod_type = f"{matched_cat} ({sub})"
                    else:
                        prod_type = sub

                # Limpieza de metadatos bibliográficos anexos al título
                split_meta = re.split(
                    r"(?:Colombia|España|México|Brasil|Argentina|Chile|Perú|USA|Estados Unidos|ISSN|ISBN|vol:|fasc:|\bEd\.)",
                    titulo,
                    maxsplit=1,
                    flags=re.IGNORECASE,
                )
                if len(split_meta) > 1 and len(split_meta[0].strip()) > 8:
                    titulo_clean = split_meta[0].strip().rstrip(",.-: ")
                else:
                    titulo_clean = titulo[:250].strip().rstrip(",.-: ")

                # 4. Asociar producto con el investigador autor
                assigned_cedula = ""
                for aut in autores:
                    norm_aut = _normalize(aut)
                    for inv in investigadores:
                        norm_inv = _normalize(inv.get("nombre_completo", ""))
                        aut_words = [w for w in norm_aut.split() if len(w) > 2]
                        inv_words = [w for w in norm_inv.split() if len(w) > 2]
                        overlap = set(aut_words).intersection(inv_words)
                        if len(overlap) >= 2:
                            assigned_cedula = inv["cedula"]
                            break
                    if assigned_cedula:
                        break

                prod = {
                    "titulo": titulo_clean,
                    "tipo": prod_type,
                    "categoria": matched_cat,
                    "anio": anio,
                    "investigador_cedula": assigned_cedula,
                    "autores": autores,
                    "validado": True,
                    "raw": clean[:300],
                }
                productos.append(prod)
                section_prod_count += 1

            if section_prod_count == 0 and matched_sec_name not in secciones_vacias:
                secciones_vacias.append(matched_sec_name)

    except Exception as e:
        logger.warning("Error extrayendo productos: %s", e)

    # Identificar secciones esperadas que no aparecieron en la página
    for orig_sec, _ in EXPECTED_PRODUCT_SECTIONS:
        if orig_sec not in found_sections and orig_sec not in secciones_vacias:
            secciones_vacias.append(orig_sec)

    return productos, secciones_vacias


def load_from_csv(filepath: str) -> dict:
    """Carga datos desde un archivo CSV con fallback a estructura jerárquica."""
    if not os.path.exists(filepath):
        return {"error": "Archivo no encontrado"}
    grupos_dict = {}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                grupo_codigo = row.get("grupo_codigo", "")
                if grupo_codigo not in grupos_dict:
                    grupos_dict[grupo_codigo] = {
                        "grupo": {
                            "codigo_gruplac": grupo_codigo,
                            "nombre": row.get("grupo_nombre", ""),
                            "categoria": row.get("grupo_categoria", ""),
                            "lider": row.get("grupo_lider", ""),
                            "fecha_creacion": row.get("grupo_fecha_creacion", ""),
                        },
                        "investigadores": {},
                        "productos": [],
                    }
                inv_cedula = row.get("investigador_cedula", "")
                if inv_cedula and inv_cedula not in grupos_dict[grupo_codigo]["investigadores"]:
                    grupos_dict[grupo_codigo]["investigadores"][inv_cedula] = {
                        "investigador": {
                            "cedula": inv_cedula,
                            "nombres": row.get("investigador_nombres", ""),
                            "apellidos": row.get("investigador_apellidos", ""),
                            "email": row.get("investigador_email", ""),
                        },
                        "productos": [],
                    }
                if row.get("producto_titulo"):
                    anio = 0
                    try:
                        anio = int(row.get("producto_anio") or 0)
                    except Exception:
                        pass
                    prod = {
                        "titulo": row.get("producto_titulo", ""),
                        "tipo": row.get("producto_tipo", ""),
                        "categoria": row.get("producto_categoria", ""),
                        "anio": anio,
                        "validado": row.get("producto_validado", "").lower()
                        in ("s", "si", "true", "1", "yes"),
                    }
                    if (
                        inv_cedula
                        and inv_cedula in grupos_dict[grupo_codigo]["investigadores"]
                    ):
                        grupos_dict[grupo_codigo]["investigadores"][inv_cedula]["productos"].append(
                            prod
                        )
                    else:
                        grupos_dict[grupo_codigo]["productos"].append(prod)

        grupos_list = []
        for gcode, gdata in grupos_dict.items():
            invs_list = []
            for iced, idata in gdata["investigadores"].items():
                invs_list.append(
                    {
                        "investigador": idata["investigador"],
                        "productos": idata["productos"],
                    }
                )
            if gdata["productos"]:
                if invs_list:
                    invs_list[0]["productos"].extend(gdata["productos"])
                else:
                    invs_list.append(
                        {"investigador": {}, "productos": gdata["productos"]}
                    )
            grupos_list.append(
                {"grupo": gdata["grupo"], "investigadores": invs_list}
            )
        return {"grupos": grupos_list}
    except Exception as e:
        return {"error": str(e)}


def load_from_pdf(filepath: str) -> dict:
    """Carga texto crudo desde un archivo PDF."""
    if not os.path.exists(filepath):
        return {"error": "Archivo no encontrado"}
    if pdfplumber is None:
        return {"error": "pdfplumber no está instalado"}
    try:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return {"grupos": [], "raw_text": text}
    except Exception as e:
        return {"error": str(e)}


def build_entities(data: dict) -> tuple:
    """Convierte un diccionario crudo de datos a instancias de entidades del dominio."""
    try:
        from ..entidades.grupo import Grupo
        from ..entidades.investigador import Investigador
        from ..entidades.producto import Producto
    except (ImportError, ValueError):
        from entidades.grupo import Grupo
        from entidades.investigador import Investigador
        from entidades.producto import Producto

    grupo = None
    investigadores = []
    productos = []
    try:
        grupo = Grupo.from_dict(data.get("grupo", {}))
        for inv in data.get("investigadores", []):
            inv_dict = inv.get("investigador", {}) if "investigador" in inv else inv
            inv_obj = Investigador.from_dict(inv_dict)
            investigadores.append(inv_obj)
            for prod in inv.get("productos", []):
                prod_obj = Producto.from_dict(prod)
                productos.append(prod_obj)
        for prod in data.get("productos", []):
            prod_obj = Producto.from_dict(prod)
            productos.append(prod_obj)
    except Exception as e:
        logger.warning("Error construyendo entidades desde datos: %s", e)

    return (grupo, investigadores, productos)
