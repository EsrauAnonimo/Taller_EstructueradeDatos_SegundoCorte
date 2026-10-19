//! Módulo de scraping y extracción de datos desde SCIENTI / GrupLAC de MinCiencias.
//!
//! Utiliza `reqwest` (modo blocking) y `scraper` (HTML parsing) para descargar e
//! indexar grupos de investigación, sus integrantes y productos según la taxonomía MinCiencias.

use crate::modelos::entidades::{
    normalizar_gran_categoria, Grupo, Investigador, Producto,
};
use scraper::{Html, Selector};
use std::time::Duration;

pub struct ResultadoScraping {
    pub grupo: Grupo,
    pub investigadores: Vec<Investigador>,
    pub productos: Vec<Producto>,
    pub resumen: String,
}

/// Extrae el código del grupo a partir del parámetro 'nro' de la URL.
pub fn extract_group_code(url: &str) -> String {
    if let Ok(parsed) = reqwest::Url::parse(url) {
        for (k, v) in parsed.query_pairs() {
            if k == "nro" {
                return v.to_string();
            }
        }
    }
    // Fallback con regex simple manual
    if let Some(pos) = url.find("nro=") {
        let sub = &url[pos + 4..];
        let end = sub.find('&').unwrap_or(sub.len());
        return sub[..end].to_string();
    }
    String::new()
}

/// Normaliza texto quitando tildes y espacios extras.
fn normalizar_texto(s: &str) -> String {
    s.trim()
        .to_lowercase()
        .replace('á', "a")
        .replace('é', "e")
        .replace('í', "i")
        .replace('ó', "o")
        .replace('ú', "u")
        .replace('ñ', "n")
}

/// Descarga y parsea un grupo desde GrupLAC.
pub fn download_group(url: &str, timeout_secs: u64) -> Result<ResultadoScraping, String> {
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .danger_accept_invalid_certs(true) // GrupLAC a veces tiene certificados autofirmados
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
        .build()
        .map_err(|e| format!("Error creando cliente HTTP: {}", e))?;

    let response = client
        .get(url)
        .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        .header("Accept-Language", "es-ES,es;q=0.9")
        .send()
        .map_err(|e| format!("Error conectando con MinCiencias ({})", e))?;

    if !response.status().is_success() {
        return Err(format!("El servidor respondió con código HTTP {}", response.status()));
    }

    let bytes = response
        .bytes()
        .map_err(|e| format!("Error leyendo el cuerpo de la respuesta: {}", e))?;

    // MinCiencias usualmente responde en Latin-1 / ISO-8859-1 o UTF-8.
    // En ISO-8859-1, los bytes 0..=255 se corresponden 1 a 1 con U+0000..=U+00FF.
    let html_content = match String::from_utf8(bytes.to_vec()) {
        Ok(s) => s,
        Err(_) => bytes.iter().map(|&b| b as char).collect(),
    };

    let document = Html::parse_document(&html_content);

    let code_from_url = extract_group_code(url);
    let mut grupo = parse_group_html(&document, &code_from_url);
    let gid = grupo.id.unwrap_or(1);

    let investigadores = parse_investigators_html(&document, gid);
    let productos = parse_products_html(&document, &investigadores, gid);

    let resumen = format!(
        "Grupo '{}': {} investigadores, {} productos extraídos",
        grupo.nombre,
        investigadores.len(),
        productos.len()
    );

    if grupo.codigo_gruplac.is_empty() {
        grupo.codigo_gruplac = code_from_url;
    }

    Ok(ResultadoScraping {
        grupo,
        investigadores,
        productos,
        resumen,
    })
}

/// Extrae metadatos del grupo desde el DOM.
fn parse_group_html(doc: &Html, code_from_url: &str) -> Grupo {
    let mut nombre = String::new();
    let mut categoria = String::new();
    let mut lider = String::new();
    let mut fecha_creacion = String::new();
    let mut codigo_gruplac = code_from_url.to_string();

    // 1. Nombre del grupo desde celdaEncabezado o h1
    if let Ok(sel_span) = Selector::parse("span.celdaEncabezado, td.celdaEncabezado, h1") {
        if let Some(el) = doc.select(&sel_span).next() {
            nombre = el.text().collect::<Vec<_>>().join(" ").trim().to_string();
        }
    }

    if nombre.is_empty() {
        if let Ok(sel_title) = Selector::parse("title") {
            if let Some(el) = doc.select(&sel_title).next() {
                let t = el.text().collect::<Vec<_>>().join(" ");
                if t.contains('-') {
                    nombre = t.split('-').nth(1).unwrap_or(&t).trim().to_string();
                } else {
                    nombre = t.trim().to_string();
                }
            }
        }
    }

    // 2. Metadatos en filas de tabla
    if let Ok(sel_tr) = Selector::parse("tr") {
        if let Ok(sel_td) = Selector::parse("td, th") {
            for tr in doc.select(&sel_tr) {
                let cells: Vec<String> = tr
                    .select(&sel_td)
                    .map(|c| c.text().collect::<Vec<_>>().join(" ").trim().to_string())
                    .collect();

                if cells.len() >= 2 {
                    let label = normalizar_texto(&cells[0]);
                    let val = cells[1].trim();

                    if label.contains("lider") {
                        lider = val.to_string();
                    } else if label.contains("clasificacion") {
                        let clean_cat = if val.to_lowercase().contains("con") {
                            val.split("con").next().unwrap_or(val).trim().to_string()
                        } else {
                            val.to_string()
                        };
                        categoria = clean_cat;
                    } else if label.contains("formacion") && !label.contains("informacion") {
                        fecha_creacion = val.to_string();
                    } else if label.contains("codigo del grupo") && codigo_gruplac.is_empty() {
                        codigo_gruplac = val.to_string();
                    }
                }
            }
        }
    }

    let plan = extract_plan_estrategico(doc);

    Grupo {
        id: None,
        codigo_gruplac,
        nombre: if nombre.is_empty() { "Grupo GrupLAC".to_string() } else { nombre },
        categoria,
        lider,
        activo: true,
        fecha_creacion,
        plan,
    }
}

/// Extrae el texto del bloque 'Plan Estratégico'.
fn extract_plan_estrategico(doc: &Html) -> String {
    let mut plan_text = String::new();
    if let Ok(sel_td) = Selector::parse("td.celdaEncabezado") {
        for td in doc.select(&sel_td) {
            let txt = normalizar_texto(&td.text().collect::<Vec<_>>().join(" "));
            if txt.contains("plan") && txt.contains("estrateg") {
                // Obtener fila siguiente
                if let Some(parent) = td.parent() {
                    if let Some(next_sibling) = parent.next_sibling() {
                        if let Some(el) = scraper::ElementRef::wrap(next_sibling) {
                            plan_text = el.text().collect::<Vec<_>>().join("\n").trim().to_string();
                            break;
                        }
                    }
                }
            }
        }
    }
    plan_text
}

/// Extrae la lista de investigadores integrantes.
fn parse_investigators_html(doc: &Html, grupo_id: i64) -> Vec<Investigador> {
    let mut list = Vec::new();
    if let Ok(sel_table) = Selector::parse("table") {
        if let Ok(sel_tr) = Selector::parse("tr") {
            if let Ok(sel_td) = Selector::parse("td, th") {
                if let Ok(sel_a) = Selector::parse("a[href]") {
                    for table in doc.select(&sel_table) {
                        let text = table.text().collect::<Vec<_>>().join(" ");
                        if text.contains("Integrantes del grupo") {
                            let rows: Vec<_> = table.select(&sel_tr).collect();
                            // Saltar fila de encabezado
                            for row in rows.into_iter().skip(2) {
                                let cells: Vec<String> = row
                                    .select(&sel_td)
                                    .map(|c| c.text().collect::<Vec<_>>().join(" ").trim().to_string())
                                    .collect();

                                if cells.is_empty() {
                                    continue;
                                }

                                let raw_name = &cells[0];
                                // Quitar numeración como "1.- "
                                let clean_name = raw_name
                                    .trim_start_matches(|c: char| c.is_ascii_digit() || c == '.' || c == '-' || c == ' ')
                                    .trim();
                                if clean_name.is_empty() {
                                    continue;
                                }

                                // Extraer código de CvLAC si existe
                                let mut cedula = String::new();
                                for a in row.select(&sel_a) {
                                    if let Some(href) = a.value().attr("href") {
                                        if href.contains("cod_rh=") {
                                            if let Some(sub) = href.split("cod_rh=").nth(1) {
                                                let end = sub.find('&').unwrap_or(sub.len());
                                                cedula = sub[..end].to_string();
                                                break;
                                            }
                                        }
                                    }
                                }

                                if cedula.is_empty() {
                                    cedula = format!("INV-{:04}", list.len() + 1);
                                }

                                let parts: Vec<&str> = clean_name.split_whitespace().collect();
                                let (nombres, apellidos) = if parts.len() >= 3 {
                                    (parts[..2].join(" "), parts[2..].join(" "))
                                } else if parts.len() == 2 {
                                    (parts[0].to_string(), parts[1].to_string())
                                } else {
                                    (clean_name.to_string(), String::new())
                                };

                                list.push(Investigador {
                                    id: Some(cedula.clone()),
                                    cedula,
                                    nombres,
                                    apellidos,
                                    email: String::new(),
                                    activo: true,
                                    grupo_id: Some(grupo_id),
                                });
                            }
                        }
                    }
                }
            }
        }
    }
    list
}

/// Extrae productos por tipología asociándolos a sus autores.
fn parse_products_html(
    doc: &Html,
    investigadores: &[Investigador],
    grupo_id: i64,
) -> Vec<Producto> {
    let mut productos = Vec::new();
    let sections = [
        ("Artículos publicados", "Artículo", "GNC", "2.2.1.1"),
        ("Otros artículos publicados", "Artículo", "GNC", "2.2.1.1"),
        ("Libros publicados", "Libro", "GNC", "2.2.1.3"),
        ("Libros de formación", "Libro", "GNC", "2.2.3.4.3.1"),
        ("Otros Libros publicados", "Libro", "GNC", "2.2.1.3"),
        ("Capítulos de libro publicados", "Capítulo de libro", "GNC", "2.2.1.4"),
        ("Softwares", "Software", "DTI", "2.2.2.1"),
        ("Otros productos tecnológicos", "Producto tecnológico", "DTI", "2.2.2.1"),
        ("Consultorías científico-tecnológicas", "Consultoría", "DTI", "2.2.2.4"),
        ("Documentos de trabajo", "Documento de trabajo", "ASC", "2.2.3.4.1"),
        ("Eventos Científicos", "Ponencia / Evento", "ASC", "2.2.3.3.1"),
        ("Otra publicación divulgativa", "Publicación divulgativa", "ASC", "2.2.3.4.2"),
        ("Demás trabajos", "Otro producto", "ASC", "2.2.3.4.2"),
        ("Trabajos dirigidos/tutorías", "Trabajo dirigido", "FRH", "2.2.4.1"),
        ("Trabajos dirigidos", "Trabajo dirigido", "FRH", "2.2.4.3"),
    ];

    if let Ok(sel_table) = Selector::parse("table") {
        if let Ok(sel_tr) = Selector::parse("tr") {
            if let Ok(sel_td) = Selector::parse("td") {
                for table in doc.select(&sel_table) {
                    let header_text = normalizar_texto(&table.text().collect::<Vec<_>>().join(" "));

                    for (sec_name, tipo, gran_cat, cod_minc) in sections {
                        let norm_sec = normalizar_texto(sec_name);
                        if header_text.contains(&norm_sec) {
                            for row in table.select(&sel_tr).skip(1) {
                                let cells: Vec<String> = row
                                    .select(&sel_td)
                                    .map(|c| c.text().collect::<Vec<_>>().join(" ").trim().to_string())
                                    .collect();

                                if let Some(last_cell) = cells.last() {
                                    if last_cell.len() < 5 {
                                        continue;
                                    }

                                    // Extraer año de 4 dígitos
                                    let mut anio = None;
                                    for word in last_cell.split(|c: char| !c.is_ascii_digit()) {
                                        if word.len() == 4 {
                                            if let Ok(y) = word.parse::<i32>() {
                                                if (1950..=2030).contains(&y) {
                                                    anio = Some(y);
                                                    break;
                                                }
                                            }
                                        }
                                    }

                                    // Extraer título limpio
                                    let clean_text = last_cell
                                        .trim_start_matches(|c: char| c.is_ascii_digit() || c == '.' || c == '-' || c == ' ')
                                        .trim();
                                    let titulo = if clean_text.len() > 180 {
                                        clean_text[..180].to_string()
                                    } else {
                                        clean_text.to_string()
                                    };

                                    // Intentar emparejar autor con investigador integrante
                                    let mut assigned_cedula = if let Some(first_inv) = investigadores.first() {
                                        first_inv.cedula.clone()
                                    } else {
                                        format!("INV-{}", grupo_id)
                                    };

                                    let norm_cell = normalizar_texto(last_cell);
                                    for inv in investigadores {
                                        let inv_norm = normalizar_texto(&inv.nombre_completo());
                                        let words: Vec<&str> = inv_norm.split_whitespace().filter(|w| w.len() > 3).collect();
                                        if !words.is_empty() && words.iter().all(|w| norm_cell.contains(w)) {
                                            assigned_cedula = inv.cedula.clone();
                                            break;
                                        }
                                    }

                                    let pid = format!("PRD-{}", productos.len() + 1);
                                    productos.push(Producto {
                                        id: Some(pid),
                                        titulo,
                                        tipo: tipo.to_string(),
                                        categoria: match gran_cat {
                                            "DTI" => "Desarrollo tecnológico".to_string(),
                                            "ASC" => "Apropiación social del conocimiento".to_string(),
                                            "FRH" => "Formación de recurso humano".to_string(),
                                            _ => "Nuevo conocimiento".to_string(),
                                        },
                                        validado: true,
                                        anio,
                                        investigador_id: Some(assigned_cedula.clone()),
                                        investigador_cedula: Some(assigned_cedula),
                                        grupo_id: Some(grupo_id),
                                        raw: None,
                                        gran_categoria: normalizar_gran_categoria(gran_cat),
                                        codigo_minciencias: cod_minc.to_string(),
                                        validacion: "Validado".to_string(),
                                        activo: true,
                                    });
                                }
                            }
                            break;
                        }
                    }
                }
            }
        }
    }
    productos
}
