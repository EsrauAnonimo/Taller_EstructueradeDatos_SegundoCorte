//! Persistencia en formato JSON idéntico a la versión Python (`datos.json`).
//!
//! Permite interoperabilidad total entre las implementaciones en Python y Rust.

use crate::modelos::entidades::{Grupo, Investigador, Producto};
use crate::modelos::multilista::Multilist;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::{BufReader, BufWriter, Write};
use std::path::Path;

#[derive(Serialize, Deserialize)]
struct SchemaInvestigadorJson {
    investigador: Investigador,
    #[serde(default)]
    productos: Vec<Producto>,
}

#[derive(Serialize, Deserialize)]
struct SchemaGrupoJson {
    grupo: Grupo,
    #[serde(default)]
    investigadores: Vec<SchemaInvestigadorJson>,
}

#[derive(Serialize, Deserialize)]
struct RootJson {
    #[serde(default)]
    grupos: Vec<SchemaGrupoJson>,
}

/// Guarda la Multilista en un archivo JSON estructurado idéntico a Python.
pub fn guardar_json(multilist: &Multilist, ruta: impl AsRef<Path>) -> Result<(), String> {
    let mut root_grupos = Vec::new();

    let mut curr_g = multilist.head_group.clone();
    while let Some(g_node) = curr_g {
        let grupo = g_node.borrow().data.clone();
        let gid = grupo.id;

        let mut inv_schema_list = Vec::new();
        let mut curr_i = g_node.borrow().sublist.clone();
        while let Some(i_node) = curr_i {
            let mut inv = i_node.borrow().data.clone();
            if inv.grupo_id.is_none() {
                inv.grupo_id = gid;
            }
            let inv_ced = inv.cedula.clone();

            let mut prod_list = Vec::new();
            let mut curr_p = i_node.borrow().sublist.clone();
            while let Some(p_node) = curr_p {
                let mut prod = p_node.borrow().data.clone();
                if prod.grupo_id.is_none() {
                    prod.grupo_id = gid;
                }
                if prod.investigador_id.is_none() {
                    prod.investigador_id = Some(inv_ced.clone());
                }
                if prod.investigador_cedula.is_none() {
                    prod.investigador_cedula = Some(inv_ced.clone());
                }
                prod_list.push(prod);
                curr_p = p_node.borrow().next.clone();
            }

            inv_schema_list.push(SchemaInvestigadorJson {
                investigador: inv,
                productos: prod_list,
            });

            curr_i = i_node.borrow().next.clone();
        }

        root_grupos.push(SchemaGrupoJson {
            grupo,
            investigadores: inv_schema_list,
        });

        curr_g = g_node.borrow().next.clone();
    }

    let root = RootJson { grupos: root_grupos };

    // Crear directorio padre si no existe
    if let Some(parent) = ruta.as_ref().parent() {
        if !parent.as_os_str().is_empty() {
            let _ = std::fs::create_dir_all(parent);
        }
    }

    let file = File::create(ruta.as_ref())
        .map_err(|e| format!("No se pudo crear el archivo JSON: {}", e))?;
    let mut writer = BufWriter::new(file);

    serde_json::to_writer_pretty(&mut writer, &root)
        .map_err(|e| format!("Error serializando JSON: {}", e))?;
    writer.flush().map_err(|e| format!("Error escribiendo JSON: {}", e))?;

    Ok(())
}

/// Carga los datos desde un archivo JSON reconstruyendo la Multilista jerárquica.
pub fn cargar_json(ruta: impl AsRef<Path>) -> Result<Multilist, String> {
    let file = File::open(ruta.as_ref())
        .map_err(|e| format!("No se pudo abrir el archivo JSON: {}", e))?;
    let reader = BufReader::new(file);

    let root: RootJson = serde_json::from_reader(reader)
        .map_err(|e| format!("Error decodificando estructura JSON: {}", e))?;

    let mut multilist = Multilist::new();

    for g_entry in root.grupos {
        let grupo = g_entry.grupo;
        let g_node = multilist.add_group(grupo.clone());
        let gid = grupo.id.unwrap_or(multilist.len_groups() as i64);
        g_node.borrow_mut().data.id = Some(gid);

        for i_entry in g_entry.investigadores {
            let mut inv = i_entry.investigador;
            if inv.grupo_id.is_none() {
                inv.grupo_id = Some(gid);
            }
            let cedula = inv.cedula.clone();

            multilist.add_investigador(gid, inv);

            for mut prod in i_entry.productos {
                if prod.grupo_id.is_none() {
                    prod.grupo_id = Some(gid);
                }
                if prod.investigador_id.is_none() {
                    prod.investigador_id = Some(cedula.clone());
                }
                if prod.investigador_cedula.is_none() {
                    prod.investigador_cedula = Some(cedula.clone());
                }
                multilist.add_producto(&cedula, prod);
            }
        }
    }

    Ok(multilist)
}
