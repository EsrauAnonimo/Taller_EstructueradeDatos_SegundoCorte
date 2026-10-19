#![allow(dead_code, unused_imports)]

mod crud;
mod estadisticas;
mod importacion;
mod menu;
mod modelos;
mod persistencia;

use menu::ConsolaApp;
use modelos::multilista::Multilist;
use persistencia::cargar_json;
use std::path::Path;

fn main() {
    println!("Iniciando PEA-i (Versión Rust - Consola Interactiva)...");

    // Buscar archivo de datos existente en las rutas usuales del proyecto
    let posibles_rutas = [
        "../../python/datos/datos.json",
        "../python/datos/datos.json",
        "python/datos/datos.json",
        "datos/datos.json",
        "datos.json",
    ];

    let mut ruta_seleccionada = "datos/datos.json".to_string();
    let mut multilist = Multilist::new();

    for r in posibles_rutas {
        if Path::new(r).exists() {
            println!("Cargando datos iniciales desde '{}'...", r);
            match cargar_json(r) {
                Ok(ml) => {
                    println!(
                        "✓ Datos cargados: {} grupos registrados.",
                        ml.len_groups()
                    );
                    multilist = ml;
                    ruta_seleccionada = r.to_string();
                    break;
                }
                Err(e) => {
                    eprintln!("Advertencia al leer '{}': {}", r, e);
                }
            }
        }
    }

    if multilist.is_empty() {
        println!("Iniciando con Multilista en memoria vacía.");
    }

    let mut app = ConsolaApp::new(multilist, ruta_seleccionada);
    app.run();
}
