//! Lector e importador de datos desde archivos CSV hacia las entidades del sistema.

use crate::modelos::entidades::{Grupo, Investigador, Producto};
use std::fs::File;
use std::path::Path;

pub struct DatosCsvImportados {
    pub grupos: Vec<Grupo>,
    pub investigadores: Vec<Investigador>,
    pub productos: Vec<Producto>,
}

pub fn cargar_desde_csv(ruta: impl AsRef<Path>) -> Result<DatosCsvImportados, String> {
    let file = File::open(ruta.as_ref())
        .map_err(|e| format!("No se pudo abrir el archivo CSV: {}", e))?;

    let mut rdr = csv::ReaderBuilder::new()
        .has_headers(true)
        .flexible(true)
        .from_reader(file);

    let headers = rdr
        .headers()
        .map_err(|e| format!("Error leyendo encabezados CSV: {}", e))?
        .clone();

    let mut grupos: Vec<Grupo> = Vec::new();
    let mut investigadores: Vec<Investigador> = Vec::new();
    let mut productos: Vec<Producto> = Vec::new();

    for result in rdr.records() {
        let record = result.map_err(|e| format!("Error en fila CSV: {}", e))?;

        let get_val = |key: &str| -> String {
            for (idx, h) in headers.iter().enumerate() {
                if h.trim().eq_ignore_ascii_case(key) {
                    return record.get(idx).unwrap_or("").trim().to_string();
                }
            }
            String::new()
        };

        // Extraer Grupo
        let g_code = get_val("grupo_codigo");
        let g_name = get_val("grupo_nombre");
        if !g_code.is_empty() || !g_name.is_empty() {
            let existing = grupos.iter().any(|g| g.codigo_gruplac == g_code && !g_code.is_empty());
            if !existing {
                grupos.push(Grupo {
                    id: None,
                    codigo_gruplac: g_code.clone(),
                    nombre: if g_name.is_empty() { format!("Grupo {}", g_code) } else { g_name },
                    categoria: get_val("grupo_categoria"),
                    lider: get_val("grupo_lider"),
                    activo: true,
                    fecha_creacion: get_val("grupo_fecha_creacion"),
                    plan: get_val("grupo_plan"),
                });
            }
        }

        // Extraer Investigador
        let inv_ced = get_val("investigador_cedula");
        if !inv_ced.is_empty() {
            let existing = investigadores.iter().any(|i| i.cedula == inv_ced);
            if !existing {
                investigadores.push(Investigador {
                    id: Some(inv_ced.clone()),
                    cedula: inv_ced.clone(),
                    nombres: get_val("investigador_nombres"),
                    apellidos: get_val("investigador_apellidos"),
                    email: get_val("investigador_email"),
                    activo: true,
                    grupo_id: None,
                });
            }
        }

        // Extraer Producto
        let prod_titulo = get_val("producto_titulo");
        if !prod_titulo.is_empty() {
            let anio = get_val("producto_anio").parse::<i32>().ok();
            let val = get_val("producto_validacion");
            let is_valid = val.eq_ignore_ascii_case("validado");
            let pid = get_val("producto_id");

            productos.push(Producto {
                id: if pid.is_empty() { None } else { Some(pid) },
                titulo: prod_titulo,
                tipo: get_val("producto_tipo"),
                categoria: get_val("producto_categoria"),
                validado: is_valid,
                anio,
                investigador_id: Some(inv_ced.clone()),
                investigador_cedula: Some(inv_ced),
                grupo_id: None,
                raw: None,
                gran_categoria: get_val("producto_gran_categoria"),
                codigo_minciencias: get_val("codigo_minciencias"),
                validacion: if val.is_empty() { "No validado".to_string() } else { val },
                activo: true,
            });
        }
    }

    Ok(DatosCsvImportados {
        grupos,
        investigadores,
        productos,
    })
}
