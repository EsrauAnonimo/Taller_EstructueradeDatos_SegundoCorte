# Taller 2 — Estructura de Datos — PEA-i

## Universidad
Universidad Popular del Cesar

## Facultad
Facultad de Ingeniería y Tecnologías

## Asignatura
Estructura de Datos

## Integrantes del grupo
- Esteban Raúl Vergara Jaime

## Requisitos
- Python 3.11+
- pip

## Instalación
`ash
pip install -r python/requirements.txt
`

## Cómo ejecutar

### Opción A — VS Code
1. Abrir el proyecto en VS Code.
2. Presionar F5 y seleccionar la configuración "PEA-i GUI".

### Opción B — Terminal
`ash
cd python
python gui/app.py
`

## Persistencia
- Por defecto usa JSON (python/datos/datos.json) para facilitar la evaluación sin necesidad de configurar base de datos.
- Para usar PostgreSQL, copiar .env.example a .env y configurar las credenciales correspondientes.

## Estructura del proyecto (breve)
- python/ — Código fuente (modelos, CRUD, persistencia, scraping, GUI con CustomTkinter)
- python/gui/ — Interfaz gráfica (tabs, formularios, widgets y estilos)
- python/datos/ — Datos de ejemplo en JSON
- .vscode/launch.json — Configuración para ejecutar con F5 en VS Code
- python/requirements.txt — Dependencias del proyecto

## Enlace al video de YouTube
[Video de demostración - PEA-i](https://www.youtube.com/placeholder)