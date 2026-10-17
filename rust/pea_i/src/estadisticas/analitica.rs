//! Módulo de analítica y cálculo estadístico de la producción científica.

use crate::modelos::entidades::{normalizar_gran_categoria, Grupo, Investigador, Producto};
use crate::modelos::multilista::Multilist;
use chrono::Datelike;

#[derive(Debug, Clone)]
pub struct ResumenKPIs {
    pub total_grupos: usize,
    pub grupos_activos: usize,
    pub total_investigadores: usize,
    pub investigadores_activos: usize,
    pub total_productos: usize,
    pub productos_validados: usize,
    pub productos_no_validados: usize,
    pub productos_en_revision: usize,
}

#[derive(Debug, Clone)]
pub struct EstadisticaDescriptiva {
    pub total: usize,
    pub promedio: f64,
    pub mediana: f64,
    pub minimo: usize,
    pub maximo: usize,
}

#[derive(Debug, Clone)]
pub struct ConteoItem {
    pub etiqueta: String,
    pub conteo: usize,
    pub porcentaje: f64,
}

#[derive(Debug, Clone)]
pub struct AnaliticaCompleta {
    pub kpis: ResumenKPIs,
    pub descriptiva_investigadores: EstadisticaDescriptiva,
    pub productos_por_anio: Vec<ConteoItem>,
    pub productos_por_gran_categoria: Vec<ConteoItem>,
    pub productos_por_tipo_top10: Vec<ConteoItem>,
    pub histograma_investigadores: Vec<ConteoItem>,
}

#[derive(Debug, Clone, Default)]
pub struct FiltroEstadisticas {
    pub grupo_id: Option<i64>,
    pub investigador_cedula: Option<String>,
    pub anio_inicio: Option<i32>,
    pub anio_fin: Option<i32>,
}

impl FiltroEstadisticas {
    pub fn matches_producto(&self, p: &Producto) -> bool {
        if let Some(gid) = self.grupo_id {
            if p.grupo_id != Some(gid) {
                return false;
            }
        }
        if let Some(ced) = &self.investigador_cedula {
            let p_ced = p.investigador_id.as_deref().unwrap_or("");
            if !p_ced.eq_ignore_ascii_case(ced) {
                return false;
            }
        }
        if let Some(ini) = self.anio_inicio {
            if let Some(y) = p.anio {
                if y < ini {
                    return false;
                }
            } else {
                return false;
            }
        }
        if let Some(fin) = self.anio_fin {
            if let Some(y) = p.anio {
                if y > fin {
                    return false;
                }
            } else {
                return false;
            }
        }
        true
    }
}

/// Genera el reporte analítico completo aplicando los filtros especificados.
pub fn calcular_analitica(multilist: &Multilist, filtro: &FiltroEstadisticas) -> AnaliticaCompleta {
    let grupos = multilist.iterate_groups(false);
    let investigadores = multilist.iterate_investigadores(filtro.grupo_id, false);
    let todos_prods = multilist.iterate_productos(filtro.grupo_id, filtro.investigador_cedula.as_deref(), None, false);

    // Filtrar productos
    let productos_filtrados: Vec<Producto> = todos_prods
        .into_iter()
        .filter(|p| filtro.matches_producto(p))
        .collect();

    // 1. KPIs
    let total_grupos = grupos.len();
    let grupos_activos = grupos.iter().filter(|g| g.activo).count();

    let total_investigadores = investigadores.len();
    let investigadores_activos = investigadores.iter().filter(|i| i.activo).count();

    let total_productos = productos_filtrados.len();
    let productos_validados = productos_filtrados
        .iter()
        .filter(|p| p.validado || p.validacion.eq_ignore_ascii_case("validado"))
        .count();
    let productos_en_revision = productos_filtrados
        .iter()
        .filter(|p| p.validacion.eq_ignore_ascii_case("en revision") || p.validacion.eq_ignore_ascii_case("en revisión"))
        .count();
    let productos_no_validados = total_productos.saturating_sub(productos_validados + productos_en_revision);

    let kpis = ResumenKPIs {
        total_grupos,
        grupos_activos,
        total_investigadores,
        investigadores_activos,
        total_productos,
        productos_validados,
        productos_no_validados,
        productos_en_revision,
    };

    // 2. Estadística Descriptiva (Distribución de productos por investigador)
    let mut prods_per_inv: Vec<usize> = Vec::new();
    for inv in &investigadores {
        let count = productos_filtrados
            .iter()
            .filter(|p| p.investigador_id.as_deref().unwrap_or("").eq_ignore_ascii_case(&inv.cedula))
            .count();
        prods_per_inv.push(count);
    }
    prods_per_inv.sort_unstable();

    let descriptiva_investigadores = if prods_per_inv.is_empty() {
        EstadisticaDescriptiva {
            total: 0,
            promedio: 0.0,
            mediana: 0.0,
            minimo: 0,
            maximo: 0,
        }
    } else {
        let sum: usize = prods_per_inv.iter().sum();
        let prom = sum as f64 / prods_per_inv.len() as f64;
        let mid = prods_per_inv.len() / 2;
        let med = if prods_per_inv.len() % 2 == 0 {
            (prods_per_inv[mid - 1] + prods_per_inv[mid]) as f64 / 2.0
        } else {
            prods_per_inv[mid] as f64
        };
        let min = *prods_per_inv.first().unwrap();
        let max = *prods_per_inv.last().unwrap();
        EstadisticaDescriptiva {
            total: sum,
            promedio: prom,
            mediana: med,
            minimo: min,
            maximo: max,
        }
    };

    // 3. Distribución por año
    let mut year_counts: std::collections::BTreeMap<i32, usize> = std::collections::BTreeMap::new();
    for p in &productos_filtrados {
        if let Some(y) = p.anio {
            if (1950..=2030).contains(&y) {
                *year_counts.entry(y).or_insert(0) += 1;
            }
        }
    }
    let total_con_anio: usize = year_counts.values().sum();
    let productos_por_anio: Vec<ConteoItem> = year_counts
        .into_iter()
        .map(|(anio, count)| ConteoItem {
            etiqueta: anio.to_string(),
            conteo: count,
            porcentaje: if total_con_anio > 0 {
                (count as f64 / total_con_anio as f64) * 100.0
            } else {
                0.0
            },
        })
        .collect();

    // 4. Distribución por Gran Categoría MinCiencias
    let mut gran_cat_counts: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
    for code in ["GNC", "DTI", "ASC", "FRH", "Sin clasificar"] {
        gran_cat_counts.insert(code.to_string(), 0);
    }
    for p in &productos_filtrados {
        let norm = normalizar_gran_categoria(&p.gran_categoria);
        *gran_cat_counts.entry(norm).or_insert(0) += 1;
    }
    let mut productos_por_gran_categoria: Vec<ConteoItem> = gran_cat_counts
        .into_iter()
        .map(|(gc, count)| ConteoItem {
            etiqueta: gc,
            conteo: count,
            porcentaje: if total_productos > 0 {
                (count as f64 / total_productos as f64) * 100.0
            } else {
                0.0
            },
        })
        .collect();
    productos_por_gran_categoria.sort_by(|a, b| b.conteo.cmp(&a.conteo));

    // 5. Productos por tipo (Top 10)
    let mut type_counts: std::collections::HashMap<String, usize> = std::collections::HashMap::new();
    for p in &productos_filtrados {
        let t = if p.tipo.trim().is_empty() {
            "Sin clasificar".to_string()
        } else {
            p.tipo.trim().to_string()
        };
        *type_counts.entry(t).or_insert(0) += 1;
    }
    let mut type_vec: Vec<ConteoItem> = type_counts
        .into_iter()
        .map(|(tipo, count)| ConteoItem {
            etiqueta: tipo,
            conteo: count,
            porcentaje: if total_productos > 0 {
                (count as f64 / total_productos as f64) * 100.0
            } else {
                0.0
            },
        })
        .collect();
    type_vec.sort_by(|a, b| b.conteo.cmp(&a.conteo));
    type_vec.truncate(10);
    let productos_por_tipo_top10 = type_vec;

    // 6. Histograma: distribución de productividad de investigadores
    let mut bins = [
        ("0 productos", 0),
        ("1 a 2 productos", 0),
        ("3 a 5 productos", 0),
        ("6 a 10 productos", 0),
        ("Más de 10 productos", 0),
    ];
    for count in &prods_per_inv {
        match *count {
            0 => bins[0].1 += 1,
            1..=2 => bins[1].1 += 1,
            3..=5 => bins[2].1 += 1,
            6..=10 => bins[3].1 += 1,
            _ => bins[4].1 += 1,
        }
    }
    let total_inv_conteo = prods_per_inv.len();
    let histograma_investigadores: Vec<ConteoItem> = bins
        .iter()
        .map(|(label, count)| ConteoItem {
            etiqueta: label.to_string(),
            conteo: *count,
            porcentaje: if total_inv_conteo > 0 {
                (*count as f64 / total_inv_conteo as f64) * 100.0
            } else {
                0.0
            },
        })
        .collect();

    AnaliticaCompleta {
        kpis,
        descriptiva_investigadores,
        productos_por_anio,
        productos_por_gran_categoria,
        productos_por_tipo_top10,
        histograma_investigadores,
    }
}
