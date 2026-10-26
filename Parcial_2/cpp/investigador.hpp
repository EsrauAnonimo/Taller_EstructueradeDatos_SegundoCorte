#pragma once

#include <iostream>
#include <string>

template <typename T>
class ListaEnlazada;
struct Producto;

// ============================================================================
//  Estructura Investigador
// ============================================================================
struct Investigador {
    int id;
    std::string nombre;
    std::string areaConocimiento;
    std::string categoria;
    bool activo = true;
    ListaEnlazada<Producto>* misProductosPtr = nullptr;
};

// Función que imprime los datos de un investigador.
// "inline" permite definir la función en el encabezado sin provocar
// errores de enlace si varios .cpp la incluyen.
inline void imprimirInvestigador(const Investigador& investigador) {
    std::cout << "ID: " << investigador.id << std::endl;
    std::cout << "Nombre: " << investigador.nombre << std::endl;
    std::cout << "Area de conocimiento: " << investigador.areaConocimiento << std::endl;
    std::cout << "Categoria: " << investigador.categoria << std::endl;
    std::cout << "Activo: " << (investigador.activo ? "Si" : "No") << std::endl;
}
