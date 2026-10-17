//! Interfaz de consola interactiva con bucle principal y submenús numerados.

use crate::crud::{GrupoCRUD, InvestigadorCRUD, ProductoCRUD};
use crate::estadisticas::{calcular_analitica, render_dashboard, FiltroEstadisticas};
use crate::importacion::cola_trabajo;
use crate::modelos::cola::{Queue, TareaImportacion};
use crate::modelos::entidades::{Grupo, Investigador, Producto, CATEGORIAS_PRODUCTO, ESTADOS_VALIDACION};
use crate::modelos::multilista::Multilist;
use crate::modelos::pila::{OperacionDeshacer, Stack};
use crate::persistencia::{cargar_json, exportar_csv, guardar_json};

use std::cell::RefCell;
use std::io::{self, Write};
use std::rc::Rc;

pub struct ConsolaApp {
    pub multilist: Rc<RefCell<Multilist>>,
    pub grupo_crud: GrupoCRUD,
    pub inv_crud: InvestigadorCRUD,
    pub prod_crud: ProductoCRUD,
    pub undo_stack: Stack<OperacionDeshacer>,
    pub import_queue: Queue<TareaImportacion>,
    pub ruta_datos: String,
}

impl ConsolaApp {
    pub fn new(multilist: Multilist, ruta_datos: String) -> Self {
        let ml_rc = Rc::new(RefCell::new(multilist));
        let grupo_crud = GrupoCRUD::new(Rc::clone(&ml_rc));
        let inv_crud = InvestigadorCRUD::new(Rc::clone(&ml_rc));
        let prod_crud = ProductoCRUD::new(Rc::clone(&ml_rc));

        Self {
            multilist: ml_rc,
            grupo_crud,
            inv_crud,
            prod_crud,
            undo_stack: Stack::new(),
            import_queue: Queue::new(),
            ruta_datos,
        }
    }

    /// Bucle principal interactivo
    pub fn run(&mut self) {
        loop {
            self.mostrar_encabezado_principal();
            println!(" 1. Gestión de Grupos de Investigación (CRUD)");
            println!(" 2. Gestión de Investigadores (CRUD)");
            println!(" 3. Gestión de Productos de Investigación (CRUD)");
            println!(" 4. Pila de Deshacer (Undo Stack de Eliminaciones) [{}]", self.undo_stack.len());
            println!(" 5. Cola de Importación (FIFO: GrupLAC / CSV) [{}]", self.import_queue.len());
            println!(" 6. Estadísticas y Analítica de Producción Científica");
            println!(" 7. Persistencia de Datos (Guardar / Cargar / Exportar CSV)");
            println!(" 8. Salir del programa");
            println!("─────────────────────────────────────────────────────────────────────────────");

            let opc = leer_linea("Seleccione una opción (1-8): ");
            match opc.trim() {
                "1" => self.menu_grupos(),
                "2" => self.menu_investigadores(),
                "3" => self.menu_productos(),
                "4" => self.menu_deshacer(),
                "5" => self.menu_cola_importacion(),
                "6" => self.menu_estadisticas(),
                "7" => self.menu_persistencia(),
                "8" => {
                    let confirm = leer_linea("¿Desea guardar los datos antes de salir? (S/N): ");
                    if confirm.trim().eq_ignore_ascii_case("s") {
                        if let Err(e) = guardar_json(&self.multilist.borrow(), &self.ruta_datos) {
                            println!("Error guardando: {}", e);
                        } else {
                            println!("✓ Datos guardados exitosamente en '{}'", self.ruta_datos);
                        }
                    }
                    println!("\n¡Gracias por utilizar PEA-i (Versión Rust)! Hasta pronto.\n");
                    break;
                }
                _ => {
                    println!("Opción no válida. Por favor ingrese un número del 1 al 8.");
                    pausar();
                }
            }
        }
    }

    fn mostrar_encabezado_principal(&self) {
        let ml = self.multilist.borrow();
        let total_g = ml.len_groups();
        let total_i = ml.iterate_investigadores(None, false).len();
        let total_p = ml.iterate_productos(None, None, None, false).len();
        let nu = self.undo_stack.len();
        let nq = self.import_queue.len();

        println!("\n╔═══════════════════════════════════════════════════════════════════════════╗");
        println!("║                      PEA-i — PLATAFORMA DE INVESTIGACIÓN                  ║");
        println!("║                  Consola Interactiva en Rust (100% Terminal)              ║");
        println!("╚═══════════════════════════════════════════════════════════════════════════╝");
        println!(
            " Estado: Grupos: {} │ Investigadores: {} │ Productos: {} │ Deshacer: {} │ Cola: {}",
            total_g, total_i, total_p, nu, nq
        );
        println!(" Archivo de persistencia: {}", self.ruta_datos);
        println!("─────────────────────────────────────────────────────────────────────────────");
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 1. SUBMENÚ GRUPOS
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_grupos(&mut self) {
        loop {
            println!("\n┌────────────────────────────────────────────────────────┐");
            println!("│             GESTIÓN DE GRUPOS DE INVESTIGACIÓN         │");
            println!("└────────────────────────────────────────────────────────┘");
            println!(" 1. Listar todos los grupos activos");
            println!(" 2. Listar todos los grupos (incluyendo inactivos)");
            println!(" 3. Buscar grupo por ID o Código GrupLAC");
            println!(" 4. Registrar nuevo grupo");
            println!(" 5. Editar datos de un grupo");
            println!(" 6. Desactivar grupo (Eliminación lógica)");
            println!(" 7. Activar grupo");
            println!(" 8. Eliminar grupo físicamente (Apila en Deshacer)");
            println!(" 9. Ver integrantes y productos de un grupo");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => self.listar_grupos(true),
                "2" => self.listar_grupos(false),
                "3" => self.buscar_grupo(),
                "4" => self.crear_grupo(),
                "5" => self.editar_grupo(),
                "6" => self.desactivar_grupo(),
                "7" => self.activar_grupo(),
                "8" => self.eliminar_grupo_fisicamente(),
                "9" => self.ver_detalle_grupo(),
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }

    fn listar_grupos(&self, only_active: bool) {
        let grupos = self.grupo_crud.list_all(only_active);
        println!("\n--- LISTA DE GRUPOS ({}) ---", if only_active { "Activos" } else { "Todos" });
        if grupos.is_empty() {
            println!("No hay grupos registrados.");
        } else {
            println!("{:<5} │ {:<14} │ {:<32} │ {:<6} │ {:<18} │ {:<6}", "ID", "CÓDIGO", "NOMBRE", "CAT", "LÍDER", "ESTADO");
            println!("──────┼────────────────┼──────────────────────────────────┼────────┼────────────────────┼───────");
            for g in grupos {
                let id_s = g.id.map(|i| i.to_string()).unwrap_or_else(|| "-".to_string());
                let nom = if g.nombre.len() > 30 { format!("{}...", &g.nombre[..27]) } else { g.nombre };
                let lid = if g.lider.len() > 18 { format!("{}...", &g.lider[..15]) } else { g.lider };
                let est = if g.activo { "Activo" } else { "Inact." };
                println!("{:<5} │ {:<14} │ {:<32} │ {:<6} │ {:<18} │ {:<6}", id_s, g.codigo_gruplac, nom, g.categoria, lid, est);
            }
        }
        pausar();
    }

    fn buscar_grupo(&self) {
        let q = leer_linea("Ingrese ID numérico o Código de GrupLAC: ");
        if let Ok(id) = q.trim().parse::<i64>() {
            if let Some(g) = self.grupo_crud.get_by_id(id) {
                mostrar_ficha_grupo(&g);
                pausar();
                return;
            }
        }
        if let Some(g) = self.grupo_crud.get_by_code(q.trim()) {
            mostrar_ficha_grupo(&g);
        } else {
            println!("No se encontró ningún grupo con el criterio '{}'.", q.trim());
        }
        pausar();
    }

    fn crear_grupo(&self) {
        println!("\n--- REGISTRAR NUEVO GRUPO ---");
        let codigo = leer_linea("Código GrupLAC (o Enter para omitir): ");
        let nombre = leer_linea("Nombre del grupo: ");
        if nombre.trim().is_empty() {
            println!("El nombre es obligatorio.");
            pausar();
            return;
        }
        let categoria = leer_linea("Categoría (A1, A, B, C, Reconocido): ");
        let lider = leer_linea("Líder del grupo: ");
        let fecha = leer_linea("Fecha / Año de creación (ej. 2010): ");
        let plan = leer_linea("Plan estratégico / Objetivos: ");

        let mut grupo = Grupo::new(None, codigo, nombre, categoria, lider, fecha, plan);
        match self.grupo_crud.create(&mut grupo) {
            Ok(id) => println!("✓ Grupo creado con éxito con ID {}", id),
            Err(e) => println!("✗ Error creando grupo: {}", e),
        }
        pausar();
    }

    fn editar_grupo(&self) {
        let id_str = leer_linea("Ingrese el ID del grupo a editar: ");
        let id = match id_str.trim().parse::<i64>() {
            Ok(i) => i,
            Err(_) => { println!("ID no válido."); pausar(); return; }
        };

        let g = match self.grupo_crud.get_by_id(id) {
            Some(grp) => grp,
            None => { println!("Grupo no encontrado."); pausar(); return; }
        };

        println!("Grupo actual: '{}' ({})", g.nombre, g.codigo_gruplac);
        println!("(Presione Enter para conservar el valor actual)");

        let nom = leer_linea(&format!("Nuevo nombre [{}]: ", g.nombre));
        let cat = leer_linea(&format!("Nueva categoría [{}]: ", g.categoria));
        let lid = leer_linea(&format!("Nuevo líder [{}]: ", g.lider));
        let plan = leer_linea(&format!("Nuevo plan estratégico: "));
        let fec = leer_linea(&format!("Nueva fecha creación [{}]: ", g.fecha_creacion));

        let ok = self.grupo_crud.update(
            id,
            if nom.trim().is_empty() { None } else { Some(nom.trim().to_string()) },
            if cat.trim().is_empty() { None } else { Some(cat.trim().to_string()) },
            if lid.trim().is_empty() { None } else { Some(lid.trim().to_string()) },
            if plan.trim().is_empty() { None } else { Some(plan.trim().to_string()) },
            if fec.trim().is_empty() { None } else { Some(fec.trim().to_string()) },
        );

        if ok {
            println!("✓ Grupo actualizado exitosamente.");
        } else {
            println!("✗ No se pudo actualizar el grupo.");
        }
        pausar();
    }

    fn desactivar_grupo(&self) {
        let id_str = leer_linea("Ingrese ID del grupo a desactivar: ");
        if let Ok(id) = id_str.trim().parse::<i64>() {
            if self.grupo_crud.deactivate(id) {
                println!("✓ Grupo desactivado lógicamente.");
            } else {
                println!("✗ Grupo no encontrado.");
            }
        } else {
            println!("ID no válido.");
        }
        pausar();
    }

    fn activar_grupo(&self) {
        let id_str = leer_linea("Ingrese ID del grupo a activar: ");
        if let Ok(id) = id_str.trim().parse::<i64>() {
            if self.grupo_crud.activate(id) {
                println!("✓ Grupo activado exitosamente.");
            } else {
                println!("✗ Grupo no encontrado.");
            }
        } else {
            println!("ID no válido.");
        }
        pausar();
    }

    fn eliminar_grupo_fisicamente(&mut self) {
        let id_str = leer_linea("Ingrese ID del grupo a ELIMINAR FÍSICAMENTE: ");
        if let Ok(id) = id_str.trim().parse::<i64>() {
            let confirm = leer_linea("¿Está seguro de eliminar físicamente este grupo y sus sublistas? (S/N): ");
            if confirm.trim().eq_ignore_ascii_case("s") {
                if let Some((grupo, invs)) = self.grupo_crud.delete(id) {
                    let desc = format!("Grupo '{}' con {} investigadores", grupo.nombre, invs.len());
                    self.undo_stack.push(OperacionDeshacer::Grupo {
                        grupo,
                        investigadores: invs,
                    });
                    println!("✓ {} eliminado físicamente. (Guardado en Pila de Deshacer).", desc);
                } else {
                    println!("✗ Grupo no encontrado.");
                }
            } else {
                println!("Operación cancelada.");
            }
        } else {
            println!("ID no válido.");
        }
        pausar();
    }

    fn ver_detalle_grupo(&self) {
        let id_str = leer_linea("Ingrese ID del grupo: ");
        if let Ok(id) = id_str.trim().parse::<i64>() {
            if let Some(g) = self.grupo_crud.get_by_id(id) {
                mostrar_ficha_grupo(&g);
                let invs = self.grupo_crud.list_members(id, true);
                let prods = self.grupo_crud.list_products(id, true);
                println!("\n▶ Integrantes activos ({}):", invs.len());
                for (idx, inv) in invs.iter().enumerate() {
                    println!("  {}. {} (Cédula: {})", idx + 1, inv.nombre_completo(), inv.cedula);
                }
                println!("\n▶ Productos activos ({}):", prods.len());
                for (idx, p) in prods.iter().take(15).enumerate() {
                    let a = p.anio.map(|y| y.to_string()).unwrap_or_else(|| "S/A".to_string());
                    println!("  {}. [{}] {} ({}) - {}", idx + 1, a, p.titulo, p.tipo, p.validacion);
                }
                if prods.len() > 15 {
                    println!("  ... y {} productos más.", prods.len() - 15);
                }
            } else {
                println!("Grupo no encontrado.");
            }
        } else {
            println!("ID no válido.");
        }
        pausar();
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 2. SUBMENÚ INVESTIGADORES
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_investigadores(&mut self) {
        loop {
            println!("\n┌────────────────────────────────────────────────────────┐");
            println!("│             GESTIÓN DE INVESTIGADORES                  │");
            println!("└────────────────────────────────────────────────────────┘");
            println!(" 1. Listar todos los investigadores activos");
            println!(" 2. Listar todos los investigadores (incluyendo inactivos)");
            println!(" 3. Listar investigadores de un grupo");
            println!(" 4. Buscar investigador por cédula");
            println!(" 5. Registrar nuevo investigador");
            println!(" 6. Editar datos de un investigador");
            println!(" 7. Desactivar investigador (Eliminación lógica)");
            println!(" 8. Activar investigador");
            println!(" 9. Eliminar investigador físicamente (Apila en Deshacer)");
            println!(" 10. Ver productos de un investigador");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => self.listar_investigadores(None, true),
                "2" => self.listar_investigadores(None, false),
                "3" => {
                    let id_str = leer_linea("Ingrese ID del grupo: ");
                    if let Ok(id) = id_str.trim().parse::<i64>() {
                        self.listar_investigadores(Some(id), true);
                    } else {
                        println!("ID no válido.");
                        pausar();
                    }
                }
                "4" => self.buscar_investigador(),
                "5" => self.crear_investigador(),
                "6" => self.editar_investigador(),
                "7" => self.desactivar_investigador(),
                "8" => self.activar_investigador(),
                "9" => self.eliminar_investigador_fisicamente(),
                "10" => self.ver_productos_investigador(),
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }

    fn listar_investigadores(&self, group_id: Option<i64>, only_active: bool) {
        let invs = match group_id {
            Some(gid) => self.inv_crud.list_by_group(gid, only_active),
            None => self.inv_crud.list_all(only_active),
        };

        println!("\n--- INVESTIGADORES ({}) ---", invs.len());
        if invs.is_empty() {
            println!("No hay investigadores registrados.");
        } else {
            println!("{:<16} │ {:<32} │ {:<24} │ {:<6} │ {:<6}", "CÉDULA", "NOMBRE COMPLETO", "EMAIL", "GRUPO", "ESTADO");
            println!("─────────────────┼──────────────────────────────────┼──────────────────────────┼────────┼───────");
            for i in invs {
                let nom = i.nombre_completo();
                let nom_s = if nom.len() > 30 { format!("{}...", &nom[..27]) } else { nom };
                let em = if i.email.len() > 22 { format!("{}...", &i.email[..19]) } else { i.email };
                let gid_s = i.grupo_id.map(|g| g.to_string()).unwrap_or_else(|| "-".to_string());
                let est = if i.activo { "Activo" } else { "Inact." };
                println!("{:<16} │ {:<32} │ {:<24} │ {:<6} │ {:<6}", i.cedula, nom_s, em, gid_s, est);
            }
        }
        pausar();
    }

    fn buscar_investigador(&self) {
        let ced = leer_linea("Ingrese la cédula del investigador: ");
        if let Some(i) = self.inv_crud.get_by_cedula(ced.trim(), false) {
            println!("\n╔════════════════════════════════════════════════════════════════╗");
            println!("║ FICHA DE INVESTIGADOR                                          ║");
            println!("╠════════════════════════════════════════════════════════════════╣");
            println!("  Cédula:          {}", i.cedula);
            println!("  Nombres:         {}", i.nombres);
            println!("  Apellidos:       {}", i.apellidos);
            println!("  Email:           {}", i.email);
            println!("  Grupo ID:        {:?}", i.grupo_id);
            println!("  Estado:          {}", if i.activo { "Activo" } else { "Inactivo" });
            let prods = self.inv_crud.list_products(&i.cedula, true);
            println!("  Total productos: {}", prods.len());
            println!("╚════════════════════════════════════════════════════════════════╝");
        } else {
            println!("No se encontró ningún investigador con cédula '{}'.", ced.trim());
        }
        pausar();
    }

    fn crear_investigador(&self) {
        println!("\n--- REGISTRAR NUEVO INVESTIGADOR ---");
        let cedula = leer_linea("Cédula / Identificador único: ");
        if cedula.trim().is_empty() {
            println!("La cédula es obligatoria.");
            pausar();
            return;
        }
        let nombres = leer_linea("Nombres: ");
        let apellidos = leer_linea("Apellidos: ");
        let email = leer_linea("Email: ");
        let gid_str = leer_linea("ID del grupo de investigación: ");
        let gid = gid_str.trim().parse::<i64>().ok();

        let mut inv = Investigador::new(None, cedula, nombres, apellidos, email, gid);
        match self.inv_crud.create(&mut inv) {
            Ok(_) => println!("✓ Investigador registrado exitosamente."),
            Err(e) => println!("✗ Error registrando investigador: {}", e),
        }
        pausar();
    }

    fn editar_investigador(&self) {
        let ced = leer_linea("Ingrese la cédula del investigador a editar: ");
        let inv = match self.inv_crud.get_by_cedula(ced.trim(), false) {
            Some(i) => i,
            None => { println!("Investigador no encontrado."); pausar(); return; }
        };

        println!("Investigador: {}", inv.nombre_completo());
        println!("(Presione Enter para conservar el valor actual)");

        let nom = leer_linea(&format!("Nuevos nombres [{}]: ", inv.nombres));
        let ape = leer_linea(&format!("Nuevos apellidos [{}]: ", inv.apellidos));
        let em = leer_linea(&format!("Nuevo email [{}]: ", inv.email));
        let gid_str = leer_linea(&format!("Nuevo grupo ID [{:?}]: ", inv.grupo_id));
        let gid = gid_str.trim().parse::<i64>().ok();

        let ok = self.inv_crud.update(
            &inv.cedula,
            if nom.trim().is_empty() { None } else { Some(nom.trim().to_string()) },
            if ape.trim().is_empty() { None } else { Some(ape.trim().to_string()) },
            if em.trim().is_empty() { None } else { Some(em.trim().to_string()) },
            gid,
        );

        if ok {
            println!("✓ Investigador actualizado exitosamente.");
        } else {
            println!("✗ No se pudo actualizar el investigador.");
        }
        pausar();
    }

    fn desactivar_investigador(&self) {
        let ced = leer_linea("Ingrese cédula del investigador a desactivar: ");
        if self.inv_crud.deactivate(ced.trim()) {
            println!("✓ Investigador y sus productos desactivados lógicamente.");
        } else {
            println!("✗ Investigador no encontrado.");
        }
        pausar();
    }

    fn activar_investigador(&self) {
        let ced = leer_linea("Ingrese cédula del investigador a activar: ");
        if self.inv_crud.activate(ced.trim()) {
            println!("✓ Investigador y sus productos activados exitosamente.");
        } else {
            println!("✗ Investigador no encontrado.");
        }
        pausar();
    }

    fn eliminar_investigador_fisicamente(&mut self) {
        let ced = leer_linea("Ingrese cédula del investigador a ELIMINAR FÍSICAMENTE: ");
        let confirm = leer_linea("¿Está seguro de eliminar físicamente este investigador y sus productos? (S/N): ");
        if confirm.trim().eq_ignore_ascii_case("s") {
            if let Some((inv, prods)) = self.inv_crud.delete(ced.trim()) {
                let desc = format!("Investigador '{}' con {} productos", inv.nombre_completo(), prods.len());
                self.undo_stack.push(OperacionDeshacer::Investigador {
                    investigador: inv,
                    productos: prods,
                });
                println!("✓ {} eliminado físicamente. (Guardado en Pila de Deshacer).", desc);
            } else {
                println!("✗ Investigador no encontrado.");
            }
        } else {
            println!("Operación cancelada.");
        }
        pausar();
    }

    fn ver_productos_investigador(&self) {
        let ced = leer_linea("Ingrese cédula del investigador: ");
        let prods = self.inv_crud.list_products(ced.trim(), true);
        println!("\n--- PRODUCTOS DEL INVESTIGADOR ({}) ---", prods.len());
        if prods.is_empty() {
            println!("No tiene productos registrados.");
        } else {
            for (idx, p) in prods.iter().enumerate() {
                let a = p.anio.map(|y| y.to_string()).unwrap_or_else(|| "S/A".to_string());
                println!(" {}. [{}] {} ({}) [ID: {:?}] - Estado: {}", idx + 1, a, p.titulo, p.tipo, p.id, p.validacion);
            }
        }
        pausar();
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 3. SUBMENÚ PRODUCTOS
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_productos(&mut self) {
        loop {
            println!("\n┌────────────────────────────────────────────────────────┐");
            println!("│             GESTIÓN DE PRODUCTOS DE INVESTIGACIÓN      │");
            println!("└────────────────────────────────────────────────────────┘");
            println!(" 1. Listar todos los productos activos");
            println!(" 2. Listar todos los productos (incluyendo inactivos)");
            println!(" 3. Filtrar productos por año específico");
            println!(" 4. Filtrar productos por rango de años");
            println!(" 5. Buscar producto por ID");
            println!(" 6. Registrar nuevo producto");
            println!(" 7. Editar datos de un producto");
            println!(" 8. Cambiar estado de validación (Validado / No validado / En revisión)");
            println!(" 9. Desactivar producto (Eliminación lógica)");
            println!(" 10. Activar producto");
            println!(" 11. Eliminar producto físicamente (Apila en Deshacer)");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => self.listar_productos(None, true),
                "2" => self.listar_productos(None, false),
                "3" => {
                    let y_str = leer_linea("Ingrese el año (ej. 2023): ");
                    if let Ok(y) = y_str.trim().parse::<i32>() {
                        let prods = self.prod_crud.list_by_anio(y, true);
                        mostrar_tabla_productos(&prods);
                        pausar();
                    } else {
                        println!("Año no válido.");
                        pausar();
                    }
                }
                "4" => {
                    let ini = leer_linea("Año inicial: ").trim().parse::<i32>().unwrap_or(1900);
                    let fin = leer_linea("Año final: ").trim().parse::<i32>().unwrap_or(2030);
                    let prods = self.prod_crud.list_by_anio_range(ini, fin, true);
                    mostrar_tabla_productos(&prods);
                    pausar();
                }
                "5" => self.buscar_producto(),
                "6" => self.crear_producto(),
                "7" => self.editar_producto(),
                "8" => self.cambiar_validacion_producto(),
                "9" => self.desactivar_producto(),
                "10" => self.activar_producto(),
                "11" => self.eliminar_producto_fisicamente(),
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }

    fn listar_productos(&self, group_id: Option<i64>, only_active: bool) {
        let prods = match group_id {
            Some(gid) => self.prod_crud.list_by_group(gid, only_active),
            None => self.prod_crud.list_all(only_active),
        };
        mostrar_tabla_productos(&prods);
        pausar();
    }

    fn buscar_producto(&self) {
        let pid = leer_linea("Ingrese el ID del producto (ej. PRD-1): ");
        if let Some(p) = self.prod_crud.get_by_id(pid.trim()) {
            println!("\n╔════════════════════════════════════════════════════════════════╗");
            println!("║ FICHA DE PRODUCTO CIENTÍFICO                                   ║");
            println!("╠════════════════════════════════════════════════════════════════╣");
            println!("  ID:              {:?}", p.id);
            println!("  Título:          {}", p.titulo);
            println!("  Tipo:            {}", p.tipo);
            println!("  Categoría:       {}", p.categoria);
            println!("  Gran Categoría:  {}", p.gran_categoria);
            println!("  Cód MinCiencias: {}", p.codigo_minciencias);
            println!("  Año:             {:?}", p.anio);
            println!("  Validación:      {} (Validado bool: {})", p.validacion, p.validado);
            println!("  Investigador ID: {:?}", p.investigador_id);
            println!("  Grupo ID:        {:?}", p.grupo_id);
            println!("  Estado:          {}", if p.activo { "Activo" } else { "Inactivo" });
            println!("╚════════════════════════════════════════════════════════════════╝");
        } else {
            println!("No se encontró ningún producto con ID '{}'.", pid.trim());
        }
        pausar();
    }

    fn crear_producto(&self) {
        println!("\n--- REGISTRAR NUEVO PRODUCTO ---");
        let titulo = leer_linea("Título del producto: ");
        if titulo.trim().is_empty() {
            println!("El título es obligatorio.");
            pausar();
            return;
        }
        let tipo = leer_linea("Tipo (Artículo, Libro, Software, etc.): ");
        println!("Seleccione Categoría:");
        for (idx, cat) in CATEGORIAS_PRODUCTO.iter().enumerate() {
            println!("  {}. {}", idx + 1, cat);
        }
        let cat_idx = leer_linea("Opción (1-4, defecto 1): ").trim().parse::<usize>().unwrap_or(1);
        let categoria = CATEGORIAS_PRODUCTO.get(cat_idx.saturating_sub(1)).copied().unwrap_or("Nuevo conocimiento");

        println!("Seleccione Gran Categoría MinCiencias:");
        println!("  1. GNC - Generación de Nuevo Conocimiento");
        println!("  2. DTI - Desarrollo Tecnológico e Innovación");
        println!("  3. ASC - Apropiación Social del Conocimiento");
        println!("  4. FRH - Formación de Recurso Humano");
        let gc_idx = leer_linea("Opción (1-4, defecto 1): ");
        let gran_categoria = match gc_idx.trim() {
            "2" => "DTI",
            "3" => "ASC",
            "4" => "FRH",
            _ => "GNC",
        };

        let cod_minc = leer_linea("Código MinCiencias (ej. 2.2.1.1): ");
        let anio = leer_linea("Año (ej. 2024): ").trim().parse::<i32>().ok();
        let inv_ced = leer_linea("Cédula del investigador autor: ");
        let gid_str = leer_linea("ID del grupo: ");
        let gid = gid_str.trim().parse::<i64>().ok();

        let mut prod = Producto::new(
            None,
            titulo,
            tipo,
            categoria,
            anio,
            if inv_ced.trim().is_empty() { None } else { Some(inv_ced.trim().to_string()) },
            gid,
            Some(gran_categoria.to_string()),
            Some(cod_minc.trim().to_string()),
            Some("No validado".to_string()),
        );

        match self.prod_crud.create(&mut prod) {
            Ok(pid) => println!("✓ Producto registrado con éxito con ID '{}'.", pid),
            Err(e) => println!("✗ Error registrando producto: {}", e),
        }
        pausar();
    }

    fn editar_producto(&self) {
        let pid = leer_linea("Ingrese el ID del producto a editar: ");
        let p = match self.prod_crud.get_by_id(pid.trim()) {
            Some(prod) => prod,
            None => { println!("Producto no encontrado."); pausar(); return; }
        };

        println!("Producto: '{}' ({})", p.titulo, p.tipo);
        println!("(Presione Enter para conservar el valor actual)");

        let tit = leer_linea(&format!("Nuevo título [{}]: ", p.titulo));
        let tip = leer_linea(&format!("Nuevo tipo [{}]: ", p.tipo));
        let anio_s = leer_linea(&format!("Nuevo año [{:?}]: ", p.anio));
        let cod = leer_linea(&format!("Nuevo código MinCiencias [{}]: ", p.codigo_minciencias));

        let anio = if anio_s.trim().is_empty() { p.anio } else { anio_s.trim().parse::<i32>().ok() };

        let ok = self.prod_crud.update(
            pid.trim(),
            if tit.trim().is_empty() { None } else { Some(tit.trim().to_string()) },
            if tip.trim().is_empty() { None } else { Some(tip.trim().to_string()) },
            None,
            None,
            anio,
            None,
            if cod.trim().is_empty() { None } else { Some(cod.trim().to_string()) },
        );

        if ok {
            println!("✓ Producto actualizado exitosamente.");
        } else {
            println!("✗ No se pudo actualizar el producto.");
        }
        pausar();
    }

    fn cambiar_validacion_producto(&self) {
        let pid = leer_linea("Ingrese el ID del producto: ");
        println!("Seleccione nuevo estado de validación:");
        println!("  1. Validado");
        println!("  2. No validado");
        println!("  3. En revisión");
        let opc = leer_linea("Opción (1-3): ");
        let nuevo_estado = match opc.trim() {
            "1" => "Validado",
            "2" => "No validado",
            "3" => "En revisión",
            _ => { println!("Opción no válida."); pausar(); return; }
        };

        let ok = self.prod_crud.update(
            pid.trim(),
            None,
            None,
            None,
            None,
            None,
            Some(nuevo_estado.to_string()),
            None,
        );

        if ok {
            println!("✓ Estado de validación actualizado a '{}'.", nuevo_estado);
        } else {
            println!("✗ Producto no encontrado.");
        }
        pausar();
    }

    fn desactivar_producto(&self) {
        let pid = leer_linea("Ingrese ID del producto a desactivar: ");
        if self.prod_crud.deactivate(pid.trim()) {
            println!("✓ Producto desactivado lógicamente.");
        } else {
            println!("✗ Producto no encontrado.");
        }
        pausar();
    }

    fn activar_producto(&self) {
        let pid = leer_linea("Ingrese ID del producto a activar: ");
        if self.prod_crud.activate(pid.trim()) {
            println!("✓ Producto activado exitosamente.");
        } else {
            println!("✗ Producto no encontrado.");
        }
        pausar();
    }

    fn eliminar_producto_fisicamente(&mut self) {
        let pid = leer_linea("Ingrese ID del producto a ELIMINAR FÍSICAMENTE: ");
        let confirm = leer_linea("¿Está seguro de eliminar físicamente este producto? (S/N): ");
        if confirm.trim().eq_ignore_ascii_case("s") {
            if let Some(prod) = self.prod_crud.delete(pid.trim()) {
                let desc = format!("Producto '{}' [ID: {:?}]", prod.titulo, prod.id);
                self.undo_stack.push(OperacionDeshacer::Producto { producto: prod });
                println!("✓ {} eliminado físicamente. (Guardado en Pila de Deshacer).", desc);
            } else {
                println!("✗ Producto no encontrado.");
            }
        } else {
            println!("Operación cancelada.");
        }
        pausar();
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 4. SUBMENÚ PILA DE DESHACER (UNDO STACK)
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_deshacer(&mut self) {
        loop {
            println!("\n┌────────────────────────────────────────────────────────┐");
            println!("│           PILA DE DESHACER (UNDO STACK LIFO)           │");
            println!("└────────────────────────────────────────────────────────┘");
            println!(" Elementos en la cima de la pila: {}", self.undo_stack.len());
            if let Some(top) = self.undo_stack.peek() {
                println!(" Próxima acción a revertir: {}", top.descripcion());
            } else {
                println!(" (La pila de deshacer está vacía)");
            }
            println!("──────────────────────────────────────────────────────────");
            println!(" 1. Deshacer última eliminación (Pop y Restaurar)");
            println!(" 2. Vaciar historial de deshacer");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => {
                    if let Some(op) = self.undo_stack.pop() {
                        let desc = op.descripcion();
                        match op {
                            OperacionDeshacer::Grupo { mut grupo, investigadores } => {
                                grupo.activo = true;
                                let _ = self.grupo_crud.create(&mut grupo);
                                let gid = grupo.id.unwrap_or(1);
                                for (mut inv, prods) in investigadores {
                                    inv.activo = true;
                                    inv.grupo_id = Some(gid);
                                    let _ = self.inv_crud.create(&mut inv);
                                    let ced = inv.cedula.clone();
                                    for mut prod in prods {
                                        prod.investigador_id = Some(ced.clone());
                                        prod.grupo_id = Some(gid);
                                        let _ = self.prod_crud.create(&mut prod);
                                    }
                                }
                            }
                            OperacionDeshacer::Investigador { mut investigador, productos } => {
                                investigador.activo = true;
                                let ced = investigador.cedula.clone();
                                let _ = self.inv_crud.create(&mut investigador);
                                for mut prod in productos {
                                    prod.investigador_id = Some(ced.clone());
                                    let _ = self.prod_crud.create(&mut prod);
                                }
                            }
                            OperacionDeshacer::Producto { mut producto } => {
                                producto.activo = true;
                                let _ = self.prod_crud.create(&mut producto);
                            }
                        }
                        println!("✓ Eliminación revertida con éxito: {}", desc);
                    } else {
                        println!("La pila de deshacer está vacía. No hay acciones para revertir.");
                    }
                    pausar();
                }
                "2" => {
                    let confirm = leer_linea("¿Vaciar todo el historial de deshacer? (S/N): ");
                    if confirm.trim().eq_ignore_ascii_case("s") {
                        self.undo_stack.clear();
                        println!("✓ Pila de deshacer vaciada.");
                    }
                    pausar();
                }
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 5. SUBMENÚ COLA DE IMPORTACIÓN (IMPORT QUEUE FIFO)
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_cola_importacion(&mut self) {
        loop {
            println!("\n┌────────────────────────────────────────────────────────┐");
            println!("│        COLA DE IMPORTACIÓN (FIFO BATCH QUEUE)          │");
            println!("└────────────────────────────────────────────────────────┘");
            println!(" Tareas encoladas pendientes: {}", self.import_queue.len());
            let items = self.import_queue.to_vec();
            if items.is_empty() {
                println!(" (La cola de importación está vacía)");
            } else {
                for (idx, it) in items.iter().enumerate() {
                    println!("  {}. {}", idx + 1, it.etiqueta());
                }
            }
            println!("──────────────────────────────────────────────────────────");
            println!(" 1. Encolar URL de GrupLAC (Scraping MinCiencias)");
            println!(" 2. Encolar archivo CSV local");
            println!(" 3. Procesar cola de importación (Orden FIFO secuencial)");
            println!(" 4. Vaciar cola de importación");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => {
                    let url = leer_linea("Ingrese la URL de GrupLAC (http:// o https://): ");
                    if url.starts_with("http://") || url.starts_with("https://") {
                        let etiqueta = if url.len() > 60 { format!("{}...", &url[..57]) } else { url.clone() };
                        self.import_queue.enqueue(TareaImportacion::Url {
                            url: url.trim().to_string(),
                            etiqueta,
                        });
                        println!("✓ URL agregada a la cola de importación FIFO.");
                    } else {
                        println!("La URL debe comenzar con http:// o https://");
                    }
                    pausar();
                }
                "2" => {
                    let ruta = leer_linea("Ingrese la ruta del archivo CSV: ");
                    let p = std::path::Path::new(ruta.trim());
                    if p.exists() {
                        let etiqueta = format!("CSV: {}", p.file_name().unwrap_or_default().to_string_lossy());
                        self.import_queue.enqueue(TareaImportacion::ArchivoCsv {
                            ruta: ruta.trim().to_string(),
                            etiqueta,
                        });
                        println!("✓ Archivo CSV agregado a la cola de importación FIFO.");
                    } else {
                        println!("El archivo '{}' no existe.", ruta.trim());
                    }
                    pausar();
                }
                "3" => {
                    if self.import_queue.is_empty() {
                        println!("La cola de importación está vacía. Encole URLs o archivos primero.");
                        pausar();
                    } else {
                        println!("\nIniciando procesamiento secuencial FIFO...");
                        let rep = cola_trabajo::procesar_cola(
                            &mut self.import_queue,
                            &self.grupo_crud,
                            &self.inv_crud,
                            &self.prod_crud,
                        );
                        println!("\n--- RESULTADO DE LA COLA ---");
                        println!("Total tareas: {} │ Éxitos: {} │ Fallos: {}", rep.total_procesados, rep.exitosos, rep.fallidos);
                        for det in rep.detalles {
                            println!("  {}", det);
                        }
                        pausar();
                    }
                }
                "4" => {
                    self.import_queue.clear();
                    println!("✓ Cola de importación vaciada.");
                    pausar();
                }
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 6. SUBMENÚ ESTADÍSTICAS Y ANALÍTICA
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_estadisticas(&self) {
        let mut filtro = FiltroEstadisticas::default();

        loop {
            let analitica = calcular_analitica(&self.multilist.borrow(), &filtro);
            print!("{}", render_dashboard(&analitica));

            println!("\nFiltros activos:");
            println!("  Grupo: {:?}", filtro.grupo_id);
            println!("  Investigador: {:?}", filtro.investigador_cedula);
            println!("  Rango años: {:?} - {:?}", filtro.anio_inicio, filtro.anio_fin);
            println!("──────────────────────────────────────────────────────────");
            println!(" 1. Filtrar por Grupo específico");
            println!(" 2. Filtrar por Investigador específico (Cédula)");
            println!(" 3. Filtrar por rango de años");
            println!(" 4. Limpiar todos los filtros (Vista Global)");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => {
                    let gid_s = leer_linea("Ingrese ID del grupo (o Enter para cancelar): ");
                    if let Ok(gid) = gid_s.trim().parse::<i64>() {
                        filtro.grupo_id = Some(gid);
                    }
                }
                "2" => {
                    let ced = leer_linea("Ingrese cédula del investigador (o Enter para cancelar): ");
                    if !ced.trim().is_empty() {
                        filtro.investigador_cedula = Some(ced.trim().to_string());
                    }
                }
                "3" => {
                    let ini_s = leer_linea("Año inicio: ");
                    let fin_s = leer_linea("Año fin: ");
                    filtro.anio_inicio = ini_s.trim().parse::<i32>().ok();
                    filtro.anio_fin = fin_s.trim().parse::<i32>().ok();
                }
                "4" => {
                    filtro = FiltroEstadisticas::default();
                    println!("✓ Filtros restablecidos a Vista Global.");
                }
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }

    // ═════════════════════════════════════════════════════════════════════════
    // 7. SUBMENÚ PERSISTENCIA
    // ═════════════════════════════════════════════════════════════════════════
    fn menu_persistencia(&mut self) {
        loop {
            println!("\n┌────────────────────────────────────────────────────────┐");
            println!("│             PERSISTENCIA Y EXPORTACIÓN DE DATOS        │");
            println!("└────────────────────────────────────────────────────────┘");
            println!(" Ruta JSON configurada: {}", self.ruta_datos);
            println!("──────────────────────────────────────────────────────────");
            println!(" 1. Guardar en archivo JSON actual ('{}')", self.ruta_datos);
            println!(" 2. Cargar desde archivo JSON ('{}')", self.ruta_datos);
            println!(" 3. Guardar en otra ruta JSON personalizada");
            println!(" 4. Cargar desde otra ruta JSON personalizada");
            println!(" 5. Exportar toda la base a archivo plano CSV");
            println!(" 0. Volver al menú principal");
            println!("──────────────────────────────────────────────────────────");

            let opc = leer_linea("Opción: ");
            match opc.trim() {
                "1" => {
                    match guardar_json(&self.multilist.borrow(), &self.ruta_datos) {
                        Ok(_) => println!("✓ Multilista guardada exitosamente en '{}'.", self.ruta_datos),
                        Err(e) => println!("✗ Error guardando: {}", e),
                    }
                    pausar();
                }
                "2" => {
                    let confirm = leer_linea("¿Cargar desde JSON reemplazará los datos en memoria? (S/N): ");
                    if confirm.trim().eq_ignore_ascii_case("s") {
                        match cargar_json(&self.ruta_datos) {
                            Ok(new_ml) => {
                                *self.multilist.borrow_mut() = new_ml;
                                self.undo_stack.clear();
                                println!("✓ Datos cargados exitosamente desde '{}'.", self.ruta_datos);
                            }
                            Err(e) => println!("✗ Error cargando: {}", e),
                        }
                    }
                    pausar();
                }
                "3" => {
                    let ruta = leer_linea("Ingrese ruta de destino (.json): ");
                    match guardar_json(&self.multilist.borrow(), ruta.trim()) {
                        Ok(_) => println!("✓ Multilista guardada en '{}'.", ruta.trim()),
                        Err(e) => println!("✗ Error guardando: {}", e),
                    }
                    pausar();
                }
                "4" => {
                    let ruta = leer_linea("Ingrese ruta de origen (.json): ");
                    match cargar_json(ruta.trim()) {
                        Ok(new_ml) => {
                            *self.multilist.borrow_mut() = new_ml;
                            self.undo_stack.clear();
                            self.ruta_datos = ruta.trim().to_string();
                            println!("✓ Datos cargados exitosamente desde '{}'.", ruta.trim());
                        }
                        Err(e) => println!("✗ Error cargando: {}", e),
                    }
                    pausar();
                }
                "5" => {
                    let ruta = leer_linea("Ingrese ruta para exportar CSV (ej. export.csv): ");
                    match exportar_csv(&self.multilist.borrow(), ruta.trim()) {
                        Ok(filas) => println!("✓ Se exportaron {} filas en el archivo '{}'.", filas, ruta.trim()),
                        Err(e) => println!("✗ Error exportando CSV: {}", e),
                    }
                    pausar();
                }
                "0" => break,
                _ => println!("Opción no válida."),
            }
        }
    }
}

// ── Helpers auxiliares ─────────────────────────────────────────────────────

fn leer_linea(prompt: &str) -> String {
    print!("{}", prompt);
    let _ = io::stdout().flush();
    let mut buffer = String::new();
    let _ = io::stdin().read_line(&mut buffer);
    buffer.trim().to_string()
}

fn pausar() {
    print!("\nPresione Enter para continuar...");
    let _ = io::stdout().flush();
    let mut buffer = String::new();
    let _ = io::stdin().read_line(&mut buffer);
}

fn mostrar_ficha_grupo(g: &Grupo) {
    println!("\n╔════════════════════════════════════════════════════════════════╗");
    println!("║ FICHA DE GRUPO DE INVESTIGACIÓN                                ║");
    println!("╠════════════════════════════════════════════════════════════════╣");
    println!("  ID:              {:?}", g.id);
    println!("  Código GrupLAC:  {}", g.codigo_gruplac);
    println!("  Nombre:          {}", g.nombre);
    println!("  Categoría:       {}", g.categoria);
    println!("  Líder:           {}", g.lider);
    println!("  Fecha creación:  {}", g.fecha_creacion);
    println!("  Estado:          {}", if g.activo { "Activo" } else { "Inactivo" });
    if !g.plan.trim().is_empty() {
        println!("  Plan de trabajo / Objetivos:\n    {}", g.plan.replace('\n', "\n    "));
    }
    println!("╚════════════════════════════════════════════════════════════════╝");
}

fn mostrar_tabla_productos(prods: &[Producto]) {
    println!("\n--- PRODUCTOS REGISTRADOS ({}) ---", prods.len());
    if prods.is_empty() {
        println!("No hay productos que coincidan con la búsqueda.");
    } else {
        println!("{:<8} │ {:<4} │ {:<32} │ {:<18} │ {:<6} │ {:<12}", "ID", "AÑO", "TÍTULO", "TIPO", "GRAN", "VALIDACIÓN");
        println!("─────────┼──────┼──────────────────────────────────┼────────────────────┼────────┼─────────────");
        for p in prods {
            let pid = p.id.as_deref().unwrap_or("-");
            let y = p.anio.map(|a| a.to_string()).unwrap_or_else(|| "S/A".to_string());
            let tit = if p.titulo.len() > 30 { format!("{}...", &p.titulo[..27]) } else { p.titulo.clone() };
            let tip = if p.tipo.len() > 18 { format!("{}...", &p.tipo[..15]) } else { p.tipo.clone() };
            println!("{:<8} │ {:<4} │ {:<32} │ {:<18} │ {:<6} │ {:<12}", pid, y, tit, tip, p.gran_categoria, p.validacion);
        }
    }
}
