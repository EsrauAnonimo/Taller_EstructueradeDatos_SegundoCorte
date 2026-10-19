//! Pila (Stack LIFO) propia para almacenar el historial de eliminaciones (Deshacer / Undo).
//!
//! Implementada como una lista simplemente enlazada dinámica mediante `Box<StackNode<T>>`,
//! sin usar `Vec` ni `VecDeque` como estructura principal.

use super::entidades::{Grupo, Investigador, Producto};

#[derive(Debug)]
struct StackNode<T> {
    data: T,
    next: Option<Box<StackNode<T>>>,
}

#[derive(Debug, Default)]
pub struct Stack<T> {
    top: Option<Box<StackNode<T>>>,
    size: usize,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Self { top: None, size: 0 }
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    pub fn len(&self) -> usize {
        self.size
    }

    /// Inserta un elemento en la cima de la pila.
    pub fn push(&mut self, data: T) {
        let new_node = Box::new(StackNode {
            data,
            next: self.top.take(),
        });
        self.top = Some(new_node);
        self.size += 1;
    }

    /// Extrae y retorna el elemento en la cima de la pila.
    pub fn pop(&mut self) -> Option<T> {
        self.top.take().map(|node| {
            self.top = node.next;
            self.size -= 1;
            node.data
        })
    }

    /// Retorna una referencia al elemento en la cima sin extraerlo.
    pub fn peek(&self) -> Option<&T> {
        self.top.as_deref().map(|node| &node.data)
    }

    /// Vacía la pila completamente.
    pub fn clear(&mut self) {
        while self.pop().is_some() {}
    }
}

/// Registro de operación para la pila de deshacer
#[derive(Debug, Clone)]
pub enum OperacionDeshacer {
    Grupo {
        grupo: Grupo,
        investigadores: Vec<(Investigador, Vec<Producto>)>,
    },
    Investigador {
        investigador: Investigador,
        productos: Vec<Producto>,
    },
    Producto {
        producto: Producto,
    },
}

impl OperacionDeshacer {
    pub fn descripcion(&self) -> String {
        match self {
            OperacionDeshacer::Grupo { grupo, investigadores } => {
                format!(
                    "Grupo '{}' (ID: {:?}) con {} investigadores",
                    grupo.nombre,
                    grupo.id,
                    investigadores.len()
                )
            }
            OperacionDeshacer::Investigador { investigador, productos } => {
                format!(
                    "Investigador '{}' (Cédula: {}) con {} productos",
                    investigador.nombre_completo(),
                    investigador.cedula,
                    productos.len()
                )
            }
            OperacionDeshacer::Producto { producto } => {
                format!(
                    "Producto '{}' (ID: {:?})",
                    producto.titulo,
                    producto.id
                )
            }
        }
    }
}
