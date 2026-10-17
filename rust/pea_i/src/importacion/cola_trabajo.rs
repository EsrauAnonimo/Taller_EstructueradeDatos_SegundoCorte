//! Procesador FIFO de la cola de importación (`Queue<TareaImportacion>`).

use super::csv_import;
use super::scienti;
use crate::crud::{GrupoCRUD, InvestigadorCRUD, ProductoCRUD};
use crate::modelos::cola::{Queue, TareaImportacion};

pub struct ReporteProcesamiento {
    pub total_procesados: usize,
    pub exitosos: usize,
    pub fallidos: usize,
    pub detalles: Vec<String>,
}

/// Procesa secuencialmente todos los elementos de la cola en estricto orden FIFO.
pub fn procesar_cola(
    cola: &mut Queue<TareaImportacion>,
    grupo_crud: &GrupoCRUD,
    inv_crud: &InvestigadorCRUD,
    prod_crud: &ProductoCRUD,
) -> ReporteProcesamiento {
    let mut exitosos = 0;
    let mut fallidos = 0;
    let mut detalles = Vec::new();
    let total = cola.len();

    while let Some(tarea) = cola.dequeue() {
        match tarea {
            TareaImportacion::Url { url, etiqueta } => {
                match scienti::download_group(&url, 35) {
                    Ok(res) => {
                        // 1. Insertar o actualizar grupo
                        let mut grupo = res.grupo;
                        let gid = match grupo_crud.create(&mut grupo) {
                            Ok(id) => id,
                            Err(_) => {
                                // Si ya existe por código, obtenerlo
                                if let Some(existing) = grupo_crud.get_by_code(&grupo.codigo_gruplac) {
                                    existing.id.unwrap_or(1)
                                } else {
                                    grupo_crud.next_id()
                                }
                            }
                        };

                        // 2. Insertar investigadores
                        let mut primary_cedula = None;
                        for mut inv in res.investigadores {
                            inv.grupo_id = Some(gid);
                            if primary_cedula.is_none() {
                                primary_cedula = Some(inv.cedula.clone());
                            }
                            let _ = inv_crud.create(&mut inv);
                        }

                        // Fallback de investigador si no había integrantes pero sí productos
                        if primary_cedula.is_none() && !res.productos.is_empty() {
                            let mut fallback = crate::modelos::entidades::Investigador::new(
                                None,
                                format!("INV-{}", gid),
                                grupo.lider.clone(),
                                "",
                                "",
                                Some(gid),
                            );
                            let _ = inv_crud.create(&mut fallback);
                            primary_cedula = Some(fallback.cedula);
                        }

                        // 3. Insertar productos
                        for mut prod in res.productos {
                            prod.grupo_id = Some(gid);
                            if prod.investigador_id.is_none() || prod.investigador_id.as_deref() == Some("") {
                                prod.investigador_id = primary_cedula.clone();
                                prod.investigador_cedula = primary_cedula.clone();
                            }
                            let _ = prod_crud.create(&mut prod);
                        }

                        exitosos += 1;
                        detalles.push(format!("✓ URL [{}]: Éxito ({})", etiqueta, res.resumen));
                    }
                    Err(e) => {
                        fallidos += 1;
                        detalles.push(format!("✗ URL [{}]: Error: {}", etiqueta, e));
                    }
                }
            }
            TareaImportacion::ArchivoCsv { ruta, etiqueta } => {
                match csv_import::cargar_desde_csv(&ruta) {
                    Ok(res) => {
                        let mut gid_map: std::collections::HashMap<String, i64> = std::collections::HashMap::new();

                        // 1. Grupos
                        for mut g in res.grupos {
                            let code = g.codigo_gruplac.clone();
                            let gid = match grupo_crud.create(&mut g) {
                                Ok(id) => id,
                                Err(_) => {
                                    if let Some(existing) = grupo_crud.get_by_code(&code) {
                                        existing.id.unwrap_or(1)
                                    } else {
                                        grupo_crud.next_id()
                                    }
                                }
                            };
                            gid_map.insert(code, gid);
                        }

                        let default_gid = gid_map.values().next().copied().unwrap_or(1);

                        // 2. Investigadores
                        let mut first_cedula = None;
                        for mut inv in res.investigadores {
                            if inv.grupo_id.is_none() {
                                inv.grupo_id = Some(default_gid);
                            }
                            if first_cedula.is_none() {
                                first_cedula = Some(inv.cedula.clone());
                            }
                            let _ = inv_crud.create(&mut inv);
                        }

                        // 3. Productos
                        for mut prod in res.productos {
                            if prod.grupo_id.is_none() {
                                prod.grupo_id = Some(default_gid);
                            }
                            if prod.investigador_id.is_none() {
                                prod.investigador_id = first_cedula.clone();
                                prod.investigador_cedula = first_cedula.clone();
                            }
                            let _ = prod_crud.create(&mut prod);
                        }

                        exitosos += 1;
                        detalles.push(format!("✓ CSV [{}]: Éxito importando archivo", etiqueta));
                    }
                    Err(e) => {
                        fallidos += 1;
                        detalles.push(format!("✗ CSV [{}]: Error: {}", etiqueta, e));
                    }
                }
            }
        }
    }

    ReporteProcesamiento {
        total_procesados: total,
        exitosos,
        fallidos,
        detalles,
    }
}
