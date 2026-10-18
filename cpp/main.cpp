// ============================================================================
//  main.cpp
//  Taller de Estructura de Datos - Segundo Corte
//
//  Programa principal con menu interactivo en consola para gestionar:
//    - Grupos de investigacion.
//    - Investigadores (pertenecientes a un grupo).
//    - Productos (pertenecientes a un grupo).
//
//  Caracteristicas:
//    - Titulo en arte ASCII y colores ANSI.
//    - CRUD completo (agregar, eliminar, modificar, mostrar).
//    - Filtro de productos por antiguedad (ultimos 2, 5 anios, etc.).
//    - Estadisticas en tablas alineadas con <iomanip> (setw).
//    - Persistencia en datos.csv (guardar y cargar al inicio).
//    - Validacion de TODAS las entradas para que el programa nunca se cierre
//      si el usuario escribe letras donde se esperan numeros.
//    - Historial de cambios usando una Pila y cola de validacion usando una
//      Cola (las clases definidas en grupos.hpp).
//
//  Compilacion (desde la carpeta raiz del repositorio):
//      g++ -std=c++17 -Wall -Wextra -I cpp cpp/main.cpp -o cpp/main.exe
//  Ejecucion:
//      cpp/main.exe
// ============================================================================

#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <ctime>

#ifdef _WIN32
#include <windows.h>  // Solo en Windows: para habilitar los colores ANSI.
// Algunas versiones del encabezado no definen esta constante; su valor es
// el estandar documentado por Microsoft (0x0004).
#ifndef ENABLE_VIRTUAL_TERMINAL_PROCESSING
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 0x0004
#endif
#endif

// Encabezados del taller (cada uno incluye lo que necesita).
#include "investigador.hpp"
#include "estructuras.hpp"
#include "grupos.hpp"

// ============================================================================
//  Colores ANSI
//  La secuencia "\033[...m" cambia el color del texto en la consola.
//  Se guardan en constantes para no repetir los codigos y para poder
//  "apagar" el color con RESET.
// ============================================================================
const std::string RESET     = "\033[0m";
const std::string CIAN      = "\033[1;36m";  // Titulos.
const std::string VERDE     = "\033[1;32m";  // Exitos.
const std::string ROJO      = "\033[1;31m";  // Errores.
const std::string AMARILLO  = "\033[1;33m";  // Avisos.
const std::string MAGENTA   = "\033[1;35m";  // Mensajes de sistema.

// Nombre del archivo de persistencia.
const std::string ARCHIVO_DATOS = "datos.csv";

// Banner del titulo: letras de bloque (caracter █) formando la palabra
// INVESTIGACION. Se usa este diseno porque es mas limpio y legible en la
// consola de Windows que el arte hecho con '#' y '.'.
const std::vector<std::string> BANNER = {
    "  █████  █   █  █   █  █████   ████  █████  █████   ███    ███    ███   █████   ███   █   █",
    "    █    ██  █  █   █  █      █        █      █    █   █  █   █  █   █    █    █   █  ██  █",
    "    █    █ █ █  █   █  ████    ███     █      █    █ ███  █████  █        █    █   █  █ █ █",
    "    █    █  ██   █ █   █          █    █      █    █   █  █   █  █   █    █    █   █  █  ██",
    "  █████  █   █    █    █████  ████     █    █████   ███   █   █   ███   █████   ███   █   █",
};

// ============================================================================
//  Datos globales del programa
//  "grupos" guarda PUNTEROS a los grupos. Se usan punteros porque Grupo
//  contiene dos ListaEnlazada y estas no se pueden copiar (su copia esta
//  borrada); guardando solo la direccion evitamos cualquier copia.
//  "historial" es la Pila de cambios y se declara una sola vez para todo el
//  programa.
// ============================================================================
std::vector<Grupo*> grupos;
Pila historial;

// ============================================================================
//  Habilitar colores ANSI en la consola de Windows
// ============================================================================
void habilitarColoresANSI() {
#ifdef _WIN32
    // Se cambia la pagina de codigo de salida a UTF-8 para que los caracteres
    // de bloque del banner (como █) se muestren correctamente en la consola.
    SetConsoleOutputCP(CP_UTF8);

    HANDLE salida = GetStdHandle(STD_OUTPUT_HANDLE);
    if (salida != INVALID_HANDLE_VALUE) {
        DWORD modo = 0;
        if (GetConsoleMode(salida, &modo)) {
            // ENABLE_VIRTUAL_TERMINAL_PROCESSING hace que la consola
            // interprete las secuencias ANSI como colores.
            SetConsoleMode(salida, modo | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
        }
    }
#endif
}

// ============================================================================
//  Funciones de mensajes (usan colores)
// ============================================================================
void exito(const std::string& mensaje) {
    std::cout << VERDE << "[OK] " << mensaje << RESET << std::endl;
}

void error(const std::string& mensaje) {
    std::cout << ROJO << "[ERROR] " << mensaje << RESET << std::endl;
}

void aviso(const std::string& mensaje) {
    std::cout << AMARILLO << "[AVISO] " << mensaje << RESET << std::endl;
}

void informacion(const std::string& mensaje) {
    std::cout << MAGENTA << mensaje << RESET << std::endl;
}

// ============================================================================
//  Utilidades de entrada VALIDADA
//
//  Se usa std::getline (y no "cin >>") para leer SIEMPRE una linea completa.
//  Si se usara "cin >>", al escribir letras en un numero el flujo quedaria en
//  estado de error, el bucle se dispararia y el programa pareceria "colgarse".
//  Con getline + stoi dentro de try/catch el programa no se cierra nunca.
// ============================================================================

// Quita espacios y saltos de linea de los extremos.
std::string recortar(const std::string& texto) {
    size_t inicio = texto.find_first_not_of(" \t\r\n");
    if (inicio == std::string::npos) {
        return "";  // Solo habia espacios en blanco.
    }
    size_t fin = texto.find_last_not_of(" \t\r\n");
    return texto.substr(inicio, fin - inicio + 1);
}

// Muestra una etiqueta y devuelve la linea escrita por el usuario.
std::string leerLinea(const std::string& etiqueta) {
    std::cout << CIAN << etiqueta << RESET;
    std::string linea;
    std::getline(std::cin, linea);
    return linea;
}

// Lee un entero validado. Repite hasta que el usuario escriba un numero.
int leerEntero(const std::string& etiqueta) {
    while (true) {
        std::string texto = recortar(leerLinea(etiqueta));
        try {
            size_t posicion = 0;
            int valor = std::stoi(texto, &posicion);
            // Si sobra texto (por ejemplo "12abc") tambien es invalido.
            if (posicion != texto.size()) {
                throw std::invalid_argument("texto sobrante");
            }
            return valor;
        } catch (...) {
            error("Debe ingresar un numero entero valido.");
        }
    }
}

// Lee un entero y ademas verifica que este dentro de un rango [minimo, maximo].
int leerEnteroEnRango(const std::string& etiqueta, int minimo, int maximo) {
    while (true) {
        int valor = leerEntero(etiqueta);
        if (valor >= minimo && valor <= maximo) {
            return valor;
        }
        error("El valor debe estar entre " + std::to_string(minimo) +
              " y " + std::to_string(maximo) + ".");
    }
}

// Lee un texto que no puede quedar vacio.
std::string leerTexto(const std::string& etiqueta) {
    while (true) {
        std::string texto = recortar(leerLinea(etiqueta));
        if (!texto.empty()) {
            return texto;
        }
        error("El campo no puede quedar vacio.");
    }
}

// Lee una respuesta de si/no.
bool leerBooleano(const std::string& etiqueta) {
    while (true) {
        std::string texto = recortar(leerLinea(etiqueta + " (s/n): "));
        if (texto == "s" || texto == "S" || texto == "si" ||
            texto == "Si" || texto == "SI") {
            return true;
        }
        if (texto == "n" || texto == "N" || texto == "no" ||
            texto == "No" || texto == "NO") {
            return false;
        }
        error("Responda 's' para si o 'n' para no.");
    }
}

// Pausa hasta que el usuario presione ENTER.
void pausar() {
    std::cout << AMARILLO << "\nPresione ENTER para continuar..." << RESET;
    std::string linea;
    std::getline(std::cin, linea);
}

// Limpia la pantalla usando una secuencia ANSI.
void limpiarPantalla() {
    std::cout << "\033[2J\033[H";
}

// ============================================================================
//  Funciones auxiliares de datos
// ============================================================================

// Anio actual del sistema (para el filtro de antiguedad).
int anioActual() {
    std::time_t tiempo = std::time(nullptr);
    std::tm* ahora = std::localtime(&tiempo);
    return ahora->tm_year + 1900;  // tm_year cuenta desde 1900.
}

// Busca un grupo por id. Devuelve el PUNTERO o nullptr si no existe.
Grupo* buscarGrupo(int id) {
    for (Grupo* grupo : grupos) {
        if (grupo->id == id) {
            return grupo;
        }
    }
    return nullptr;
}

// Busca un producto por id en TODOS los grupos. Devuelve el nodo o nullptr.
ListaProductos::Nodo* buscarProductoGlobal(int id) {
    for (Grupo* grupo : grupos) {
        ListaProductos::Nodo* nodo = grupo->productos.buscar(id);
        if (nodo != nullptr) {
            return nodo;
        }
    }
    return nullptr;
}

// Libera la memoria de todos los grupos.
void liberarGrupos() {
    for (Grupo* grupo : grupos) {
        delete grupo;  // El destructor del Grupo libera sus dos listas.
    }
    grupos.clear();
}

// Totales para las estadisticas.
int contarTotalInvestigadores() {
    int total = 0;
    for (Grupo* grupo : grupos) {
        total += grupo->integrantes.contar();
    }
    return total;
}

int contarTotalProductos() {
    int total = 0;
    for (Grupo* grupo : grupos) {
        total += grupo->productos.contar();
    }
    return total;
}

// Imprime una linea separadora de guiones.
void imprimirLinea(int ancho) {
    std::cout << CIAN << std::string(ancho, '-') << RESET << std::endl;
}

// ============================================================================
//  MOSTRAR (parte de "leer" del CRUD)
// ============================================================================

void mostrarGrupos() {
    if (grupos.empty()) {
        aviso("No hay grupos registrados.");
        return;
    }

    std::cout << CIAN << "\n=== LISTA DE GRUPOS ===" << RESET << std::endl;
    imprimirLinea(78);
    std::cout << std::left
              << std::setw(6)  << "ID"
              << std::setw(24) << "NOMBRE"
              << std::setw(26) << "PLAN"
              << std::right
              << std::setw(9)  << "INTEGR."
              << std::setw(9)  << "PROD."
              << std::endl;
    imprimirLinea(78);

    for (Grupo* grupo : grupos) {
        std::cout << std::left
                  << std::setw(6)  << grupo->id
                  << std::setw(24) << grupo->nombre
                  << std::setw(26) << grupo->plan
                  << std::right
                  << std::setw(9)  << grupo->integrantes.contar()
                  << std::setw(9)  << grupo->productos.contar()
                  << std::endl;
    }
    imprimirLinea(78);
}

void mostrarInvestigadoresDeGrupo(const Grupo* grupo) {
    if (grupo->integrantes.vacia()) {
        aviso("El grupo '" + grupo->nombre + "' no tiene investigadores.");
        return;
    }

    std::cout << CIAN << "\n=== INVESTIGADORES DEL GRUPO " << grupo->id
              << " (" << grupo->nombre << ") ===" << RESET << std::endl;
    imprimirLinea(80);
    std::cout << std::left
              << std::setw(6)  << "ID"
              << std::setw(24) << "NOMBRE"
              << std::setw(30) << "AREA DE CONOCIMIENTO"
              << std::setw(16) << "CATEGORIA"
              << std::endl;
    imprimirLinea(80);

    // Recorrido de la lista enlazada con un puntero auxiliar.
    for (ListaInvestigadores::Nodo* nodo = grupo->integrantes.primero();
         nodo != nullptr; nodo = nodo->siguiente) {
        const Investigador& inv = nodo->dato;
        std::cout << std::left
                  << std::setw(6)  << inv.id
                  << std::setw(24) << inv.nombre
                  << std::setw(30) << inv.areaConocimiento
                  << std::setw(16) << inv.categoria
                  << std::endl;
    }
    imprimirLinea(80);
}

void mostrarProductosDeGrupo(const Grupo* grupo) {
    if (grupo->productos.vacia()) {
        aviso("El grupo '" + grupo->nombre + "' no tiene productos.");
        return;
    }

    std::cout << CIAN << "\n=== PRODUCTOS DEL GRUPO " << grupo->id
              << " (" << grupo->nombre << ") ===" << RESET << std::endl;
    imprimirLinea(82);
    std::cout << std::left
              << std::setw(6)  << "ID"
              << std::setw(30) << "TITULO"
              << std::right << std::setw(6) << "ANIO" << std::left << "  "
              << std::setw(18) << "CATEGORIA"
              << std::setw(10) << "VALIDADO"
              << std::endl;
    imprimirLinea(82);

    for (ListaProductos::Nodo* nodo = grupo->productos.primero();
         nodo != nullptr; nodo = nodo->siguiente) {
        const Producto& prod = nodo->dato;
        std::cout << std::left
                  << std::setw(6)  << prod.id
                  << std::setw(30) << prod.titulo
                  << std::right << std::setw(6) << prod.anio << std::left << "  "
                  << std::setw(18) << prod.categoria
                  << std::setw(10) << (prod.validado ? "Si" : "No")
                  << std::endl;
    }
    imprimirLinea(82);
}

// Pide un grupo por id y lo devuelve (o nullptr si no existe).
// Se usa antes de operar sobre investigadores/productos.
Grupo* pedirGrupo() {
    if (grupos.empty()) {
        error("No hay grupos registrados. Cree un grupo primero.");
        return nullptr;
    }
    mostrarGrupos();
    int id = leerEntero("Ingrese el ID del grupo: ");
    Grupo* grupo = buscarGrupo(id);
    if (grupo == nullptr) {
        error("No existe un grupo con el ID " + std::to_string(id) + ".");
    }
    return grupo;
}

// ============================================================================
//  CRUD DE GRUPOS
// ============================================================================

void agregarGrupo() {
    std::cout << CIAN << "\n--- AGREGAR GRUPO ---" << RESET << std::endl;

    int id = leerEntero("ID del grupo: ");
    if (buscarGrupo(id) != nullptr) {
        error("Ya existe un grupo con ese ID.");
        return;
    }
    std::string nombre = leerTexto("Nombre del grupo: ");
    std::string plan = leerTexto("Plan de estudios: ");

    grupos.push_back(new Grupo(id, nombre, plan));  // Se crea en el heap.
    historial.insertar("Grupo agregado (ID " + std::to_string(id) + "): " + nombre);
    exito("Grupo agregado correctamente.");
}

void eliminarGrupo() {
    std::cout << CIAN << "\n--- ELIMINAR GRUPO ---" << RESET << std::endl;
    if (grupos.empty()) {
        aviso("No hay grupos para eliminar.");
        return;
    }

    int id = leerEntero("ID del grupo a eliminar: ");
    for (size_t i = 0; i < grupos.size(); ++i) {
        if (grupos[i]->id == id) {
            if (!leerBooleano("Confirma eliminar el grupo y TODOS sus datos?")) {
                aviso("Operacion cancelada.");
                return;
            }
            std::string nombre = grupos[i]->nombre;
            delete grupos[i];                 // Libera el grupo y sus listas.
            grupos.erase(grupos.begin() + i); // Lo quita del vector.
            historial.insertar("Grupo eliminado (ID " + std::to_string(id) + "): " + nombre);
            exito("Grupo eliminado correctamente.");
            return;
        }
    }
    error("No existe un grupo con ese ID.");
}

void modificarGrupo() {
    std::cout << CIAN << "\n--- MODIFICAR GRUPO ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    std::cout << "1) Nombre\n2) Plan\n3) Ambos\n";
    int opcion = leerEnteroEnRango("Opcion a modificar: ", 1, 3);

    if (opcion == 1 || opcion == 3) {
        grupo->nombre = leerTexto("Nuevo nombre: ");
    }
    if (opcion == 2 || opcion == 3) {
        grupo->plan = leerTexto("Nuevo plan: ");
    }
    historial.insertar("Grupo modificado (ID " + std::to_string(grupo->id) + ")");
    exito("Grupo modificado correctamente.");
}

// ============================================================================
//  CRUD DE INVESTIGADORES
// ============================================================================

void agregarInvestigador() {
    std::cout << CIAN << "\n--- AGREGAR INVESTIGADOR ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    int id = leerEntero("ID del investigador: ");
    if (grupo->integrantes.buscar(id) != nullptr) {
        error("Ese grupo ya tiene un investigador con ese ID.");
        return;
    }
    std::string nombre = leerTexto("Nombre: ");
    std::string area = leerTexto("Area de conocimiento: ");
    std::string categoria = leerTexto("Categoria: ");

    grupo->integrantes.insertar({id, nombre, area, categoria});
    historial.insertar("Investigador agregado al grupo " + std::to_string(grupo->id) +
                       ": " + nombre);
    exito("Investigador agregado correctamente.");
}

void eliminarInvestigador() {
    std::cout << CIAN << "\n--- ELIMINAR INVESTIGADOR ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    int id = leerEntero("ID del investigador a eliminar: ");
    if (grupo->integrantes.eliminar(id)) {
        historial.insertar("Investigador eliminado (ID " + std::to_string(id) +
                           ") del grupo " + std::to_string(grupo->id));
        exito("Investigador eliminado correctamente.");
    } else {
        error("No existe un investigador con ese ID en el grupo.");
    }
}

void modificarInvestigador() {
    std::cout << CIAN << "\n--- MODIFICAR INVESTIGADOR ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    int id = leerEntero("ID del investigador a modificar: ");
    ListaInvestigadores::Nodo* nodo = grupo->integrantes.buscar(id);
    if (nodo == nullptr) {
        error("No existe un investigador con ese ID en el grupo.");
        return;
    }

    std::cout << "1) Nombre\n2) Area de conocimiento\n3) Categoria\n4) Todos\n";
    int opcion = leerEnteroEnRango("Opcion a modificar: ", 1, 4);

    Investigador& inv = nodo->dato;  // Referencia: modifica el dato del nodo.
    if (opcion == 1 || opcion == 4) {
        inv.nombre = leerTexto("Nuevo nombre: ");
    }
    if (opcion == 2 || opcion == 4) {
        inv.areaConocimiento = leerTexto("Nueva area de conocimiento: ");
    }
    if (opcion == 3 || opcion == 4) {
        inv.categoria = leerTexto("Nueva categoria: ");
    }
    historial.insertar("Investigador modificado (ID " + std::to_string(id) +
                       ") del grupo " + std::to_string(grupo->id));
    exito("Investigador modificado correctamente.");
}

void mostrarInvestigadores() {
    std::cout << CIAN << "\n--- MOSTRAR INVESTIGADORES ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }
    mostrarInvestigadoresDeGrupo(grupo);
}

// ============================================================================
//  CRUD DE PRODUCTOS
// ============================================================================

void agregarProducto() {
    std::cout << CIAN << "\n--- AGREGAR PRODUCTO ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    int id = leerEntero("ID del producto: ");
    if (grupo->productos.buscar(id) != nullptr) {
        error("Ese grupo ya tiene un producto con ese ID.");
        return;
    }
    std::string titulo = leerTexto("Titulo: ");
    int anio = leerEnteroEnRango("Anio de publicacion: ", 1900, anioActual() + 1);
    std::string categoria = leerTexto("Categoria: ");
    bool validado = leerBooleano("Esta validado?");

    grupo->productos.insertar({id, titulo, anio, categoria, validado});
    historial.insertar("Producto agregado al grupo " + std::to_string(grupo->id) +
                       ": " + titulo);
    exito("Producto agregado correctamente.");
}

void eliminarProducto() {
    std::cout << CIAN << "\n--- ELIMINAR PRODUCTO ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    int id = leerEntero("ID del producto a eliminar: ");
    if (grupo->productos.eliminar(id)) {
        historial.insertar("Producto eliminado (ID " + std::to_string(id) +
                           ") del grupo " + std::to_string(grupo->id));
        exito("Producto eliminado correctamente.");
    } else {
        error("No existe un producto con ese ID en el grupo.");
    }
}

void modificarProducto() {
    std::cout << CIAN << "\n--- MODIFICAR PRODUCTO ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }

    int id = leerEntero("ID del producto a modificar: ");
    ListaProductos::Nodo* nodo = grupo->productos.buscar(id);
    if (nodo == nullptr) {
        error("No existe un producto con ese ID en el grupo.");
        return;
    }

    std::cout << "1) Titulo\n2) Anio\n3) Categoria\n4) Validado\n5) Todos\n";
    int opcion = leerEnteroEnRango("Opcion a modificar: ", 1, 5);

    Producto& prod = nodo->dato;  // Referencia al dato del nodo.
    if (opcion == 1 || opcion == 5) {
        prod.titulo = leerTexto("Nuevo titulo: ");
    }
    if (opcion == 2 || opcion == 5) {
        prod.anio = leerEnteroEnRango("Nuevo anio: ", 1900, anioActual() + 1);
    }
    if (opcion == 3 || opcion == 5) {
        prod.categoria = leerTexto("Nueva categoria: ");
    }
    if (opcion == 4 || opcion == 5) {
        prod.validado = leerBooleano("Esta validado?");
    }
    historial.insertar("Producto modificado (ID " + std::to_string(id) +
                       ") del grupo " + std::to_string(grupo->id));
    exito("Producto modificado correctamente.");
}

void mostrarProductos() {
    std::cout << CIAN << "\n--- MOSTRAR PRODUCTOS ---" << RESET << std::endl;
    Grupo* grupo = pedirGrupo();
    if (grupo == nullptr) {
        return;
    }
    mostrarProductosDeGrupo(grupo);
}

// ============================================================================
//  FILTRO DE PRODUCTOS POR ANIO
//  Muestra los productos publicados en los ultimos N anios (por ejemplo 2 o 5).
// ============================================================================
void filtrarProductosPorAnio() {
    std::cout << CIAN << "\n--- FILTRAR PRODUCTOS POR ANIO ---" << RESET << std::endl;

    if (grupos.empty()) {
        aviso("No hay grupos registrados.");
        return;
    }

    std::cout << "Ejemplos: 2 = ultimos 2 anios, 5 = ultimos 5 anios.\n";
    int cantidadAnios = leerEnteroEnRango("Cuantos anios hacia atras (1-100)? ", 1, 100);
    int anioLimite = anioActual() - cantidadAnios;  // Anio minimo incluido.

    std::cout << CIAN << "\nProductos desde el anio " << anioLimite
              << " en adelante (ultimos " << cantidadAnios << " anios):" << RESET << std::endl;
    imprimirLinea(88);
    std::cout << std::left
              << std::setw(8)  << "GRUPO"
              << std::setw(6)  << "ID"
              << std::setw(30) << "TITULO"
              << std::right << std::setw(6) << "ANIO" << std::left << "  "
              << std::setw(18) << "CATEGORIA"
              << std::setw(10) << "VALIDADO"
              << std::endl;
    imprimirLinea(88);

    int encontrados = 0;
    // Recorremos todos los grupos y, dentro de cada uno, su lista de productos.
    for (Grupo* grupo : grupos) {
        for (ListaProductos::Nodo* nodo = grupo->productos.primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            const Producto& prod = nodo->dato;
            if (prod.anio >= anioLimite) {  // Filtro por anio.
                std::cout << std::left
                          << std::setw(8)  << grupo->id
                          << std::setw(6)  << prod.id
                          << std::setw(30) << prod.titulo
                          << std::right << std::setw(6) << prod.anio << std::left << "  "
                          << std::setw(18) << prod.categoria
                          << std::setw(10) << (prod.validado ? "Si" : "No")
                          << std::endl;
                ++encontrados;
            }
        }
    }
    imprimirLinea(88);

    if (encontrados == 0) {
        aviso("No se encontraron productos en ese rango de anios.");
    } else {
        exito("Total de productos encontrados: " + std::to_string(encontrados));
    }
}

// ============================================================================
//  ESTADISTICAS (tablas alineadas con <iomanip> y setw)
// ============================================================================
void mostrarEstadisticas() {
    std::cout << CIAN << "\n=== ESTADISTICAS ===" << RESET << std::endl;

    if (grupos.empty()) {
        aviso("No hay datos para calcular estadisticas.");
        return;
    }

    int totalInvestigadores = contarTotalInvestigadores();
    int totalProductos = contarTotalProductos();
    int productosValidados = 0;
    for (Grupo* grupo : grupos) {
        for (ListaProductos::Nodo* nodo = grupo->productos.primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            if (nodo->dato.validado) {
                ++productosValidados;
            }
        }
    }

    // --- Tabla 1: resumen general ---
    std::cout << "\n" << AMARILLO << "Resumen general" << RESET << std::endl;
    imprimirLinea(46);
    std::cout << std::left << std::setw(32) << "METRICA"
              << std::right << std::setw(14) << "VALOR" << std::endl;
    imprimirLinea(46);
    std::cout << std::left << std::setw(32) << "Grupos registrados"
              << std::right << std::setw(14) << grupos.size() << std::endl;
    std::cout << std::left << std::setw(32) << "Investigadores"
              << std::right << std::setw(14) << totalInvestigadores << std::endl;
    std::cout << std::left << std::setw(32) << "Productos"
              << std::right << std::setw(14) << totalProductos << std::endl;
    std::cout << std::left << std::setw(32) << "Productos validados"
              << std::right << std::setw(14) << productosValidados << std::endl;
    std::cout << std::left << std::setw(32) << "Productos sin validar"
              << std::right << std::setw(14) << (totalProductos - productosValidados)
              << std::endl;
    imprimirLinea(46);

    // --- Tabla 2: productos por grupo ---
    std::cout << "\n" << AMARILLO << "Productos por grupo" << RESET << std::endl;
    imprimirLinea(46);
    std::cout << std::left << std::setw(32) << "GRUPO"
              << std::right << std::setw(14) << "PRODUCTOS" << std::endl;
    imprimirLinea(46);
    for (Grupo* grupo : grupos) {
        std::cout << std::left << std::setw(32) << (grupo->nombre + " (" +
                     std::to_string(grupo->id) + ")")
                  << std::right << std::setw(14) << grupo->productos.contar()
                  << std::endl;
    }
    imprimirLinea(46);

    // --- Tabla 3: investigadores por area de conocimiento ---
    // std::map ordena las areas alfabeticamente, lo que mejora la lectura.
    std::map<std::string, int> porArea;
    for (Grupo* grupo : grupos) {
        for (ListaInvestigadores::Nodo* nodo = grupo->integrantes.primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            porArea[nodo->dato.areaConocimiento] += 1;
        }
    }

    std::cout << "\n" << AMARILLO << "Investigadores por area" << RESET << std::endl;
    imprimirLinea(54);
    std::cout << std::left << std::setw(38) << "AREA DE CONOCIMIENTO"
              << std::right << std::setw(16) << "INVESTIGADORES" << std::endl;
    imprimirLinea(54);
    if (porArea.empty()) {
        std::cout << std::left << std::setw(38) << "(sin investigadores)"
                  << std::right << std::setw(16) << 0 << std::endl;
    } else {
        for (const auto& par : porArea) {
            std::cout << std::left << std::setw(38) << par.first
                      << std::right << std::setw(16) << par.second << std::endl;
        }
    }
    imprimirLinea(54);
}

// ============================================================================
//  HISTORIAL DE CAMBIOS (Pila) y COLA DE VALIDACION (Cola)
// ============================================================================

void verHistorial() {
    std::cout << CIAN << "\n--- HISTORIAL DE CAMBIOS (Pila LIFO) ---" << RESET << std::endl;
    if (historial.vacia()) {
        aviso("Todavia no hay cambios registrados.");
        return;
    }
    // mostrar() de la Pila imprime del cambio mas reciente al mas antiguo.
    historial.mostrar();
}

void procesarColaValidacion() {
    std::cout << CIAN << "\n--- COLA DE VALIDACION DE PRODUCTOS (Cola FIFO) ---"
              << RESET << std::endl;

    // Se llena la cola con los IDs de los productos NO validados, en el orden
    // en que aparecen (grupo por grupo).
    Cola cola;
    for (Grupo* grupo : grupos) {
        for (ListaProductos::Nodo* nodo = grupo->productos.primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            if (!nodo->dato.validado) {
                cola.insertar(nodo->dato.id);
            }
        }
    }

    if (cola.vacia()) {
        aviso("No hay productos pendientes de validacion.");
        return;
    }

    // Se atienden uno por uno respetando el orden FIFO.
    while (!cola.vacia()) {
        const int* idFrente = cola.frente();  // Puntero al id del frente.
        if (idFrente == nullptr) {
            break;
        }
        int id = *idFrente;
        ListaProductos::Nodo* nodo = buscarProductoGlobal(id);

        if (nodo == nullptr) {
            cola.eliminar();
            continue;
        }

        std::cout << "\nProducto al frente de la cola: id " << id
                  << " - " << nodo->dato.titulo
                  << " (" << nodo->dato.anio << ")" << std::endl;
        if (leerBooleano("Validar este producto?")) {
            nodo->dato.validado = true;
            historial.insertar("Producto validado (ID " + std::to_string(id) + ")");
            exito("Producto validado.");
        } else {
            aviso("Producto dejado sin validar.");
        }
        cola.eliminar();  // Se saca el producto ya atendido del frente.
    }
    exito("Cola de validacion atendida.");
}

// ============================================================================
//  PERSISTENCIA EN datos.csv
//
//  Formato (una linea por registro, campos separados por comas):
//      GRUPO,idGrupo,nombre,plan
//      INVESTIGADOR,idGrupo,id,nombre,area,categoria
//      PRODUCTO,idGrupo,id,titulo,anio,categoria,validado
//  Se escribe primero el grupo y despues sus integrantes/productos para que
//  al cargar el grupo ya exista.
// ============================================================================

// Evita que una coma dentro de un texto rompa el formato CSV.
std::string sanitizarCSV(const std::string& texto) {
    std::string resultado = texto;
    for (char& c : resultado) {
        if (c == ',') {
            c = ';';
        }
    }
    return resultado;
}

void guardarCSV() {
    std::ofstream archivo(ARCHIVO_DATOS);  // ofstream crea/sobrescribe.
    if (!archivo.is_open()) {
        error("No se pudo abrir " + ARCHIVO_DATOS + " para guardar.");
        return;
    }

    for (Grupo* grupo : grupos) {
        archivo << "GRUPO," << grupo->id << ","
                << sanitizarCSV(grupo->nombre) << ","
                << sanitizarCSV(grupo->plan) << "\n";

        for (ListaInvestigadores::Nodo* nodo = grupo->integrantes.primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            const Investigador& inv = nodo->dato;
            archivo << "INVESTIGADOR," << grupo->id << "," << inv.id << ","
                    << sanitizarCSV(inv.nombre) << ","
                    << sanitizarCSV(inv.areaConocimiento) << ","
                    << sanitizarCSV(inv.categoria) << "\n";
        }

        for (ListaProductos::Nodo* nodo = grupo->productos.primero();
             nodo != nullptr; nodo = nodo->siguiente) {
            const Producto& prod = nodo->dato;
            archivo << "PRODUCTO," << grupo->id << "," << prod.id << ","
                    << sanitizarCSV(prod.titulo) << "," << prod.anio << ","
                    << sanitizarCSV(prod.categoria) << ","
                    << (prod.validado ? 1 : 0) << "\n";
        }
    }

    archivo.close();
    historial.insertar("Datos guardados en " + ARCHIVO_DATOS);
    exito("Datos guardados en " + ARCHIVO_DATOS + ".");
}

// Divide una linea por el separador indicado (por defecto la coma).
std::vector<std::string> dividir(const std::string& linea, char separador = ',') {
    std::vector<std::string> partes;
    std::stringstream flujo(linea);
    std::string parte;
    while (std::getline(flujo, parte, separador)) {
        partes.push_back(parte);
    }
    return partes;
}

void cargarCSV() {
    std::ifstream archivo(ARCHIVO_DATOS);  // ifstream abre para lectura.
    if (!archivo.is_open()) {
        aviso("No se encontro " + ARCHIVO_DATOS +
              "; el programa inicia con datos vacios.");
        return;
    }

    liberarGrupos();  // Si habia datos en memoria, se descartan.

    std::string linea;
    int contadorGrupos = 0;
    int contadorInvestigadores = 0;
    int contadorProductos = 0;

    while (std::getline(archivo, linea)) {
        if (recortar(linea).empty()) {
            continue;  // Ignora lineas en blanco.
        }
        std::vector<std::string> partes = dividir(linea);
        if (partes.empty()) {
            continue;
        }

        try {
            if (partes[0] == "GRUPO" && partes.size() >= 4) {
                grupos.push_back(new Grupo(std::stoi(partes[1]), partes[2], partes[3]));
                ++contadorGrupos;
            } else if (partes[0] == "INVESTIGADOR" && partes.size() >= 6) {
                Grupo* grupo = buscarGrupo(std::stoi(partes[1]));
                if (grupo != nullptr) {
                    grupo->integrantes.insertar({std::stoi(partes[2]), partes[3],
                                                 partes[4], partes[5]});
                    ++contadorInvestigadores;
                }
            } else if (partes[0] == "PRODUCTO" && partes.size() >= 7) {
                Grupo* grupo = buscarGrupo(std::stoi(partes[1]));
                if (grupo != nullptr) {
                    grupo->productos.insertar({std::stoi(partes[2]), partes[3],
                                               std::stoi(partes[4]), partes[5],
                                               partes[6] == "1"});
                    ++contadorProductos;
                }
            }
        } catch (...) {
            // Si una linea esta corrupta se ignora en lugar de cerrar el
            // programa.
            continue;
        }
    }

    archivo.close();
    exito("Datos cargados: " + std::to_string(contadorGrupos) + " grupos, " +
          std::to_string(contadorInvestigadores) + " investigadores, " +
          std::to_string(contadorProductos) + " productos.");
    historial.insertar("Datos cargados desde " + ARCHIVO_DATOS);
}

// ============================================================================
//  TITULO Y MENU
// ============================================================================

void mostrarTitulo() {
    limpiarPantalla();
    for (const std::string& fila : BANNER) {
        std::cout << CIAN << fila << RESET << std::endl;
    }
    std::cout << MAGENTA
              << "                             Sistema de Gestion de Investigacion"
              << RESET << std::endl;
    std::cout << std::endl;
}

void mostrarMenu() {
    std::cout << CIAN << "==============================================" << RESET << std::endl;
    std::cout << CIAN << "                  MENU                        " << RESET << std::endl;
    std::cout << CIAN << "==============================================" << RESET << std::endl;
    std::cout << " 1) Agregar grupo         10) Agregar producto\n";
    std::cout << " 2) Eliminar grupo        11) Eliminar producto\n";
    std::cout << " 3) Modificar grupo       12) Modificar producto\n";
    std::cout << " 4) Mostrar grupos        13) Mostrar productos\n";
    std::cout << " 5) Agregar investigador  14) Filtrar productos por anio\n";
    std::cout << " 6) Eliminar investigador 15) Estadisticas\n";
    std::cout << " 7) Modificar investigador 16) Ver historial\n";
    std::cout << " 8) Mostrar investigadores 17) Cola de validacion\n";
    std::cout << " 9) Guardar datos         18) Cargar datos\n";
    std::cout << "                          19) Salir\n";
    std::cout << CIAN << "==============================================" << RESET << std::endl;
}

// ============================================================================
//  PROGRAMA PRINCIPAL
// ============================================================================
int main() {
    habilitarColoresANSI();
    cargarCSV();  // Carga los datos guardados, si existen.

    bool salir = false;
    while (!salir) {
        mostrarTitulo();
        mostrarMenu();

        int opcion = leerEnteroEnRango("Seleccione una opcion: ", 1, 19);

        switch (opcion) {
            case 1:  agregarGrupo();          pausar(); break;
            case 2:  eliminarGrupo();         pausar(); break;
            case 3:  modificarGrupo();        pausar(); break;
            case 4:  mostrarGrupos();         pausar(); break;
            case 5:  agregarInvestigador();   pausar(); break;
            case 6:  eliminarInvestigador();  pausar(); break;
            case 7:  modificarInvestigador(); pausar(); break;
            case 8:  mostrarInvestigadores(); pausar(); break;
            case 9:  guardarCSV();            pausar(); break;
            case 10: agregarProducto();       pausar(); break;
            case 11: eliminarProducto();      pausar(); break;
            case 12: modificarProducto();     pausar(); break;
            case 13: mostrarProductos();      pausar(); break;
            case 14: filtrarProductosPorAnio(); pausar(); break;
            case 15: mostrarEstadisticas();   pausar(); break;
            case 16: verHistorial();          pausar(); break;
            case 17: procesarColaValidacion(); pausar(); break;
            case 18: cargarCSV();             pausar(); break;
            case 19:
                if (leerBooleano("Guardar los datos antes de salir?")) {
                    guardarCSV();
                }
                salir = true;
                break;
            default:
                error("Opcion invalida.");
                break;
        }
    }

    liberarGrupos();  // Al terminar, se libera toda la memoria reservada.
    limpiarPantalla();
    informacion("Gracias por usar el sistema. Hasta pronto!");
    return 0;
}
