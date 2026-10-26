#pragma once

// ============================================================================
//  grupos.hpp
//  Taller de Estructura de Datos - Segundo Corte
//
//  Contiene:
//    1. La estructura Grupo, que reune un equipo de investigacion: sus datos
//       basicos, su lista de Investigadores y su lista de Productos.
//    2. La clase Pila (LIFO) con nodos enlazados, para guardar un historial
//       de cambios (cadenas descriptivas).
//    3. La clase Cola (FIFO) con nodos enlazados, para una cola de
//       validacion de productos (guardando IDs de productos).
//
//  Todas las funciones se definen dentro de las clases; de ese modo son
//  "inline" y el archivo puede incluirse en varios .cpp sin errores de enlace.
// ============================================================================

#include <iostream>
#include <string>

// Reutilizamos Producto, Investigador y la ListaEnlazada<T>.
#include "estructuras.hpp"
#include "investigador.hpp"

// Declaraciones de funciones de indicador
inline double calcularPuntajeProducto(const Producto& p);
inline double calcularIndicadorInvestigador(const Investigador& inv, int anioInicio, int anioFin);

// ============================================================================
//  1. Estructura Grupo
//
//  Un Grupo "tiene" dos listas (composicion): la lista de integrantes y la
//  lista de productos pertenecen al grupo y se destruyen junto con el,
//  gracias a que ListaEnlazada libera sus nodos en su propio destructor.
// ============================================================================
struct Grupo {
    int id;
    std::string nombre;
    std::string plan;
    ListaInvestigadores integrantes;  // Lista enlazada de Investigadores.
    ListaProductos productos;         // Lista enlazada de Productos.
    bool activo = true;

    // Constructor por comodidad: crea un grupo vacio (listas vacias).
    Grupo(int idGrupo, const std::string& nombreGrupo, const std::string& planGrupo)
        : id(idGrupo), nombre(nombreGrupo), plan(planGrupo), activo(true) {
        // Las listas se construyen solas (sus constructores dejan las
        // cabezas en nullptr), por eso no hay nada que hacer aqui.
    }

    // -------------------------------------------------------------------
    // INSERTAR: agrega un investigador o un producto al grupo.
    // Se delega en la lista correspondiente, que es quien maneja los
    // punteros y la memoria de los nodos.
    // -------------------------------------------------------------------
    void insertarInvestigador(const Investigador& investigador) {
        integrantes.insertar(investigador);
    }

    void insertarProducto(const Producto& producto) {
        productos.insertar(producto);
    }

    // -------------------------------------------------------------------
    // ELIMINAR: quita por id un investigador o un producto del grupo.
    // Devuelve true si se elimino y false si el id no existia.
    // -------------------------------------------------------------------
    bool eliminarInvestigador(int idInvestigador) {
        return integrantes.eliminar(idInvestigador);
    }

    bool eliminarProducto(int idProducto) {
        return productos.eliminar(idProducto);
    }

    // -------------------------------------------------------------------
    // MOSTRAR: imprime los datos del grupo y luego el contenido de sus
    // dos listas. Es const porque solo lee, aunque internamente recorra
    // punteros.
    // -------------------------------------------------------------------
    void mostrar() const {
        std::cout << "Grupo " << id << ": " << nombre
                  << " (Plan: " << plan << ")" << std::endl;

        std::cout << "  Integrantes:" << std::endl;
        integrantes.mostrar();

        std::cout << "  Productos:" << std::endl;
        productos.mostrar();
    }

    // -------------------------------------------------------------------
    // VACIA: el grupo esta vacio cuando no tiene integrantes ni productos.
    // -------------------------------------------------------------------
    bool vacia() const {
        return integrantes.vacia() && productos.vacia();
    }
};

// Función para calcular indicador de investigador
inline double calcularIndicadorInvestigador(const Investigador& inv, int anioInicio, int anioFin) {
    double total = 0.0;
    if (!inv.activo) return 0.0;
    // If we have a pointer to misProductos
    if (inv.misProductosPtr != nullptr) {
        for (ListaProductos::Nodo* nodo = inv.misProductosPtr->primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            const Producto& p = nodo->dato;
            if (p.activo && p.validado) {
                if (p.anio >= anioInicio && p.anio <= anioFin) {
                    total += calcularPuntajeProducto(p);
                }
            }
        }
        return total;
    }
    return 0.0;
}

// Función para calcular indicador de grupo
inline double calcularIndicadorGrupo(const Grupo& g, int anioInicio, int anioFin) {
    double total = 0.0;
    if (!g.activo) return 0.0;
    for (ListaInvestigadores::Nodo* nodo = g.integrantes.primero();
         nodo != nullptr; nodo = nodo->siguiente) {
        total += calcularIndicadorInvestigador(nodo->dato, anioInicio, anioFin);
    }
    return total;
}

// ============================================================================
//  2. Clase Pila (LIFO: Last In, First Out)
//
//  El ultimo elemento que entra es el primero que sale. Es ideal para un
//  historial de cambios: el cambio mas reciente queda en la "cima" y es el
//  primero en deshacerse.
//
//  Se implementa con nodos enlazados. El unico puntero necesario es "tope",
//  que apunta al nodo de arriba; no hace falta recorrer nada para insertar
//  ni para eliminar, por lo que ambas operaciones son O(1).
// ============================================================================
class Pila {
public:
    // Nodo de la pila: guarda un texto (string) y el puntero al nodo de
    // abajo.
    struct Nodo {
        std::string dato;   // Texto descriptivo del cambio.
        Nodo* siguiente;    // Puntero al nodo que esta debajo (o nullptr).

        explicit Nodo(const std::string& d) : dato(d), siguiente(nullptr) {}
    };

    // La pila nace vacia: el tope no apunta a ningun nodo.
    Pila() : tope(nullptr) {}

    // Destructor: libera todos los nodos para no dejar memoria sin liberar.
    ~Pila() {
        while (tope != nullptr) {
            Nodo* temp = tope;           // Guardamos el nodo de arriba...
            tope = tope->siguiente;      // ...bajamos el tope al de abajo...
            delete temp;                 // ...y borramos el nodo viejo.
        }
    }

    // Evitamos copias (dos pilas compartirian los mismos nodos y se
    // borrarian dos veces). Buena practica al manejar memoria con new/delete.
    Pila(const Pila&) = delete;
    Pila& operator=(const Pila&) = delete;

    // -------------------------------------------------------------------
    // INSERTAR (push): apila un cambio en la cima.
    //
    // Logica de punteros:
    //   1. "new Nodo(...)" crea el nodo en el heap y devuelve su direccion.
    //   2. "nuevo->siguiente = tope" hace que el nodo nuevo apunte al que
    //      era el de arriba (asi la cadena anterior queda debajo).
    //   3. "tope = nuevo" convierte al nodo nuevo en la nueva cima.
    // -------------------------------------------------------------------
    void insertar(const std::string& cambio) {
        Nodo* nuevo = new Nodo(cambio);
        nuevo->siguiente = tope;  // El nuevo nodo apunta al anterior tope.
        tope = nuevo;             // El nuevo nodo pasa a ser el tope.
    }

    // -------------------------------------------------------------------
    // ELIMINAR (pop): desapila el nodo de la cima.
    // Devuelve true si habia algo que quitar; false si la pila estaba vacia.
    //
    // Logica de punteros:
    //   Se guarda el tope en "temp", el tope baja a "tope->siguiente" y
    //   recien entonces se hace "delete temp" (nunca antes, porque si se
    //   borrara primero se perderia la direccion del nodo de abajo).
    // -------------------------------------------------------------------
    bool eliminar() {
        if (tope == nullptr) {
            return false;  // Pila vacia: no hay cima que quitar.
        }

        Nodo* temp = tope;          // temp apunta al nodo a liberar.
        tope = tope->siguiente;     // El tope baja al nodo de abajo.
        delete temp;                // Liberamos el nodo que estaba arriba.
        return true;
    }

    // -------------------------------------------------------------------
    // CIMA: devuelve un puntero al texto que esta arriba, o nullptr si la
    // pila esta vacia. Devolver puntero evita copiar el string y permite
    // comprobar con "== nullptr" si habia dato.
    // -------------------------------------------------------------------
    const std::string* cima() const {
        if (tope == nullptr) {
            return nullptr;
        }
        return &tope->dato;  // Direccion del dato del nodo del tope.
    }

    // -------------------------------------------------------------------
    // MOSTRAR: recorre la pila desde la cima hacia abajo.
    // El puntero "actual" empieza en el tope y avanza con "->siguiente"
    // hasta valer nullptr (final de la cadena).
    // -------------------------------------------------------------------
    void mostrar() const {
        if (tope == nullptr) {
            std::cout << "(la pila esta vacia)" << std::endl;
            return;
        }

        Nodo* actual = tope;  // Empezamos por arriba.
        while (actual != nullptr) {
            std::cout << "  " << actual->dato << std::endl;
            actual = actual->siguiente;  // Bajamos un nodo.
        }
    }

    // La pila esta vacia cuando el tope no apunta a ningun nodo.
    bool vacia() const {
        return tope == nullptr;
    }

private:
    Nodo* tope;  // Puntero al nodo de la cima; nullptr = pila vacia.
};

// ============================================================================
//  3. Clase Cola (FIFO: First In, First Out)
//
//  El primer elemento que entra es el primero que sale. Sirve para una cola
//  de validacion de productos: los productos se validan en el orden en que
//  llegaron.
//
//  A diferencia de la pila, la cola necesita DOS punteros:
//    - "frente": al primer nodo (por donde se elimina).
//    - "fin":    al ultimo nodo (por donde se inserta).
//  Con los dos, tanto insertar como eliminar son O(1); sin "fin" habria que
//  recorrer toda la cola para insertar al final.
// ============================================================================
class Cola {
public:
    // Nodo de la cola: guarda el id de un producto y el puntero al siguiente.
    struct Nodo {
        int dato;          // ID del producto a validar.
        Nodo* siguiente;   // Puntero al siguiente nodo (o nullptr).

        explicit Nodo(int d) : dato(d), siguiente(nullptr) {}
    };

    // La cola nace vacia: no hay frente ni fin.
    Cola() : frenteNodo(nullptr), finNodo(nullptr) {}

    // Destructor: recorre desde el frente y libera cada nodo.
    ~Cola() {
        while (frenteNodo != nullptr) {
            Nodo* temp = frenteNodo;            // Nodo a borrar (el del frente).
            frenteNodo = frenteNodo->siguiente; // El frente avanza.
            delete temp;                        // Liberamos el nodo viejo.
        }
        finNodo = nullptr;  // Por claridad: la cola quedo sin ultimo nodo.
    }

    // Evitamos copias por la misma razon que en la Pila.
    Cola(const Cola&) = delete;
    Cola& operator=(const Cola&) = delete;

    // -------------------------------------------------------------------
    // INSERTAR (enqueue): agrega un id al FINAL de la cola.
    //
    // Logica de punteros. Hay dos casos:
    //   a) Cola vacia: el nodo nuevo es a la vez frente y fin.
    //   b) Cola con elementos: se engancha el nodo nuevo despues del
    //      ultimo ("finNodo->siguiente = nuevo") y se mueve "finNodo" al
    //      nodo nuevo. El frente NO se toca.
    // -------------------------------------------------------------------
    void insertar(int idProducto) {
        Nodo* nuevo = new Nodo(idProducto);

        if (finNodo == nullptr) {
            // Caso a: la cola estaba vacia.
            frenteNodo = nuevo;
            finNodo = nuevo;
        } else {
            // Caso b: enganchamos al final y movemos el puntero de fin.
            finNodo->siguiente = nuevo;
            finNodo = nuevo;
        }
    }

    // -------------------------------------------------------------------
    // ELIMINAR (dequeue): quita el nodo del FRENTE (el mas antiguo).
    // Devuelve true si habia algo que quitar; false si estaba vacia.
    //
    // Logica de punteros:
    //   - temp guarda el nodo del frente; el frente pasa a "frente->siguiente".
    //   - Si tras avanzar el frente quedo en nullptr, la cola se vacio, y
    //     entonces tambien hay que poner "finNodo = nullptr" (si no, quedaria
    //     apuntando a memoria ya liberada: un "puntero colgante").
    // -------------------------------------------------------------------
    bool eliminar() {
        if (frenteNodo == nullptr) {
            return false;  // Cola vacia: no hay frente que quitar.
        }

        Nodo* temp = frenteNodo;                 // Nodo a liberar.
        frenteNodo = frenteNodo->siguiente;      // El frente avanza al siguiente.

        if (frenteNodo == nullptr) {
            finNodo = nullptr;  // Se vacio la cola: evitamos puntero colgante.
        }

        delete temp;  // Liberamos el nodo que estaba al frente.
        return true;
    }

    // -------------------------------------------------------------------
    // FRENTE: devuelve un puntero al id que esta al frente, o nullptr si la
    // cola esta vacia. Permite consultar sin eliminar.
    // -------------------------------------------------------------------
    const int* frente() const {
        if (frenteNodo == nullptr) {
            return nullptr;
        }
        return &frenteNodo->dato;  // Direccion del dato del nodo del frente.
    }

    // -------------------------------------------------------------------
    // MOSTRAR: recorre la cola desde el frente hasta el fin, avanzando con
    // "->siguiente" hasta llegar a nullptr.
    // -------------------------------------------------------------------
    void mostrar() const {
        if (frenteNodo == nullptr) {
            std::cout << "(la cola esta vacia)" << std::endl;
            return;
        }

        Nodo* actual = frenteNodo;  // Empezamos por el frente.
        while (actual != nullptr) {
            std::cout << "  Producto id: " << actual->dato << std::endl;
            actual = actual->siguiente;  // Avanzamos al siguiente nodo.
        }
    }

    // La cola esta vacia cuando el frente no apunta a ningun nodo.
    bool vacia() const {
        return frenteNodo == nullptr;
    }

private:
    Nodo* frenteNodo;  // Puntero al primer nodo (por donde se elimina).
    Nodo* finNodo;     // Puntero al ultimo nodo (por donde se inserta).
};
