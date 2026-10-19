//! Cola (Queue FIFO) propia para almacenar y procesar tareas de importación en lote.
//!
//! Implementada con nodos enlazados mediante `Rc<RefCell<QueueNode<T>>>`, con punteros `front`
//! y `rear` para operaciones O(1) de inserción y extracción, sin usar `VecDeque` ni `Vec` como
//! estructura principal.

use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
struct QueueNode<T> {
    data: T,
    next: Option<Rc<RefCell<QueueNode<T>>>>,
}

#[derive(Debug, Default)]
pub struct Queue<T> {
    front: Option<Rc<RefCell<QueueNode<T>>>>,
    rear: Option<Rc<RefCell<QueueNode<T>>>>,
    size: usize,
}

impl<T: Clone> Queue<T> {
    pub fn new() -> Self {
        Self {
            front: None,
            rear: None,
            size: 0,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.size == 0
    }

    pub fn len(&self) -> usize {
        self.size
    }

    /// Inserta un elemento al final de la cola (Enqueue).
    pub fn enqueue(&mut self, data: T) {
        let new_node = Rc::new(RefCell::new(QueueNode { data, next: None }));
        match self.rear.take() {
            Some(old_rear) => {
                old_rear.borrow_mut().next = Some(Rc::clone(&new_node));
                self.rear = Some(new_node);
            }
            None => {
                self.front = Some(Rc::clone(&new_node));
                self.rear = Some(new_node);
            }
        }
        self.size += 1;
    }

    /// Extrae y retorna el elemento al frente de la cola (Dequeue).
    pub fn dequeue(&mut self) -> Option<T> {
        self.front.take().map(|front_node| {
            let next_node = front_node.borrow_mut().next.take();
            self.front = next_node;
            if self.front.is_none() {
                self.rear = None;
            }
            self.size -= 1;
            // Desempaquetar el valor interno si es el único dueño o clonar
            match Rc::try_unwrap(front_node) {
                Ok(cell) => cell.into_inner().data,
                Err(rc) => rc.borrow().data.clone(),
            }
        })
    }

    /// Vacía la cola.
    pub fn clear(&mut self) {
        while self.dequeue().is_some() {}
    }
}

impl<T: Clone> Queue<T> {
    /// Inspecciona el elemento al frente sin extraerlo.
    pub fn peek(&self) -> Option<T> {
        self.front.as_ref().map(|f| f.borrow().data.clone())
    }

    /// Colecciona los datos de la cola para inspección visual.
    pub fn to_vec(&self) -> Vec<T> {
        let mut list = Vec::new();
        let mut curr = self.front.clone();
        while let Some(node) = curr {
            list.push(node.borrow().data.clone());
            curr = node.borrow().next.clone();
        }
        list
    }
}

/// Tarea que ingresa a la cola de importación
#[derive(Debug, Clone, PartialEq)]
pub enum TareaImportacion {
    Url { url: String, etiqueta: String },
    ArchivoCsv { ruta: String, etiqueta: String },
}

impl TareaImportacion {
    pub fn etiqueta(&self) -> &str {
        match self {
            TareaImportacion::Url { etiqueta, .. } => etiqueta,
            TareaImportacion::ArchivoCsv { etiqueta, .. } => etiqueta,
        }
    }
}
