# -*- coding: utf-8 -*-
"""Punto de entrada de la aplicación por consola PEA-i."""

import sys
from pathlib import Path

# Permitir ejecutar main.py tanto desde la raíz como desde la subcarpeta python
BASE_DIR = Path(__file__).resolve().parent
PYTHON_DIR = BASE_DIR / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from persistencia.persistencia_json import PersistenciaJSON
from modelos.multilista import Multilist
from crud.crud_grupos import GrupoCRUD
from crud.crud_investigadores import InvestigadorCRUD
from crud.crud_productos import ProductoCRUD
from entidades.grupo import Grupo
from entidades.investigador import Investigador
from entidades.producto import Producto


def main():
    """Punto de entrada de la aplicación de consola."""
    persistencia = PersistenciaJSON()
    multilist = Multilist()

    cargar = input("¿Desea cargar los datos guardados? (s/n): ").strip().lower()
    if cargar == 's':
        try:
            data = persistencia.load()
            multilist = PersistenciaJSON.to_multilist(data)
            print("Datos cargados correctamente.")
        except Exception as e:
            print("Error al cargar datos. Iniciando con estructura vacía.")

    grupo_crud = GrupoCRUD(multilist)
    investigador_crud = InvestigadorCRUD(multilist)
    producto_crud = ProductoCRUD(multilist)

    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Gestión de Grupos")
        print("2. Gestión de Investigadores")
        print("3. Gestión de Productos")
        print("4. Filtros por año")
        print("5. Ver estadísticas resumidas")
        print("6. Guardar datos")
        print("7. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            menu_grupos(grupo_crud, investigador_crud, producto_crud)
        elif opcion == '2':
            menu_investigadores(grupo_crud, investigador_crud, producto_crud)
        elif opcion == '3':
            menu_productos(grupo_crud, investigador_crud, producto_crud)
        elif opcion == '4':
            menu_filtros_ano(producto_crud)
        elif opcion == '5':
            menu_estadisticas(grupo_crud, investigador_crud, producto_crud)
        elif opcion == '6':
            guardar_datos(persistencia, multilist)
        elif opcion == '7':
            guardar = input("¿Desea guardar antes de salir? (s/n): ").strip().lower()
            if guardar == 's':
                guardar_datos(persistencia, multilist)
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


def guardar_datos(persistencia, multilist):
    """Guarda los datos en el archivo JSON."""
    try:
        persistencia.save(multilist)
        print("Datos guardados correctamente.")
    except Exception as e:
        print("Error al guardar los datos.")


def menu_grupos(grupo_crud, investigador_crud, producto_crud):
    """Menú de gestión de grupos."""
    while True:
        print("\n=== GESTIÓN DE GRUPOS ===")
        print("1. Crear grupo")
        print("2. Listar grupos")
        print("3. Buscar grupo por código")
        print("4. Modificar grupo")
        print("5. Desactivar grupo")
        print("6. Activar grupo")
        print("7. Eliminar grupo")
        print("8. Volver")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            try:
                gid = int(input("ID: "))
            except ValueError:
                print("ID inválido.")
                continue
            codigo = input("Código Gruplac: ").strip()
            nombre = input("Nombre: ").strip()
            categoria = input("Categoría: ").strip()
            lider = input("Líder: ").strip()
            fecha = input("Fecha creación (YYYY-MM-DD): ").strip()
            grupo = Grupo(id=gid, codigo_gruplac=codigo, nombre=nombre, categoria=categoria, lider=lider, fecha_creacion=fecha)
            if grupo_crud.create(grupo):
                print("Grupo creado.")
            else:
                print("Error al crear grupo (código duplicado).")
        elif opcion == '2':
            for g in grupo_crud.list_all():
                print(g)
        elif opcion == '3':
            codigo = input("Código: ").strip()
            g = grupo_crud.get_by_code(codigo)
            print(g if g else "No encontrado.")
        elif opcion == '4':
            try:
                gid = int(input("ID del grupo: "))
            except ValueError:
                print("ID inválido.")
                continue
            campos = {}
            nombre = input("Nuevo nombre (enter para omitir): ").strip()
            if nombre:
                campos['nombre'] = nombre
            categoria = input("Nueva categoría (enter para omitir): ").strip()
            if categoria:
                campos['categoria'] = categoria
            lider = input("Nuevo líder (enter para omitir): ").strip()
            if lider:
                campos['lider'] = lider
            if grupo_crud.update(gid, **campos):
                print("Actualizado.")
            else:
                print("No encontrado.")
        elif opcion == '5':
            try:
                gid = int(input("ID: "))
            except ValueError:
                print("ID inválido.")
                continue
            if grupo_crud.deactivate(gid):
                print("Desactivado.")
            else:
                print("No encontrado.")
        elif opcion == '6':
            try:
                gid = int(input("ID: "))
            except ValueError:
                print("ID inválido.")
                continue
            if grupo_crud.activate(gid):
                print("Activado.")
            else:
                print("No encontrado.")
        elif opcion == '7':
            try:
                gid = int(input("ID: "))
            except ValueError:
                print("ID inválido.")
                continue
            if grupo_crud.delete(gid):
                print("Eliminado.")
            else:
                print("No encontrado.")
        elif opcion == '8':
            break
        else:
            print("Opción no válida.")


def menu_investigadores(grupo_crud, investigador_crud, producto_crud):
    """Menú de gestión de investigadores."""
    while True:
        print("\n=== GESTIÓN DE INVESTIGADORES ===")
        print("1. Crear investigador")
        print("2. Listar todos")
        print("3. Listar por grupo")
        print("4. Buscar por cédula")
        print("5. Modificar investigador")
        print("6. Desactivar / Activar / Eliminar")
        print("7. Volver")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            try:
                iid = int(input("ID: "))
            except ValueError:
                print("ID inválido.")
                continue
            cedula = input("Cédula: ").strip()
            nombres = input("Nombres: ").strip()
            apellidos = input("Apellidos: ").strip()
            email = input("Email: ").strip()
            try:
                gid = int(input("ID Grupo: "))
            except ValueError:
                print("ID inválido.")
                continue
            inv = Investigador(id=iid, cedula=cedula, nombres=nombres, apellidos=apellidos, email=email, grupo_id=gid)
            if investigador_crud.create(inv):
                print("Investigador creado.")
            else:
                print("Error al crear investigador.")
        elif opcion == '2':
            for i in investigador_crud.list_all():
                print(i)
        elif opcion == '3':
            try:
                gid = int(input("ID Grupo: "))
            except ValueError:
                print("ID inválido.")
                continue
            for i in investigador_crud.list_by_group(gid):
                print(i)
        elif opcion == '4':
            cedula = input("Cédula: ").strip()
            i = investigador_crud.get_by_cedula(cedula)
            print(i if i else "No encontrado.")
        elif opcion == '5':
            cedula = input("Cédula: ").strip()
            campos = {}
            nombres = input("Nuevos nombres (enter para omitir): ").strip()
            if nombres:
                campos['nombres'] = nombres
            apellidos = input("Nuevos apellidos (enter para omitir): ").strip()
            if apellidos:
                campos['apellidos'] = apellidos
            email = input("Nuevo email (enter para omitir): ").strip()
            if email:
                campos['email'] = email
            if investigador_crud.update(cedula, **campos):
                print("Actualizado.")
            else:
                print("No encontrado.")
        elif opcion == '6':
            sub = input("1) Desactivar 2) Activar 3) Eliminar: ").strip()
            cedula = input("Cédula: ").strip()
            if sub == '1':
                if investigador_crud.deactivate(cedula):
                    print("Desactivado.")
                else:
                    print("No encontrado.")
            elif sub == '2':
                if investigador_crud.activate(cedula):
                    print("Activado.")
                else:
                    print("No encontrado.")
            elif sub == '3':
                if investigador_crud.delete(cedula):
                    print("Eliminado.")
                else:
                    print("No encontrado.")
            else:
                print("Opción no válida.")
        elif opcion == '7':
            break
        else:
            print("Opción no válida.")


def menu_productos(grupo_crud, investigador_crud, producto_crud):
    """Menú de gestión de productos."""
    while True:
        print("\n=== GESTIÓN DE PRODUCTOS ===")
        print("1. Crear producto")
        print("2. Listar todos")
        print("3. Listar por grupo / por investigador")
        print("4. Modificar producto")
        print("5. Desactivar / Activar / Eliminar")
        print("6. Volver")
        opcion = input("Seleccione una opción: ").strip()
        if opcion == '1':
            try:
                pid = int(input("ID: "))
            except ValueError:
                print("ID inválido.")
                continue
            titulo = input("Título: ").strip()
            tipo = input("Tipo: ").strip()
            categoria = input("Categoría: ").strip()
            validado_str = input("Validado (s/n): ").strip().lower()
            validado = validado_str == 's'
            try:
                anio = int(input("Año: "))
            except ValueError:
                print("Año inválido.")
                continue
            cedula = input("Cédula del investigador: ").strip()
            try:
                gid = int(input("ID Grupo: "))
            except ValueError:
                print("ID inválido.")
                continue
            prod = Producto(id=pid, titulo=titulo, tipo=tipo, categoria=categoria, validado=validado, anio=anio, investigador_id=1, grupo_id=gid)
            prod.cedula = cedula
            if producto_crud.create(prod):
                print("Producto creado.")
            else:
                print("Error al crear producto.")
        elif opcion == '2':
            for p in producto_crud.list_all():
                print(p)
        elif opcion == '3':
            sub = input("1) Por grupo 2) Por investigador: ").strip()
            if sub == '1':
                try:
                    gid = int(input("ID Grupo: "))
                except ValueError:
                    print("ID inválido.")
                    continue
                for p in producto_crud.list_by_group(gid):
                    print(p)
            elif sub == '2':
                cedula = input("Cédula: ").strip()
                for p in producto_crud.list_by_investigador(cedula):
                    print(p)
            else:
                print("Opción no válida.")
        elif opcion == '4':
            try:
                pid = int(input("ID producto: "))
            except ValueError:
                print("ID inválido.")
                continue
            campos = {}
            titulo = input("Nuevo título (enter para omitir): ").strip()
            if titulo:
                campos['titulo'] = titulo
            tipo = input("Nuevo tipo (enter para omitir): ").strip()
            if tipo:
                campos['tipo'] = tipo
            categoria = input("Nueva categoría (enter para omitir): ").strip()
            if categoria:
                campos['categoria'] = categoria
            validado_str = input("Validado (s/n, enter para omitir): ").strip().lower()
            if validado_str:
                campos['validado'] = validado_str == 's'
            anio_str = input("Nuevo año (enter para omitir): ").strip()
            if anio_str:
                try:
                    campos['anio'] = int(anio_str)
                except ValueError:
                    pass
            if producto_crud.update(pid, **campos):
                print("Actualizado.")
            else:
                print("No encontrado.")
        elif opcion == '5':
            sub = input("1) Desactivar 2) Activar 3) Eliminar: ").strip()
            try:
                pid = int(input("ID producto: "))
            except ValueError:
                print("ID inválido.")
                continue
            if sub == '1':
                if producto_crud.deactivate(pid):
                    print("Desactivado.")
                else:
                    print("No encontrado.")
            elif sub == '2':
                if producto_crud.activate(pid):
                    print("Activado.")
                else:
                    print("No encontrado.")
            elif sub == '3':
                if producto_crud.delete(pid):
                    print("Eliminado.")
                else:
                    print("No encontrado.")
            else:
                print("Opción no válida.")
        elif opcion == '6':
            break
        else:
            print("Opción no válida.")


def menu_filtros_ano(producto_crud):
    """Menú de filtros por año."""
    try:
        anio_inicio = int(input("Año inicio: "))
    except ValueError:
        print("Año inválido.")
        return
    try:
        anio_fin = int(input("Año fin: "))
    except ValueError:
        print("Año inválido.")
        return
    productos = producto_crud.list_by_anio_range(anio_inicio, anio_fin)
    print(f"\nProductos entre {anio_inicio} y {anio_fin}:")
    for p in productos:
        print(p)
    counts = {}
    for p in producto_crud.list_all():
        a = getattr(p, 'anio', None)
        if a is not None and anio_inicio <= a <= anio_fin:
            counts[a] = counts.get(a, 0) + 1
    print("\nConteo por año:")
    for a in sorted(counts.keys()):
        print(f"{a}: {counts[a]}")


def menu_estadisticas(grupo_crud, investigador_crud, producto_crud):
    """Muestra estadísticas resumidas."""
    grupos = len(grupo_crud.list_all())
    invs = len(investigador_crud.list_all())
    prods = len(producto_crud.list_all())
    print("\n=== ESTADÍSTICAS ===")
    print(f"Grupos activos: {grupos}")
    print(f"Investigadores activos: {invs}")
    print(f"Productos activos: {prods}")
    counts_anio = {}
    counts_tipo = {}
    counts_cat = {}
    for p in producto_crud.list_all():
        a = getattr(p, 'anio', None)
        if a is not None:
            counts_anio[a] = counts_anio.get(a, 0) + 1
        t = getattr(p, 'tipo', 'Desconocido')
        counts_tipo[t] = counts_tipo.get(t, 0) + 1
        c = getattr(p, 'categoria', 'Desconocida')
        counts_cat[c] = counts_cat.get(c, 0) + 1
    print("\nPor año:")
    for a in sorted(counts_anio.keys()):
        print(f"  {a}: {counts_anio[a]}")
    print("\nPor tipo:")
    for t in counts_tipo:
        print(f"  {t}: {counts_tipo[t]}")
    print("\nPor categoría:")
    for c in counts_cat:
        print(f"  {c}: {counts_cat[c]}")


if __name__ == "__main__":
    main()
