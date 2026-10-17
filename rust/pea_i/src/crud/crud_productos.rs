//! Operaciones CRUD para Productos de Investigación sobre la Multilista compartida.

use crate::modelos::entidades::{ESTADOS_VALIDACION, Producto};
use crate::modelos::multilista::Multilist;
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Clone)]
pub struct ProductoCRUD {
    multilist: Rc<RefCell<Multilist>>,
}

impl ProductoCRUD {
    pub fn new(multilist: Rc<RefCell<Multilist>>) -> Self {
        Self { multilist }
    }

    /// Inserta un nuevo producto asignándole un ID único secuencial si no lo tiene.
    pub fn create(&self, prod: &mut Producto) -> Result<String, String> {
        let cedula = match prod.investigador_id.as_deref().or(prod.investigador_cedula.as_deref()) {
            Some(c) if !c.trim().is_empty() => c.trim().to_string(),
            _ => {
                // Si no viene cédula, buscar un investigador activo en el grupo
                let ml = self.multilist.borrow();
                let gid = prod.grupo_id;
                let invs = ml.iterate_investigadores(gid, true);
                if let Some(first_inv) = invs.first() {
                    first_inv.cedula.clone()
                } else {
                    return Err("No se puede registrar el producto sin un investigador receptor".to_string());
                }
            }
        };

        prod.investigador_id = Some(cedula.clone());
        prod.investigador_cedula = Some(cedula.clone());

        if prod.id.is_none() || prod.id.as_deref() == Some("") {
            let total = self.multilist.borrow().iterate_productos(None, None, None, false).len();
            prod.id = Some(format!("PRD-{}", total + 1));
        }

        let pid = prod.id.clone().unwrap();

        let mut ml = self.multilist.borrow_mut();
        ml.add_producto(&cedula, prod.clone())
            .ok_or_else(|| format!("No se encontró al investigador con cédula '{}' en la Multilista", cedula))?;

        Ok(pid)
    }

    pub fn list_all(&self, only_active: bool) -> Vec<Producto> {
        self.multilist
            .borrow()
            .iterate_productos(None, None, None, only_active)
    }

    pub fn list_by_group(&self, group_id: i64, only_active: bool) -> Vec<Producto> {
        self.multilist
            .borrow()
            .iterate_productos(Some(group_id), None, None, only_active)
    }

    pub fn list_by_investigador(&self, cedula: &str, only_active: bool) -> Vec<Producto> {
        self.multilist
            .borrow()
            .iterate_productos(None, Some(cedula), None, only_active)
    }

    pub fn list_by_anio(&self, anio: i32, only_active: bool) -> Vec<Producto> {
        self.multilist
            .borrow()
            .iterate_productos(None, None, Some(anio), only_active)
    }

    pub fn list_by_anio_range(&self, inicio: i32, fin: i32, only_active: bool) -> Vec<Producto> {
        self.list_all(only_active)
            .into_iter()
            .filter(|p| {
                if let Some(y) = p.anio {
                    y >= inicio && y <= fin
                } else {
                    false
                }
            })
            .collect()
    }

    pub fn get_by_id(&self, prod_id: &str) -> Option<Producto> {
        self.multilist.borrow().find_producto(prod_id)
    }

    pub fn update(
        &self,
        prod_id: &str,
        titulo: Option<String>,
        tipo: Option<String>,
        categoria: Option<String>,
        gran_categoria: Option<String>,
        anio: Option<i32>,
        validacion: Option<String>,
        codigo_minciencias: Option<String>,
    ) -> bool {
        let mut ml = self.multilist.borrow_mut();
        if let Some(mut p) = ml.find_producto(prod_id) {
            if let Some(t) = titulo {
                p.titulo = t;
            }
            if let Some(tp) = tipo {
                p.tipo = tp;
            }
            if let Some(c) = categoria {
                p.categoria = c;
            }
            if let Some(gc) = gran_categoria {
                p.gran_categoria = gc;
            }
            if anio.is_some() {
                p.anio = anio;
            }
            if let Some(v) = validacion {
                if ESTADOS_VALIDACION.contains(&v.as_str()) {
                    p.validado = v == "Validado";
                    p.validacion = v;
                }
            }
            if let Some(cod) = codigo_minciencias {
                p.codigo_minciencias = cod;
            }
            ml.update_producto(prod_id, p)
        } else {
            false
        }
    }

    pub fn deactivate(&self, prod_id: &str) -> bool {
        self.multilist.borrow_mut().deactivate_producto(prod_id)
    }

    pub fn activate(&self, prod_id: &str) -> bool {
        self.multilist.borrow_mut().activate_producto(prod_id)
    }

    pub fn delete(&self, prod_id: &str) -> Option<Producto> {
        self.multilist.borrow_mut().remove_producto(prod_id)
    }
}
