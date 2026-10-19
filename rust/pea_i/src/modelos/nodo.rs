//! Nodo genérico para estructuras enlazadas (Lista Doble, Pila, Cola y Multilista).
//!
//! # Elección de diseño para enlace doble:
//! Se utiliza `Rc<RefCell<Node<T>>>` para el enlace hacia adelante (`next`) y `Weak<RefCell<Node<T>>>`
//! para el enlace hacia atrás (`prev`).
//!
//! **¿Por qué esta elección?**
//! 1. **Prevención de fugas de memoria (Reference Cycles):** Si ambos enlaces fueran `Rc`, se formaría
//!    un ciclo fuerte de referencias impidiendo que el recolector de memoria libere los nodos. El puntero
//!    débil (`Weak`) rompe el ciclo y asegura que al eliminar un nodo o la lista, la memoria se libere
//!    de inmediato.
//! 2. **Fidelidad al modelo:** Replica con exactitud la semántica del `Node` de Python (`next`, `prev`,
//!    `active`, `data`) manteniendo mutabilidad interior segura en tiempo de ejecución (`RefCell`).
//! 3. **Ausencia de `Vec`:** A diferencia de un "arena basado en índices" que internamente requiere un
//!    vector contiguo para alojar nodos, `Rc`/`Weak` aloja cada nodo individualmente en el heap,
//!    cumpliendo estrictamente con la restricción del taller de no usar `Vec` ni `HashMap` como
//!    estructura principal del modelo.

use std::cell::RefCell;
use std::rc::{Rc, Weak};

pub type NodeRef<T> = Rc<RefCell<Node<T>>>;
pub type WeakNodeRef<T> = Weak<RefCell<Node<T>>>;

#[derive(Debug)]
pub struct Node<T> {
    pub data: T,
    pub next: Option<NodeRef<T>>,
    pub prev: Option<WeakNodeRef<T>>,
    pub active: bool,
}

impl<T> Node<T> {
    pub fn new(data: T) -> Self {
        Self {
            data,
            next: None,
            prev: None,
            active: true,
        }
    }

    pub fn new_ref(data: T) -> NodeRef<T> {
        Rc::new(RefCell::new(Self::new(data)))
    }

    pub fn is_active(&self) -> bool {
        self.active
    }

    pub fn deactivate(&mut self) {
        self.active = false;
    }

    pub fn activate(&mut self) {
        self.active = true;
    }
}
