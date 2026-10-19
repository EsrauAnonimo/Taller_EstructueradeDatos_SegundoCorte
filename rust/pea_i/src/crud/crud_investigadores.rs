//! Operaciones CRUD para Investigadores sobre la Multilista compartida.

use crate::modelos::entidades::{Grupo, Investigador, Producto};
use crate::modelos::multilista::Multilist;
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Clone)]
pub struct InvestigadorCRUD {
    multilist: Rc<RefCell<Multilist>>,
}

impl InvestigadorCRUD {
    pub fn new(multilist: Rc<RefCell<Multilist>>) -> Self {
        Self { multilist }
    }

    /// Inserta un nuevo investigador validando que no exista cédula duplicada
    /// en la Multilista.
    pub fn create(&self, inv: &mut Investigador) -> Result<(), String> {
        let ced = inv.cedula.trim();
        if ced.is_empty() {
            return Err("La cédula no puede estar vacía".to_string());
        }

        let ml = self.multilist.borrow();
        if ml.get_investigador(ced, false).is_some() {
            return Err(format!("Ya existe un investigador con cédula '{}'", ced));
        }
        drop(ml);

        let gid = inv.grupo_id.unwrap_or(1);
        let mut ml_mut = self.multilist.borrow_mut();
        if ml_mut.get_group_node_by_id(gid).is_none() {
            // Si el grupo no existe, verificar si hay algún grupo o usar el primer grupo disponible
            if let Some(first_g) = ml_mut.head_group.clone() {
                inv.grupo_id = first_g.borrow().data.id;
            } else {
                return Err("No hay grupos registrados en el sistema para asociar al investigador".to_string());
            }
        }

        let final_gid = inv.grupo_id.unwrap();
        ml_mut
            .add_investigador(final_gid, inv.clone())
            .ok_or_else(|| "Error insertando investigador en la sublista".to_string())?;

        Ok(())
    }

    pub fn list_all(&self, only_active: bool) -> Vec<Investigador> {
        self.multilist.borrow().iterate_investigadores(None, only_active)
    }

    pub fn list_by_group(&self, group_id: i64, only_active: bool) -> Vec<Investigador> {
        self.multilist
            .borrow()
            .iterate_investigadores(Some(group_id), only_active)
    }

    pub fn get_by_cedula(&self, cedula: &str, only_active: bool) -> Option<Investigador> {
        self.multilist.borrow().get_investigador(cedula, only_active)
    }

    pub fn update(
        &self,
        cedula: &str,
        nombres: Option<String>,
        apellidos: Option<String>,
        email: Option<String>,
        grupo_id: Option<i64>,
    ) -> bool {
        let mut ml = self.multilist.borrow_mut();
        if let Some(mut inv) = ml.get_investigador(cedula, false) {
            if let Some(n) = nombres {
                inv.nombres = n;
            }
            if let Some(a) = apellidos {
                inv.apellidos = a;
            }
            if let Some(e) = email {
                inv.email = e;
            }
            if let Some(g) = grupo_id {
                inv.grupo_id = Some(g);
            }
            ml.update_investigador(cedula, inv)
        } else {
            false
        }
    }

    pub fn deactivate(&self, cedula: &str) -> bool {
        self.multilist.borrow_mut().deactivate_investigador(cedula)
    }

    pub fn activate(&self, cedula: &str) -> bool {
        self.multilist.borrow_mut().activate_investigador(cedula)
    }

    pub fn delete(&self, cedula: &str) -> Option<(Investigador, Vec<Producto>)> {
        self.multilist.borrow_mut().remove_investigador(cedula)
    }

    pub fn list_groups(&self, cedula: &str) -> Vec<Grupo> {
        self.multilist.borrow().get_grupos_by_investigador(cedula)
    }

    pub fn list_products(&self, cedula: &str, only_active: bool) -> Vec<Producto> {
        self.multilist
            .borrow()
            .get_productos_by_investigador(cedula, only_active)
    }
}
