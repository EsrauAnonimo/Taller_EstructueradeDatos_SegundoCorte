# AGENTS.md

Repo for "Taller Estructura de Datos" (Unicesar, Grupo 05). Student assignment repo — `cpp/` has the C++ program and `python/` has a Streamlit dashboard that reads its output; `docs/` is still empty. No build/test/lint/CI configuration exists.

## Structure

- `python/` — `dashboard.py`, a Streamlit dashboard that reads and visualizes `../cpp/datos.csv`. Dependencies (`streamlit`, `pandas`, `plotly`) are **not** pinned/committed; install with `pip install streamlit pandas plotly`.
- `docs/` — documentation/report deliverables. Still empty.
- `cpp/` — all C++ code lives here, as header-only modules included by `main.cpp`:
  - `investigador.hpp` — `Investigador` struct.
  - `estructuras.hpp` — `Producto`, generic `ListaEnlazada<T>`, aliases `ListaInvestigadores`/`ListaProductos`.
  - `grupos.hpp` — `Grupo`, `Pila` (LIFO strings), `Cola` (FIFO ints).
  - `main.cpp` — interactive menu; contains `main()`.
- `integrantes.md` — group members and contacts. Keep it intact.

## Build & run (C++)

No build system; compile directly with g++. From the repo root:

```
g++ -std=c++17 -Wall -Wextra -I cpp cpp/main.cpp -o cpp/main.exe
```

- `-I cpp` is required: the headers are included by name (`"estructuras.hpp"`), not by path.
- The program reads/writes `datos.csv` in the **current working directory** (not next to the source). Run it from where you want the CSV to land. The dashboard expects it at `cpp/datos.csv`, so generate it from inside `cpp/`.
- `ListaEnlazada<T>` requires `T` to expose `int id`; do not try to store `Grupo` in it (Grupo is non-copyable because its list members have deleted copy). `main.cpp` stores `Grupo*` in a `std::vector<Grupo*>`.
- Header-defined free functions must stay `inline` (e.g. `imprimirInvestigador`) or linking fails across translation units.

## Run (Python dashboard)

From the repo root, after `pip install streamlit pandas plotly`:

```
streamlit run python/dashboard.py
```

- It reads `../cpp/datos.csv` relative to `python/dashboard.py` (path is resolved from the script location, not the CWD).
- `datos.csv` has no header row and mixes three record shapes by first field (`GRUPO` 4 cols, `INVESTIGADOR` 6, `PRODUCTO` 7). Parsing must set the max column count explicitly (`pd.read_csv(..., header=None, names=range(7))`); otherwise pandas infers 4 columns and fails on the longer lines.
- There is no direct product→investigator relation in the CSV; both belong to a group. The dashboard attributes a group's products to each of its investigators.

## Git workflow (observed, not documented elsewhere)

- Work happens on **per-language branches**: remote has `main`, `cpp`, `python`; members also use personal variants like `cpp-luis`. Check `git branch -a` and create/continue the branch matching the language you are editing instead of committing everything to `main`.
- `main` holds shared files (`README.md`, `integrantes.md`, `.gitignore`).

## Conventions

- Repo and file content are in Spanish (code comments, docs, member list). Write new docs/comments in Spanish to match. Avoid accents in C++ identifiers (`anio`, not `año`).
- Filename typo is intentional and must be preserved: `Taller_EstructueradeDatos_SegundoCorte` ("Estructuerade").
- `.gitignore` covers Python plus `*.exe` and `*.csv` (C++ executables and the generated `datos.csv`). Build artifacts are not tracked; do not `git add -f` them.
