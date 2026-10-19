//! Multilista jerárquica propia en 3 niveles:
//! Nivel 1: Grupos (enlazados por `next` y `prev`)
//! Nivel 2: Integrantes / Investigadores (sublista de cada Grupo)
//! Nivel 3: Productos de investigación (sublista de cada Investigador)
//!
//! Cada nivel está implementado con punteros `Rc<RefCell<...>>` y `Weak<RefCell<...>>`
//! para garantizar navegación bidireccional y liberación limpia de memoria sin ciclos.

use super::entidades::{Grupo, Investigador, Producto};
use std::cell::RefCell;
use std::rc::{Rc, Weak};

// --- Nodos de cada nivel ---

pub type ProductNodeRef = Rc<RefCell<ProductNode>>;
pub type ProductWeakRef = Weak<RefCell<ProductNode>>;

#[derive(Debug)]
pub struct ProductNode {
    pub data: Producto,
    pub next: Option<ProductNodeRef>,
    pub prev: Option<ProductWeakRef>,
    pub active: bool,
}

impl ProductNode {
    pub fn new(data: Producto) -> Self {
        Self {
            data,
            next: None,
            prev: None,
            active: true,
        }
    }
}

pub type InvNodeRef = Rc<RefCell<InvestigatorNode>>;
pub type InvWeakRef = Weak<RefCell<InvestigatorNode>>;

#[derive(Debug)]
pub struct InvestigatorNode {
    pub data: Investigador,
    pub next: Option<InvNodeRef>,
    pub prev: Option<InvWeakRef>,
    pub sublist: Option<ProductNodeRef>, // Cabeza de productos de este investigador
    pub active: bool,
}

impl InvestigatorNode {
    pub fn new(data: Investigador) -> Self {
        Self {
            data,
            next: None,
            prev: None,
            sublist: None,
            active: true,
        }
    }
}

pub type GroupNodeRef = Rc<RefCell<GroupNode>>;
pub type GroupWeakRef = Weak<RefCell<GroupNode>>;

#[derive(Debug)]
pub struct GroupNode {
    pub data: Grupo,
    pub next: Option<GroupNodeRef>,
    pub prev: Option<GroupWeakRef>,
    pub sublist: Option<InvNodeRef>, // Cabeza de investigadores de este grupo
    pub active: bool,
}

impl GroupNode {
    pub fn new(data: Grupo) -> Self {
        Self {
            data,
            next: None,
            prev: None,
            sublist: None,
            active: true,
        }
    }
}

// --- Multilista Principal ---

#[derive(Debug, Default)]
pub struct Multilist {
    pub head_group: Option<GroupNodeRef>,
    pub size_groups: usize,
}

impl Multilist {
    pub fn new() -> Self {
        Self {
            head_group: None,
            size_groups: 0,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.head_group.is_none()
    }

    pub fn len_groups(&self) -> usize {
        self.size_groups
    }

    // ── GESTIÓN DE GRUPOS ──────────────────────────────────────────────────

    /// Agrega un grupo al final de la lista principal de grupos.
    pub fn add_group(&mut self, grupo: Grupo) -> GroupNodeRef {
        let node = Rc::new(RefCell::new(GroupNode::new(grupo)));
        if self.head_group.is_none() {
            self.head_group = Some(Rc::clone(&node));
        } else {
            let mut curr = self.head_group.clone().unwrap();
            loop {
                let next = curr.borrow().next.clone();
                match next {
                    Some(n) => curr = n,
                    None => break,
                }
            }
            node.borrow_mut().prev = Some(Rc::downgrade(&curr));
            curr.borrow_mut().next = Some(Rc::clone(&node));
        }
        self.size_groups += 1;
        node
    }

    /// Busca un nodo de grupo por su ID numérico.
    pub fn get_group_node_by_id(&self, group_id: i64) -> Option<GroupNodeRef> {
        let mut curr = self.head_group.clone();
        while let Some(node) = curr {
            if node.borrow().data.id == Some(group_id) {
                return Some(node);
            }
            curr = node.borrow().next.clone();
        }
        None
    }

    /// Busca un nodo de grupo por su código de GrupLAC.
    pub fn get_group_node_by_code(&self, code: &str) -> Option<GroupNodeRef> {
        let code_clean = code.trim().to_lowercase();
        let mut curr = self.head_group.clone();
        while let Some(node) = curr {
            if node.borrow().data.codigo_gruplac.trim().to_lowercase() == code_clean {
                return Some(node);
            }
            curr = node.borrow().next.clone();
        }
        None
    }

    /// Actualiza los datos de un grupo.
    pub fn update_group(&mut self, group_id: i64, new_grupo: Grupo) -> bool {
        if let Some(node) = self.get_group_node_by_id(group_id) {
            node.borrow_mut().data = new_grupo;
            true
        } else {
            false
        }
    }

    /// Desactiva lógicamente un grupo.
    pub fn deactivate_group(&mut self, group_id: i64) -> bool {
        if let Some(node) = self.get_group_node_by_id(group_id) {
            node.borrow_mut().active = false;
            node.borrow_mut().data.activo = false;
            true
        } else {
            false
        }
    }

    /// Activa lógicamente un grupo.
    pub fn activate_group(&mut self, group_id: i64) -> bool {
        if let Some(node) = self.get_group_node_by_id(group_id) {
            node.borrow_mut().active = true;
            node.borrow_mut().data.activo = true;
            true
        } else {
            false
        }
    }

    /// Elimina físicamente un grupo y todas sus sublistas, retornando la estructura
    /// para permitir la operación de deshacer (Undo Stack).
    pub fn remove_group(
        &mut self,
        group_id: i64,
    ) -> Option<(Grupo, Vec<(Investigador, Vec<Producto>)>)> {
        let target_node = self.get_group_node_by_id(group_id)?;

        // Extraer todos los investigadores y productos para el snapshot de Undo
        let mut inv_snapshots = Vec::new();
        let mut curr_inv = target_node.borrow().sublist.clone();
        while let Some(inv_node) = curr_inv {
            let inv_data = inv_node.borrow().data.clone();
            let mut prod_list = Vec::new();
            let mut curr_prod = inv_node.borrow().sublist.clone();
            while let Some(prod_node) = curr_prod {
                prod_list.push(prod_node.borrow().data.clone());
                curr_prod = prod_node.borrow().next.clone();
            }
            inv_snapshots.push((inv_data, prod_list));
            curr_inv = inv_node.borrow().next.clone();
        }

        let grupo_data = target_node.borrow().data.clone();

        // Desvincular de la lista principal
        let prev_weak = target_node.borrow_mut().prev.take();
        let next_rc = target_node.borrow_mut().next.take();

        if let Some(prev_rc) = prev_weak.as_ref().and_then(|w| w.upgrade()) {
            prev_rc.borrow_mut().next = next_rc.clone();
        } else {
            self.head_group = next_rc.clone();
        }

        if let Some(next_node) = next_rc {
            next_node.borrow_mut().prev = prev_weak;
        }

        target_node.borrow_mut().sublist = None;
        if self.size_groups > 0 {
            self.size_groups -= 1;
        }

        Some((grupo_data, inv_snapshots))
    }

    // ── GESTIÓN DE INVESTIGADORES ──────────────────────────────────────────

    /// Agrega un investigador a la sublista de un grupo.
    pub fn add_investigador(&mut self, group_id: i64, inv: Investigador) -> Option<InvNodeRef> {
        let group_node = self.get_group_node_by_id(group_id)?;
        let cedula = inv.cedula.clone();

        // Verificar si ya existe en este grupo
        let mut curr = group_node.borrow().sublist.clone();
        while let Some(node) = curr {
            if node.borrow().data.cedula == cedula {
                node.borrow_mut().active = true;
                node.borrow_mut().data.activo = true;
                return Some(node);
            }
            curr = node.borrow().next.clone();
        }

        // Si ya existe en otro grupo de la multilista, enlazar su sublista de productos
        let existing_sublist = self.find_investigador_sublist(&cedula);

        let inv_node = Rc::new(RefCell::new(InvestigatorNode::new(inv)));
        inv_node.borrow_mut().sublist = existing_sublist;

        if group_node.borrow().sublist.is_none() {
            group_node.borrow_mut().sublist = Some(Rc::clone(&inv_node));
        } else {
            let mut c = group_node.borrow().sublist.clone().unwrap();
            loop {
                let next = c.borrow().next.clone();
                match next {
                    Some(n) => c = n,
                    None => break,
                }
            }
            inv_node.borrow_mut().prev = Some(Rc::downgrade(&c));
            c.borrow_mut().next = Some(Rc::clone(&inv_node));
        }
        Some(inv_node)
    }

    fn find_investigador_sublist(&self, cedula: &str) -> Option<ProductNodeRef> {
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                if i_node.borrow().data.cedula == cedula && i_node.borrow().sublist.is_some() {
                    return i_node.borrow().sublist.clone();
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        None
    }

    /// Busca un investigador por cédula (primer hallazgo).
    pub fn get_investigador(&self, cedula: &str, only_active: bool) -> Option<Investigador> {
        let ced = cedula.trim().to_lowercase();
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                let node_ced = i_node.borrow().data.cedula.trim().to_lowercase();
                if node_ced == ced && (!only_active || i_node.borrow().active) {
                    return Some(i_node.borrow().data.clone());
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        None
    }

    /// Actualiza un investigador en todas sus referencias dentro de la Multilista.
    pub fn update_investigador(&mut self, cedula: &str, new_inv: Investigador) -> bool {
        let ced = cedula.trim().to_lowercase();
        let mut updated = false;
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                if i_node.borrow().data.cedula.trim().to_lowercase() == ced {
                    i_node.borrow_mut().data = new_inv.clone();
                    updated = true;
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        updated
    }

    /// Desactiva un investigador y sus productos en toda la Multilista.
    pub fn deactivate_investigador(&mut self, cedula: &str) -> bool {
        let ced = cedula.trim().to_lowercase();
        let mut deactivated = false;
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                if i_node.borrow().data.cedula.trim().to_lowercase() == ced {
                    i_node.borrow_mut().active = false;
                    i_node.borrow_mut().data.activo = false;
                    // Desactivar productos asociados en la sublista
                    let mut p_curr = i_node.borrow().sublist.clone();
                    while let Some(p_node) = p_curr {
                        p_node.borrow_mut().active = false;
                        p_curr = p_node.borrow().next.clone();
                    }
                    deactivated = true;
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        deactivated
    }

    /// Reactiva un investigador y sus productos.
    pub fn activate_investigador(&mut self, cedula: &str) -> bool {
        let ced = cedula.trim().to_lowercase();
        let mut activated = false;
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                if i_node.borrow().data.cedula.trim().to_lowercase() == ced {
                    i_node.borrow_mut().active = true;
                    i_node.borrow_mut().data.activo = true;
                    let mut p_curr = i_node.borrow().sublist.clone();
                    while let Some(p_node) = p_curr {
                        p_node.borrow_mut().active = true;
                        p_curr = p_node.borrow().next.clone();
                    }
                    activated = true;
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        activated
    }

    /// Elimina físicamente un investigador de todas las relaciones de la Multilista,
    /// retornando sus datos y sus productos para la pila de Deshacer.
    pub fn remove_investigador(&mut self, cedula: &str) -> Option<(Investigador, Vec<Producto>)> {
        let ced = cedula.trim().to_lowercase();
        let mut inv_data = None;
        let mut prods = Vec::new();

        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut prev_i: Option<InvNodeRef> = None;
            let mut curr_i = g_node.borrow().sublist.clone();

            while let Some(i_node) = curr_i {
                let matches = i_node.borrow().data.cedula.trim().to_lowercase() == ced;
                let next_i = i_node.borrow().next.clone();

                if matches {
                    if inv_data.is_none() {
                        inv_data = Some(i_node.borrow().data.clone());
                        // Recolectar productos
                        let mut p_curr = i_node.borrow().sublist.clone();
                        while let Some(p_node) = p_curr {
                            prods.push(p_node.borrow().data.clone());
                            p_curr = p_node.borrow().next.clone();
                        }
                    }

                    // Desvincular i_node de la sublista del grupo
                    if let Some(prev) = prev_i.clone() {
                        prev.borrow_mut().next = next_i.clone();
                    } else {
                        g_node.borrow_mut().sublist = next_i.clone();
                    }

                    if let Some(next) = next_i.clone() {
                        next.borrow_mut().prev = prev_i.as_ref().map(Rc::downgrade);
                    }

                    i_node.borrow_mut().next = None;
                    i_node.borrow_mut().prev = None;
                    i_node.borrow_mut().sublist = None;
                } else {
                    prev_i = Some(Rc::clone(&i_node));
                }
                curr_i = next_i;
            }
            g_curr = g_node.borrow().next.clone();
        }

        inv_data.map(|inv| (inv, prods))
    }

    /// Retorna los grupos activos a los que pertenece el investigador.
    pub fn get_grupos_by_investigador(&self, cedula: &str) -> Vec<Grupo> {
        let ced = cedula.trim().to_lowercase();
        let mut grupos = Vec::new();
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            if g_node.borrow().active {
                let mut i_curr = g_node.borrow().sublist.clone();
                while let Some(i_node) = i_curr {
                    if i_node.borrow().active && i_node.borrow().data.cedula.trim().to_lowercase() == ced {
                        grupos.push(g_node.borrow().data.clone());
                        break;
                    }
                    i_curr = i_node.borrow().next.clone();
                }
            }
            g_curr = g_node.borrow().next.clone();
        }
        grupos
    }

    // ── GESTIÓN DE PRODUCTOS ───────────────────────────────────────────────

    /// Agrega un producto a la sublista del investigador indicado.
    pub fn add_producto(&mut self, cedula: &str, prod: Producto) -> Option<ProductNodeRef> {
        let ced = cedula.trim().to_lowercase();
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                if i_node.borrow().data.cedula.trim().to_lowercase() == ced {
                    let prod_node = Rc::new(RefCell::new(ProductNode::new(prod)));
                    if i_node.borrow().sublist.is_none() {
                        i_node.borrow_mut().sublist = Some(Rc::clone(&prod_node));
                    } else {
                        let mut p = i_node.borrow().sublist.clone().unwrap();
                        loop {
                            let next = p.borrow().next.clone();
                            match next {
                                Some(n) => p = n,
                                None => break,
                            }
                        }
                        prod_node.borrow_mut().prev = Some(Rc::downgrade(&p));
                        p.borrow_mut().next = Some(Rc::clone(&prod_node));
                    }
                    return Some(prod_node);
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        None
    }

    /// Retorna todos los productos del investigador sin duplicados por ID.
    pub fn get_productos_by_investigador(&self, cedula: &str, only_active: bool) -> Vec<Producto> {
        let ced = cedula.trim().to_lowercase();
        let mut productos = Vec::new();
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            if !only_active || g_node.borrow().active {
                let mut i_curr = g_node.borrow().sublist.clone();
                while let Some(i_node) = i_curr {
                    if (!only_active || i_node.borrow().active)
                        && i_node.borrow().data.cedula.trim().to_lowercase() == ced
                    {
                        let mut p_curr = i_node.borrow().sublist.clone();
                        while let Some(p_node) = p_curr {
                            if !only_active || p_node.borrow().active {
                                let p_data = p_node.borrow().data.clone();
                                if !productos.iter().any(|p: &Producto| p.id == p_data.id && p.id.is_some()) {
                                    productos.push(p_data);
                                }
                            }
                            p_curr = p_node.borrow().next.clone();
                        }
                    }
                    i_curr = i_node.borrow().next.clone();
                }
            }
            g_curr = g_node.borrow().next.clone();
        }
        productos
    }

    /// Retorna los productos de un grupo (a través de todos sus investigadores).
    pub fn get_productos_by_grupo(&self, group_id: i64, only_active: bool) -> Vec<Producto> {
        let mut productos = Vec::new();
        if let Some(g_node) = self.get_group_node_by_id(group_id) {
            if !only_active || g_node.borrow().active {
                let mut i_curr = g_node.borrow().sublist.clone();
                while let Some(i_node) = i_curr {
                    if !only_active || i_node.borrow().active {
                        let mut p_curr = i_node.borrow().sublist.clone();
                        while let Some(p_node) = p_curr {
                            if !only_active || p_node.borrow().active {
                                productos.push(p_node.borrow().data.clone());
                            }
                            p_curr = p_node.borrow().next.clone();
                        }
                    }
                    i_curr = i_node.borrow().next.clone();
                }
            }
        }
        productos
    }

    /// Busca un producto por ID en toda la Multilista.
    pub fn find_producto(&self, prod_id: &str) -> Option<Producto> {
        let pid = prod_id.trim();
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                let mut p_curr = i_node.borrow().sublist.clone();
                while let Some(p_node) = p_curr {
                    if p_node.borrow().data.id.as_deref() == Some(pid) {
                        return Some(p_node.borrow().data.clone());
                    }
                    p_curr = p_node.borrow().next.clone();
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        None
    }

    /// Actualiza un producto por ID.
    pub fn update_producto(&mut self, prod_id: &str, new_prod: Producto) -> bool {
        let pid = prod_id.trim();
        let mut updated = false;
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                let mut p_curr = i_node.borrow().sublist.clone();
                while let Some(p_node) = p_curr {
                    if p_node.borrow().data.id.as_deref() == Some(pid) {
                        p_node.borrow_mut().data = new_prod.clone();
                        updated = true;
                    }
                    p_curr = p_node.borrow().next.clone();
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        updated
    }

    /// Desactiva un producto por ID.
    pub fn deactivate_producto(&mut self, prod_id: &str) -> bool {
        let pid = prod_id.trim();
        let mut modified = false;
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                let mut p_curr = i_node.borrow().sublist.clone();
                while let Some(p_node) = p_curr {
                    if p_node.borrow().data.id.as_deref() == Some(pid) {
                        p_node.borrow_mut().active = false;
                        p_node.borrow_mut().data.activo = false;
                        modified = true;
                    }
                    p_curr = p_node.borrow().next.clone();
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        modified
    }

    /// Activa un producto por ID.
    pub fn activate_producto(&mut self, prod_id: &str) -> bool {
        let pid = prod_id.trim();
        let mut modified = false;
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                let mut p_curr = i_node.borrow().sublist.clone();
                while let Some(p_node) = p_curr {
                    if p_node.borrow().data.id.as_deref() == Some(pid) {
                        p_node.borrow_mut().active = true;
                        p_node.borrow_mut().data.activo = true;
                        modified = true;
                    }
                    p_curr = p_node.borrow().next.clone();
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }
        modified
    }

    /// Elimina físicamente un producto de su sublista, retornándolo para el Undo Stack.
    pub fn remove_producto(&mut self, prod_id: &str) -> Option<Producto> {
        let pid = prod_id.trim();
        let mut removed_prod = None;

        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let mut i_curr = g_node.borrow().sublist.clone();
            while let Some(i_node) = i_curr {
                let mut prev_p: Option<ProductNodeRef> = None;
                let mut curr_p = i_node.borrow().sublist.clone();

                while let Some(p_node) = curr_p {
                    let matches = p_node.borrow().data.id.as_deref() == Some(pid);
                    let next_p = p_node.borrow().next.clone();

                    if matches {
                        if removed_prod.is_none() {
                            removed_prod = Some(p_node.borrow().data.clone());
                        }

                        if let Some(prev) = prev_p.clone() {
                            prev.borrow_mut().next = next_p.clone();
                        } else {
                            i_node.borrow_mut().sublist = next_p.clone();
                        }

                        if let Some(next) = next_p.clone() {
                            next.borrow_mut().prev = prev_p.as_ref().map(Rc::downgrade);
                        }

                        p_node.borrow_mut().next = None;
                        p_node.borrow_mut().prev = None;
                    } else {
                        prev_p = Some(Rc::clone(&p_node));
                    }
                    curr_p = next_p;
                }
                i_curr = i_node.borrow().next.clone();
            }
            g_curr = g_node.borrow().next.clone();
        }

        removed_prod
    }

    // ── ITERADORES Y CONSULTAS ─────────────────────────────────────────────

    /// Itera todos los grupos (opcionalmente solo activos).
    pub fn iterate_groups(&self, only_active: bool) -> Vec<Grupo> {
        let mut list = Vec::new();
        let mut curr = self.head_group.clone();
        while let Some(node) = curr {
            if !only_active || node.borrow().active {
                list.push(node.borrow().data.clone());
            }
            curr = node.borrow().next.clone();
        }
        list
    }

    /// Itera investigadores activos o todos, opcionalmente filtrados por grupo.
    pub fn iterate_investigadores(
        &self,
        group_id: Option<i64>,
        only_active: bool,
    ) -> Vec<Investigador> {
        let mut list = Vec::new();
        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let gid_matches = group_id.is_none() || g_node.borrow().data.id == group_id;
            if gid_matches && (!only_active || g_node.borrow().active) {
                let mut i_curr = g_node.borrow().sublist.clone();
                while let Some(i_node) = i_curr {
                    if !only_active || i_node.borrow().active {
                        let inv = i_node.borrow().data.clone();
                        if !list.iter().any(|existing: &Investigador| existing.cedula == inv.cedula) {
                            list.push(inv);
                        }
                    }
                    i_curr = i_node.borrow().next.clone();
                }
            }
            g_curr = g_node.borrow().next.clone();
        }
        list
    }

    /// Itera productos con filtros opcionales (grupo, investigador, año).
    pub fn iterate_productos(
        &self,
        group_id: Option<i64>,
        cedula: Option<&str>,
        anio: Option<i32>,
        only_active: bool,
    ) -> Vec<Producto> {
        let mut list = Vec::new();
        let ced_filter = cedula.map(|c| c.trim().to_lowercase());

        let mut g_curr = self.head_group.clone();
        while let Some(g_node) = g_curr {
            let gid_matches = group_id.is_none() || g_node.borrow().data.id == group_id;
            if gid_matches && (!only_active || g_node.borrow().active) {
                let mut i_curr = g_node.borrow().sublist.clone();
                while let Some(i_node) = i_curr {
                    let inv_matches = match &ced_filter {
                        Some(c) => i_node.borrow().data.cedula.trim().to_lowercase() == *c,
                        None => true,
                    };

                    if inv_matches && (!only_active || i_node.borrow().active) {
                        let mut p_curr = i_node.borrow().sublist.clone();
                        while let Some(p_node) = p_curr {
                            if !only_active || p_node.borrow().active {
                                let anio_matches = match anio {
                                    Some(y) => p_node.borrow().data.anio == Some(y),
                                    None => true,
                                };
                                if anio_matches {
                                    let p_data = p_node.borrow().data.clone();
                                    if !list.iter().any(|existing: &Producto| existing.id == p_data.id && p_data.id.is_some()) {
                                        list.push(p_data);
                                    }
                                }
                            }
                            p_curr = p_node.borrow().next.clone();
                        }
                    }
                    i_curr = i_node.borrow().next.clone();
                }
            }
            g_curr = g_node.borrow().next.clone();
        }
        list
    }
}
