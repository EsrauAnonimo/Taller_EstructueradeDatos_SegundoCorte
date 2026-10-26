#pragma once

// ============================================================================
//  estructuras.hpp
//  Taller de Estructura de Datos - Segundo Corte
//
//  Contiene:
//    1. La estructura Producto (id, titulo, anio, categoria, validado).
//    2. Una Lista Enlazada Simple (nodos con punteros) reutilizable para
//       almacenar tanto Investigadores como Productos.
//
//  Las funciones estan definidas en este mismo encabezado porque son
//  plantillas (template) o estan marcadas como "inline"; esto permite
//  incluir el archivo en varios .cpp sin provocar errores de enlace.
// ============================================================================

#include <iostream>
#include <string>

// Reutilizamos la estructura Investigador definida en investigador.hpp
// (mismo taller, mismo modulo).
#include "investigador.hpp"

// ============================================================================
//  1. Estructura Producto
// ============================================================================
struct Producto {
    int id;
    std::string titulo;
    int anio;  // Se escribe "anio" (sin tilde) porque los identificadores de
               // C++ no deben contener caracteres especiales.
    std::string categoria;
    bool validado;
};

// ----------------------------------------------------------------------------
// Operadores de flujo (operator<<)
// Permite imprimir un Investigador o un Producto con std::cout << objeto.
// Se usan dentro de mostrar() de la lista para que esta funcione con
// cualquier tipo que tenga su propio operator<<.
// ----------------------------------------------------------------------------
inline std::ostream& operator<<(std::ostream& os, const Investigador& inv) {
    os << "ID: " << inv.id
       << " | Nombre: " << inv.nombre
       << " | Area: " << inv.areaConocimiento
       << " | Categoria: " << inv.categoria;
    return os;  // Se devuelve el flujo para poder encadenar operaciones.
}

inline std::ostream& operator<<(std::ostream& os, const Producto& prod) {
    os << "ID: " << prod.id
       << " | Titulo: " << prod.titulo
       << " | Anio: " << prod.anio
       << " | Categoria: " << prod.categoria
       << " | Validado: " << (prod.validado ? "si" : "no");
    return os;
}

// ============================================================================
//  2. Lista Enlazada Simple
//
//  Un nodo es una pequena estructura de memoria con dos partes:
//      - dato:      almacena el objeto (Investigador o Producto).
//      - siguiente: PUNTERO que guarda la DIRECCION de memoria del siguiente
//                   nodo de la cadena. Si es "nullptr" (nulo), el nodo es el
//                   ultimo de la lista.
//
//  La lista "cabeza" (o head) es un puntero al primer nodo. Toda la lista se
//  recorre empezando por ese puntero y saltando de uno a otro mediante
//  "->siguiente".
//
//  Al ser una plantilla (template), el mismo codigo sirve para
//  ListaEnlazada<Investigador> y ListaEnlazada<Producto> sin duplicar logicas.
//  La unica restriccion es que el tipo T tenga un campo "int id", pues buscar
//  y eliminar comparan por ese campo.
// ============================================================================
template <typename T>
class ListaEnlazada {
public:
    // -----------------------------------------------------------------
    // Nodo: definido publicamente para poder recorrerlo desde el main
    // (por ejemplo, usando el puntero que devuelve buscar()).
    // -----------------------------------------------------------------
    struct Nodo {
        T dato;
        Nodo* siguiente;  // Puntero al siguiente nodo (o nullptr si es el ultimo).

        // explicit: evita conversiones implicitas accidentales al crear nodos.
        explicit Nodo(const T& d) : dato(d), siguiente(nullptr) {}
    };

    // -----------------------------------------------------------------
    // Constructor: la lista empieza vacia, por eso cabeza = nullptr.
    // nullptr significa "no apunta a ningun nodo todavia".
    // -----------------------------------------------------------------
    ListaEnlazada() : cabeza(nullptr) {}

    // -----------------------------------------------------------------
    // Destructor: recorre la lista y libera la memoria de cada nodo.
    // Como los nodos se crean con "new" (memoria en el heap), sin este
    // metodo la lista provocaria fugas de memoria (memory leak).
    // -----------------------------------------------------------------
    ~ListaEnlazada() {
        while (cabeza != nullptr) {
            Nodo* temp = cabeza;   // temp guarda la direccion del nodo actual...
            cabeza = cabeza->siguiente;  // ...la lista "adelanta" su cabeza...
            delete temp;                // ...y recien ahi se borra el nodo viejo.
        }
    }

    // -----------------------------------------------------------------
    // Regla de los tres: como la lista maneja punteros con new/delete,
    // prohibimos copiarla. Si alguien intentara hacer "lista2 = lista1",
    // el compilador la rechazara, evitando que dos listas apunten a los
    // mismos nodos y borren la memoria dos veces (double free).
    // -----------------------------------------------------------------
    ListaEnlazada(const ListaEnlazada&) = delete;
    ListaEnlazada& operator=(const ListaEnlazada&) = delete;

    // -----------------------------------------------------------------
    // INSERTAR: agrega un nuevo nodo al INICIO de la lista (costo O(1)).
    //
    // Logica de los punteros, paso a paso:
    //   1. "new Nodo(...)" crea el nodo en el heap y devuelve su direccion,
    //      que guardamos en "nuevo".
    //   2. "nuevo->siguiente = cabeza" hace que el nodo nuevo apunte al que
    //      hasta ahora era el primero (nada se pierde de la cadena).
    //   3. "cabeza = nuevo" convierte al nodo nuevo en el primer nodo.
    // -----------------------------------------------------------------
    void insertar(const T& nuevoDato) {
        Nodo* nuevo = new Nodo(nuevoDato);
        nuevo->siguiente = cabeza;  // El nuevo nodo "engancha" la cadena vieja.
        cabeza = nuevo;             // El nuevo nodo pasa a ser la cabeza.
    }

    // -----------------------------------------------------------------
    // ELIMINAR: busca el nodo con ese id y lo saca de la cadena.
    // Devuelve true si lo encontro y false si el id no existe.
    //
    // Logica de los punteros:
    //   - "anterior" y "actual" caminan juntos por la lista. Cuando se
    //     encuentra el nodo a borrar, basta con que "anterior->siguiente"
    //     deje de apuntar a "actual" y pase a apuntar a "actual->siguiente":
    //     el nodo queda fuera de la cadena y se libera con delete.
    //   - Caso especial: si "anterior == nullptr" el nodo a borrar es la
    //     cabeza, asi que la nueva cabeza pasa a ser "actual->siguiente".
    // -----------------------------------------------------------------
    bool eliminar(int id) {
        Nodo* actual = cabeza;
        Nodo* anterior = nullptr;

        // Recorremos mientras no lleguemos al final ni encontremos el id.
        while (actual != nullptr && actual->dato.id != id) {
            anterior = actual;              // anterior se queda un paso atras.
            actual = actual->siguiente;     // actual avanza al siguiente nodo.
        }

        if (actual == nullptr) {
            return false;  // El id no esta en la lista; nada que borrar.
        }

        if (anterior == nullptr) {
            cabeza = actual->siguiente;  // Borramos la cabeza: la nueva cabeza
                                         // es el segundo nodo.
        } else {
            // "Saltamos" el nodo a borrar: anterior ahora apunta al que le
            // seguia a actual, dejando a "actual" fuera de la cadena.
            anterior->siguiente = actual->siguiente;
        }

        delete actual;  // Recien aqui se libera la memoria del nodo borrado.
        return true;
    }

    // -----------------------------------------------------------------
    // BUSCAR: recorre la lista nodo por nodo hasta encontrar el id.
    // Devuelve un PUNTERO al nodo encontrado (para acceder a su dato con
    // ->dato) o nullptr si no existe.
    //
    // Logica del puntero de avance:
    //   "actual = actual->siguiente" es equivalente a "avanzar al siguiente
    //   nodo": se reemplaza la direccion guardada en "actual" por la del
    //   siguiente. Cuando "actual" valga nullptr, se llego al final.
    // -----------------------------------------------------------------
    Nodo* buscar(int id) {
        Nodo* actual = cabeza;
        while (actual != nullptr) {
            if (actual->dato.id == id) {
                return actual;  // Encontrado: devolvemos el nodo.
            }
            actual = actual->siguiente;  // Avanzamos al siguiente nodo.
        }
        return nullptr;  // Se recorrio toda la lista sin encontrar el id.
    }

    // -----------------------------------------------------------------
    // MOSTRAR: recorre la lista completa e imprime cada dato.
    // Usa el mismo esquema de avance que buscar().
    // Es const porque no modifica la lista; solo "lee" con punteros.
    // -----------------------------------------------------------------
    void mostrar() const {
        if (cabeza == nullptr) {
            std::cout << "(la lista esta vacia)" << std::endl;
            return;
        }

        Nodo* actual = cabeza;  // Empezamos por el primer nodo.
        while (actual != nullptr) {
            std::cout << actual->dato << std::endl;  // Imprime el dato actual
                                                    // con su operator<<.
            actual = actual->siguiente;             // Avanzamos al siguiente.
        }
    }

    // -----------------------------------------------------------------
    // vacia: devuelve true si la lista no tiene nodos.
    // -----------------------------------------------------------------
    bool vacia() const {
        return cabeza == nullptr;
    }

    // -----------------------------------------------------------------
    // primero: devuelve la DIRECCION del primer nodo (o nullptr si la
    // lista esta vacia). Sirve para que el codigo externo (por ejemplo el
    // menu de main.cpp) pueda recorrer la lista con un puntero auxiliar:
    //     for (Nodo* n = lista.primero(); n != nullptr; n = n->siguiente)
    // -----------------------------------------------------------------
    Nodo* primero() const {
        return cabeza;
    }

    // -----------------------------------------------------------------
    // contar: recorre la lista con un puntero auxiliar y cuenta los nodos.
    // No se guarda un contador aparte para no desincronizarlo al insertar
    // o eliminar; el costo es O(n).
    // -----------------------------------------------------------------
    int contar() const {
        int total = 0;
        for (Nodo* actual = cabeza; actual != nullptr; actual = actual->siguiente) {
            ++total;
        }
        return total;
    }

private:
    Nodo* cabeza;  // Puntero al primer nodo; nullptr = lista vacia.
};

// ----------------------------------------------------------------------------
// Alias de uso comodo: en vez de escribir ListaEnlazada<Investigador>,
// podemos escribir ListaInvestigadores y ListaProductos.
// ----------------------------------------------------------------------------
using ListaInvestigadores = ListaEnlazada<Investigador>;
using ListaProductos = ListaEnlazada<Producto>;
