//! Lista doblemente enlazada genérica para almacenamiento en memoria.
//!
//! Implementada con `Rc<RefCell<Node<T>>>` para enlaces siguientes (`next`)
//! y `Weak<RefCell<Node<T>>>` para enlaces anteriores (`prev`).

use super::nodo::{Node, NodeRef};
use std::rc::Rc;

#[derive(Debug, Default)]
pub struct DoublyLinkedList<T> {
    pub head: Option<NodeRef<T>>,
    pub tail: Option<NodeRef<T>>,
    pub size: usize,
}

impl<T> DoublyLinkedList<T> {
    pub fn new() -> Self {
        Self {
            head: None,
            tail: None,
            size: 0,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    pub fn len(&self) -> usize {
        self.size
    }

    /// Agrega un dato al final de la lista.
    pub fn append(&mut self, data: T) -> NodeRef<T> {
        let new_node = Node::new_ref(data);
        match self.tail.take() {
            Some(old_tail) => {
                new_node.borrow_mut().prev = Some(Rc::downgrade(&old_tail));
                old_tail.borrow_mut().next = Some(Rc::clone(&new_node));
                self.tail = Some(Rc::clone(&new_node));
            }
            None => {
                self.head = Some(Rc::clone(&new_node));
                self.tail = Some(Rc::clone(&new_node));
            }
        }
        self.size += 1;
        new_node
    }

    /// Agrega un dato al inicio de la lista.
    pub fn prepend(&mut self, data: T) -> NodeRef<T> {
        let new_node = Node::new_ref(data);
        match self.head.take() {
            Some(old_head) => {
                old_head.borrow_mut().prev = Some(Rc::downgrade(&new_node));
                new_node.borrow_mut().next = Some(Rc::clone(&old_head));
                self.head = Some(Rc::clone(&new_node));
            }
            None => {
                self.head = Some(Rc::clone(&new_node));
                self.tail = Some(Rc::clone(&new_node));
            }
        }
        self.size += 1;
        new_node
    }

    /// Obtiene el nodo en la posición indicada.
    pub fn get_node(&self, index: usize) -> Option<NodeRef<T>> {
        if index >= self.size {
            return None;
        }
        let mut curr = self.head.clone();
        for _ in 0..index {
            curr = curr.and_then(|n| n.borrow().next.clone());
        }
        curr
    }

    /// Desvincula físicamente un nodo de la lista doblemente enlazada.
    pub fn unlink(&mut self, node: &NodeRef<T>) {
        let prev_weak = node.borrow_mut().prev.take();
        let next_rc = node.borrow_mut().next.take();

        if let Some(prev_rc) = prev_weak.as_ref().and_then(|w| w.upgrade()) {
            prev_rc.borrow_mut().next = next_rc.clone();
        } else {
            // Era el head
            self.head = next_rc.clone();
        }

        if let Some(next_node) = next_rc {
            next_node.borrow_mut().prev = prev_weak;
            if let Some(head) = &self.head {
                if Rc::ptr_eq(node, head) {
                    next_node.borrow_mut().prev = None;
                }
            }
        } else {
            // Era el tail
            self.tail = prev_weak.as_ref().and_then(|w| w.upgrade());
        }

        if self.size > 0 {
            self.size -= 1;
        }
    }

    /// Elimina físicamente el primer nodo que coincida con el predicado.
    pub fn remove_first<F>(&mut self, mut predicate: F) -> Option<T>
    where
        F: FnMut(&T) -> bool,
        T: Clone,
    {
        let mut curr = self.head.clone();
        while let Some(node) = curr {
            let matches = predicate(&node.borrow().data);
            if matches {
                let data = node.borrow().data.clone();
                self.unlink(&node);
                return Some(data);
            }
            curr = node.borrow().next.clone();
        }
        None
    }

    /// Limpia todos los elementos de la lista rompiendo ciclos.
    pub fn clear(&mut self) {
        let mut curr = self.head.take();
        while let Some(node) = curr {
            node.borrow_mut().prev = None;
            curr = node.borrow_mut().next.take();
        }
        self.tail = None;
        self.size = 0;
    }
}

impl<T: Clone> DoublyLinkedList<T> {
    /// Colecciona los datos activos en un `Vec` auxiliar para visualización o guardado.
    pub fn collect_active(&self) -> Vec<T> {
        let mut result = Vec::new();
        let mut curr = self.head.clone();
        while let Some(node) = curr {
            if node.borrow().active {
                result.push(node.borrow().data.clone());
            }
            curr = node.borrow().next.clone();
        }
        result
    }

    /// Colecciona todos los datos en un `Vec` auxiliar.
    pub fn to_vec(&self) -> Vec<T> {
        let mut result = Vec::new();
        let mut curr = self.head.clone();
        while let Some(node) = curr {
            result.push(node.borrow().data.clone());
            curr = node.borrow().next.clone();
        }
        result
    }
}
