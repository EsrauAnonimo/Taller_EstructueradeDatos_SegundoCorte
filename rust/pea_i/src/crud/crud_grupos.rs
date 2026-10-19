//! Operaciones CRUD para Grupos de Investigación sobre la Multilista compartida.

use crate::modelos::entidades::{Grupo, Investigador, Producto};
use crate::modelos::multilista::Multilist;
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Clone)]
pub struct GrupoCRUD {
    multilist: Rc<RefCell<Multilist>>,
}

impl GrupoCRUD {
    pub fn new(multilist: Rc<RefCell<Multilist>>) -> Self {
        Self { multilist }
    }

    /// Genera el siguiente ID secuencial disponible para un nuevo grupo.
    pub fn next_id(&self) -> i64 {
        let ml = self.multilist.borrow();
        let mut max_id: i64 = 0;
        let mut curr = ml.head_group.clone();
        while let Some(node) = curr {
            if let Some(id) = node.borrow().data.id {
                if id > max_id {
                    max_id = id;
                }
            }
            curr = node.borrow().next.clone();
        }
        max_id + 1
    }

    /// Crea un nuevo grupo asegurando ID secuencial y unicidad de código GrupLAC.
    pub fn create(&self, grupo: &mut Grupo) -> Result<i64, String> {
        let mut ml = self.multilist.borrow_mut();
        let code = grupo.codigo_gruplac.trim();
        if !code.is_empty() && ml.get_group_node_by_code(code).is_some() {
            return Err(format!("Ya existe un grupo con el código '{}'", code));
        }

        let gid = match grupo.id {
            Some(id) if id > 0 => id,
            _ => {
                let next = {
                    let mut max_id: i64 = 0;
                    let mut curr = ml.head_group.clone();
                    while let Some(node) = curr {
                        if let Some(id) = node.borrow().data.id {
                            if id > max_id {
                                max_id = id;
                            }
                        }
                        curr = node.borrow().next.clone();
                    }
                    max_id + 1
                };
                grupo.id = Some(next);
                next
            }
        };

        ml.add_group(grupo.clone());
        Ok(gid)
    }

    pub fn list_all(&self, only_active: bool) -> Vec<Grupo> {
        self.multilist.borrow().iterate_groups(only_active)
    }

    pub fn get_by_id(&self, group_id: i64) -> Option<Grupo> {
        self.multilist
            .borrow()
            .get_group_node_by_id(group_id)
            .map(|n| n.borrow().data.clone())
    }

    pub fn get_by_code(&self, code: &str) -> Option<Grupo> {
        self.multilist
            .borrow()
            .get_group_node_by_code(code)
            .map(|n| n.borrow().data.clone())
    }

    pub fn update(
        &self,
        group_id: i64,
        nombre: Option<String>,
        categoria: Option<String>,
        lider: Option<String>,
        plan: Option<String>,
        fecha_creacion: Option<String>,
    ) -> bool {
        let ml = self.multilist.borrow();
        if let Some(node) = ml.get_group_node_by_id(group_id) {
            let mut g = node.borrow().data.clone();
            if let Some(n) = nombre {
                g.nombre = n;
            }
            if let Some(c) = categoria {
                g.categoria = c;
            }
            if let Some(l) = lider {
                g.lider = l;
            }
            if let Some(p) = plan {
                g.plan = p;
            }
            if let Some(f) = fecha_creacion {
                g.fecha_creacion = f;
            }
            node.borrow_mut().data = g;
            true
        } else {
            false
        }
    }

    pub fn deactivate(&self, group_id: i64) -> bool {
        self.multilist.borrow_mut().deactivate_group(group_id)
    }

    pub fn activate(&self, group_id: i64) -> bool {
        self.multilist.borrow_mut().activate_group(group_id)
    }

    pub fn delete(&self, group_id: i64) -> Option<(Grupo, Vec<(Investigador, Vec<Producto>)>)> {
        self.multilist.borrow_mut().remove_group(group_id)
    }

    pub fn add_member(&self, group_id: i64, inv: Investigador) -> bool {
        self.multilist
            .borrow_mut()
            .add_investigador(group_id, inv)
            .is_some()
    }

    pub fn list_members(&self, group_id: i64, only_active: bool) -> Vec<Investigador> {
        self.multilist
            .borrow()
            .iterate_investigadores(Some(group_id), only_active)
    }

    pub fn list_products(&self, group_id: i64, only_active: bool) -> Vec<Producto> {
        self.multilist
            .borrow()
            .get_productos_by_grupo(group_id, only_active)
    }
}
