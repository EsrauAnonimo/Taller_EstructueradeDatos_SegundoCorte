//! Generador de gráficos y tablas ASCII para terminal de consola.

use super::analitica::{AnaliticaCompleta, ConteoItem};

const BAR_CHAR: char = '█';
const MAX_BAR_WIDTH: usize = 35;

/// Dibuja un gráfico de barras horizontal en ASCII.
pub fn render_bar_chart(title: &str, items: &[ConteoItem]) -> String {
    let mut out = String::new();
    out.push_str(&format!("\n─── {} ───\n", title));

    if items.is_empty() {
        out.push_str("   (Sin datos para graficar)\n");
        return out;
    }

    let max_count = items.iter().map(|it| it.conteo).max().unwrap_or(1).max(1);
    let max_label_len = items.iter().map(|it| it.etiqueta.len()).max().unwrap_or(10).min(30);

    for it in items {
        let label = if it.etiqueta.len() > 30 {
            format!("{}...", &it.etiqueta[..27])
        } else {
            it.etiqueta.clone()
        };

        let bar_len = ((it.conteo as f64 / max_count as f64) * MAX_BAR_WIDTH as f64).round() as usize;
        let bar: String = std::iter::repeat(BAR_CHAR).take(bar_len).collect();

        out.push_str(&format!(
            " {:<width$} │ {:<bar_width$}  {:>4} ({:>5.1}%)\n",
            label,
            bar,
            it.conteo,
            it.porcentaje,
            width = max_label_len,
            bar_width = MAX_BAR_WIDTH,
        ));
    }

    out
}

/// Dibuja el panel completo del dashboard analítico en formato ASCII.
pub fn render_dashboard(data: &AnaliticaCompleta) -> String {
    let mut s = String::new();

    s.push_str("╔════════════════════════════════════════════════════════════════════════════════╗\n");
    s.push_str("║                   PANEL DE ANALÍTICA Y ESTADÍSTICAS PEA-i                      ║\n");
    s.push_str("╚════════════════════════════════════════════════════════════════════════════════╝\n\n");

    // Tarjetas KPI
    s.push_str("┌───────────────────────────┬───────────────────────────┬───────────────────────────┐\n");
    s.push_str("│ GRUPOS DE INVESTIGACIÓN   │ INVESTIGADORES            │ PRODUCTOS REGISTRADOS     │\n");
    s.push_str(&format!(
        "│ Total: {:<5} Activos: {:<5}│ Total: {:<5} Activos: {:<5}│ Total: {:<5} Valid: {:<5} │\n",
        data.kpis.total_grupos,
        data.kpis.grupos_activos,
        data.kpis.total_investigadores,
        data.kpis.investigadores_activos,
        data.kpis.total_productos,
        data.kpis.productos_validados,
    ));
    s.push_str(&format!(
        "│ Inactivos: {:<14}│ Inactivos: {:<14}│ Rev: {:<5} No val: {:<6}│\n",
        data.kpis.total_grupos.saturating_sub(data.kpis.grupos_activos),
        data.kpis.total_investigadores.saturating_sub(data.kpis.investigadores_activos),
        data.kpis.productos_en_revision,
        data.kpis.productos_no_validados,
    ));
    s.push_str("└───────────────────────────┴───────────────────────────┴───────────────────────────┘\n");

    // Resumen descriptivo
    let d = &data.descriptiva_investigadores;
    s.push_str("\n┌───────────────────────────────────────────────────────────────────────────────┐\n");
    s.push_str("│ RESUMEN ESTADÍSTICO DESCRIPTIVO (PRODUCTIVIDAD POR INVESTIGADOR)              │\n");
    s.push_str(&format!(
        "│ Total: {:<5} │ Promedio: {:<6.2} │ Mediana: {:<5.1} │ Mínimo: {:<4} │ Máximo: {:<5} │\n",
        d.total, d.promedio, d.mediana, d.minimo, d.maximo
    ));
    s.push_str("└───────────────────────────────────────────────────────────────────────────────┘\n");

    // Gráfico 1: Por Gran Categoría MinCiencias
    s.push_str(&render_bar_chart(
        "DISTRIBUCIÓN POR GRAN CATEGORÍA MINCIENCIAS (GNC, DTI, ASC, FRH)",
        &data.productos_por_gran_categoria,
    ));

    // Gráfico 2: Histograma de productividad de investigadores
    s.push_str(&render_bar_chart(
        "HISTOGRAMA: PRODUCTOS POR INVESTIGADOR",
        &data.histograma_investigadores,
    ));

    // Gráfico 3: Productos por año (últimos años registrados)
    s.push_str(&render_bar_chart(
        "DISTRIBUCIÓN DE PRODUCTOS POR AÑO",
        &data.productos_por_anio,
    ));

    // Gráfico 4: Top 10 tipos de productos
    s.push_str(&render_bar_chart(
        "TOP 10 TIPOS DE PRODUCTOS CIENTÍFICOS",
        &data.productos_por_tipo_top10,
    ));

    s
}
