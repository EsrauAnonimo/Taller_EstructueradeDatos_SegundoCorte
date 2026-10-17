//! Exportación e importación de la Multilista completa a formato tabular CSV.

use crate::modelos::multilista::Multilist;
use std::fs::File;
use std::path::Path;

/// Exporta todos los registros de la Multilista en un archivo CSV plano.
pub fn exportar_csv(multilist: &Multilist, ruta: impl AsRef<Path>) -> Result<usize, String> {
    if let Some(parent) = ruta.as_ref().parent() {
        if !parent.as_os_str().is_empty() {
            let _ = std::fs::create_dir_all(parent);
        }
    }

    let file = File::create(ruta.as_ref())
        .map_err(|e| format!("No se pudo crear archivo CSV: {}", e))?;

    let mut wtr = csv::WriterBuilder::new().has_headers(true).from_writer(file);

    wtr.write_record([
        "grupo_id",
        "grupo_codigo",
        "grupo_nombre",
        "grupo_categoria",
        "grupo_lider",
        "grupo_activo",
        "grupo_fecha_creacion",
        "investigador_id",
        "investigador_cedula",
        "investigador_nombres",
        "investigador_apellidos",
        "investigador_email",
        "investigador_activo",
        "producto_id",
        "producto_titulo",
        "producto_tipo",
        "producto_categoria",
        "producto_gran_categoria",
        "producto_codigo_minciencias",
        "producto_anio",
        "producto_validacion",
        "producto_validado",
        "producto_activo",
    ])
    .map_err(|e| format!("Error escribiendo encabezados CSV: {}", e))?;

    let mut rows_count = 0;
    let mut g_curr = multilist.head_group.clone();

    while let Some(g_node) = g_curr {
        let g = g_node.borrow().data.clone();
        let g_id_str = g.id.map(|i| i.to_string()).unwrap_or_default();
        let g_act_str = g.activo.to_string();

        let mut i_curr = g_node.borrow().sublist.clone();
        if i_curr.is_none() {
            // Fila de grupo sin investigadores
            wtr.write_record([
                &g_id_str,
                &g.codigo_gruplac,
                &g.nombre,
                &g.categoria,
                &g.lider,
                &g_act_str,
                &g.fecha_creacion,
                "", "", "", "", "", "",
                "", "", "", "", "", "", "", "", "", "",
            ])
            .map_err(|e| format!("Error escribiendo fila CSV: {}", e))?;
            rows_count += 1;
        }

        while let Some(i_node) = i_curr {
            let inv = i_node.borrow().data.clone();
            let inv_id_str = inv.id.unwrap_or_default();
            let inv_act_str = inv.activo.to_string();

            let mut p_curr = i_node.borrow().sublist.clone();
            if p_curr.is_none() {
                // Fila de investigador sin productos
                wtr.write_record([
                    &g_id_str,
                    &g.codigo_gruplac,
                    &g.nombre,
                    &g.categoria,
                    &g.lider,
                    &g_act_str,
                    &g.fecha_creacion,
                    &inv_id_str,
                    &inv.cedula,
                    &inv.nombres,
                    &inv.apellidos,
                    &inv.email,
                    &inv_act_str,
                    "", "", "", "", "", "", "", "", "", "",
                ])
                .map_err(|e| format!("Error escribiendo fila CSV: {}", e))?;
                rows_count += 1;
            }

            while let Some(p_node) = p_curr {
                let p = p_node.borrow().data.clone();
                let p_id_str = p.id.unwrap_or_default();
                let p_anio_str = p.anio.map(|y| y.to_string()).unwrap_or_default();
                let p_val_str = p.validado.to_string();
                let p_act_str = p.activo.to_string();

                wtr.write_record([
                    &g_id_str,
                    &g.codigo_gruplac,
                    &g.nombre,
                    &g.categoria,
                    &g.lider,
                    &g_act_str,
                    &g.fecha_creacion,
                    &inv_id_str,
                    &inv.cedula,
                    &inv.nombres,
                    &inv.apellidos,
                    &inv.email,
                    &inv_act_str,
                    &p_id_str,
                    &p.titulo,
                    &p.tipo,
                    &p.categoria,
                    &p.gran_categoria,
                    &p.codigo_minciencias,
                    &p_anio_str,
                    &p.validacion,
                    &p_val_str,
                    &p_act_str,
                ])
                .map_err(|e| format!("Error escribiendo fila CSV: {}", e))?;
                rows_count += 1;

                p_curr = p_node.borrow().next.clone();
            }

            i_curr = i_node.borrow().next.clone();
        }

        g_curr = g_node.borrow().next.clone();
    }

    wtr.flush()
        .map_err(|e| format!("Error vaciando buffer CSV: {}", e))?;
    Ok(rows_count)
}
