# Entregable - Estado actual del programa PEA-i

## Descripción
Aplicación de escritorio para gestión de grupos, investigadores y productos de investigación. 
Interfaz gráfica desarrollada con CustomTkinter. Estructura basada en Multilista y CRUD.

## Componentes implementados
- GUI CustomTkinter (app.py, tabs, forms, widgets, styles)
- Persistencia: JSON (intento) con fallback a JSON (sin aviso emergente)
- CRUD para Grupos, Investigadores, Productos
- Scraping SCIENTI con fallback CSV
- Datos de ejemplo en python/datos/datos.json

## Estado de ejecución
La aplicación se inicializa correctamente. Al ejecutar python gui/app.py desde el directorio python, 
la ventana se crea sin errores (verificado con creación/destroy de instancia).

## Archivos relevantes
- .vscode/launch.json: configuración para F5 (cwd ${workspaceFolder}/python)
- python/gui/app.py: ventana principal, menú, persistencia
- python/datos/datos.json: datos de ejemplo (1 grupo, 2 investigadores, 3 productos)
- README.md: instrucciones de instalación y ejecución

## Cómo ejecutar (profesor)
Opción A (VS Code): Abrir proyecto -> F5 -> "PEA-i GUI"
Opción B (Terminal): cd python && python gui/app.py

## Notas
- Requiere customtkinter, matplotlib, pandas, requests, beautifulsoup4, , , pdfplumber
- Funciona sin .env ni JSON (usa JSON por defecto)