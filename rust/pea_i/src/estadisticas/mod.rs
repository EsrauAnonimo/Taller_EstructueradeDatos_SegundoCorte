pub mod analitica;
pub mod ascii_charts;

pub use analitica::{calcular_analitica, AnaliticaCompleta, FiltroEstadisticas, ResumenKPIs};
pub use ascii_charts::{render_bar_chart, render_dashboard};
