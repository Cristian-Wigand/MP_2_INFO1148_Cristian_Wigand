# Generador de Casos de Prueba desde una Gramática Libre de Contexto

Mini Proyecto 2 — INFO1148 — Semestre II-2025  
Universidad Católica de Temuco

Este proyecto implementa un generador automático de expresiones aritméticas a partir de una **gramática libre de contexto (GLC)**.  
El sistema produce tres tipos de cadenas:

- **Válidas**: cumplen la gramática especificada.
- **Inválidas**: se obtienen aplicando mutaciones sintácticas sobre cadenas válidas.
- **Extremas**: buscan alcanzar límites máximos de **profundidad** y **longitud**.

Todos los casos generados se guardan en un archivo **JSON**, junto con un **reporte estadístico** que resume la distribución de categorías, longitudes, profundidad máxima, operadores y tiempos de ejecución.

---

## Estructura del proyecto

Archivos principales:

- `cfg_parser.py`  
  Carga una gramática libre de contexto desde un archivo de texto (`gramatica.txt`) y la representa internamente con:
  - símbolo inicial
  - no terminales
  - terminales
  - producciones

- `derivador.py`  
  Implementa la derivación controlada:
  - `derive_valid_string(...)`: genera cadenas **válidas**.
  - `derive_extreme_string(...)`: genera cadenas **extremas**, intentando maximizar profundidad y longitud.

- `generador_validas.py`  
  Coordina la generación y clasificación:
  - genera casos **válidos**, **inválidos** (por mutación) y **extremos**
  - calcula estadísticas de resumen
  - exporta resultados a JSON (`guardar_json(...)`)

- `main_miembro1.py`  
  Punto de entrada del programa. Proporciona una **interfaz por consola** para:
  - cargar la gramática
  - pedir parámetros al usuario (cantidades, profundidad, longitud)
  - ejecutar la generación de casos
  - guardar el archivo `resultados.json`

- `gramatica.txt`  
  Archivo de texto con la gramática de expresiones aritméticas utilizada por defecto.

---

## Requisitos

- **Python 3.10+** (cualquier versión 3.x reciente funciona).
- Sistema operativo: Windows / Linux / macOS.
- No se requieren librerías externas (solo biblioteca estándar de Python).

---

## Cómo ejecutar el proyecto

1. Clonar o copiar la carpeta del proyecto.

2. Verificar que los siguientes archivos estén en la **misma carpeta**:

   - `cfg_parser.py`  
   - `derivador.py`  
   - `generador_validas.py`  
   - `main_miembro1.py`  
   - `gramatica.txt`

3. Abrir una terminal en la carpeta del proyecto.

   En Windows, por ejemplo:

   ```bash
   cd "C:\Users\...\Mini proyecto 2"
   ```

4. Ejecutar el archivo principal:

   ```bash
   python main_miembro1.py
   ```

5. El programa:

   - Cargará automáticamente `gramatica.txt`.
   - Mostrará el símbolo inicial, no terminales y terminales.
   - Pedirá por consola:
     - Cantidad de casos **válidos** a generar.
     - Cantidad de casos **inválidos** a generar.
     - Cantidad de casos **extremos** a generar.
     - Profundidad máxima de derivación.
     - Longitud máxima de las expresiones.
     - Nombre del archivo JSON de salida (por defecto: `resultados.json`).

6. Al finalizar, se indicará en pantalla el resumen y el nombre del archivo JSON generado.

---

## Formato de la gramática (`gramatica.txt`)

El archivo `gramatica.txt` define una gramática libre de contexto.  
Formato general soportado:

```text
START: E
NONTERMINALS: E T F
TERMINALS: + - * / % ( ) num

E -> E + T | E - T | T
T -> T * F | T / F | T % F | F
F -> ( E ) | num
```

- `START:` define el símbolo inicial.
- `NONTERMINALS:` lista de no terminales.
- `TERMINALS:` lista de terminales.
- Las producciones usan `->` y alternativas con `|`.
- Los símbolos en el lado derecho van separados por espacios.

El parser también puede **inferir terminales** si no se declaran explícitamente.

---

## Formato del archivo JSON de salida

El archivo generado (por defecto `resultados.json`) tiene la forma:

```json
{
  "casos": [
    {
      "cadena": "3+(4*5)",
      "tipo": "valida",
      "longitud": 7,
      "profundidad": 3,
      "operadores": {
        "+": 1,
        "-": 0,
        "*": 1,
        "/": 0,
        "%": 0
      },
      "mutaciones": {
        "eliminacion": 0,
        "sustitucion": 0,
        "insercion": 0
      }
    },
    {
      "cadena": "(((((8*4)+3)-((7%2)*9))*((3+5)*(6/2)))+(9*(4*(8-2))))",
      "tipo": "extrema",
      "longitud": 41,
      "profundidad": 8,
      "operadores": {
        "+": 4,
        "-": 1,
        "*": 7,
        "/": 1,
        "%": 1
      },
      "mutaciones": {
        "eliminacion": 0,
        "sustitucion": 0,
        "insercion": 0
      }
    }
  ],
  "reporte_general": {
    "total": 120,
    "porcentajes": {
      "validas": 50.0,
      "invalidas": 25.0,
      "extremas": 25.0
    },
    "longitud_promedio": 14.2,
      "profundidad_maxima": 9,
      "operadores": {
        "+": 31,
        "-": 14,
        "*": 28,
        "/": 10,
        "%": 4
      },
      "mutaciones": {
        "eliminacion": 7,
        "sustitucion": 4,
        "insercion": 3
      },
      "tiempos_ms": {
        "validas": {
          "total_ms": 80.5,
          "promedio_ms": 4.0
        },
        "invalidas": {
          "total_ms": 40.2,
          "promedio_ms": 2.0
        },
        "extremas": {
          "total_ms": 31.6,
          "promedio_ms": 3.1
        }
      }
    }
  }
}
```

### Campos principales

- Para cada caso:
  - `cadena`: expresión generada.
  - `tipo`: `"valida"`, `"invalida"` o `"extrema"`.
  - `longitud`: número de caracteres.
  - `profundidad`: estimación basada en el anidamiento de paréntesis.
  - `operadores`: conteo por operador (`+`, `-`, `*`, `/`, `%`).
  - `mutaciones`: cuántas mutaciones de eliminación / sustitución / inserción se aplicaron.

- En `reporte_general`:
  - `total`: cantidad total de casos.
  - `porcentajes`: distribución de válidas / inválidas / extremas.
  - `longitud_promedio`: promedio de longitudes.
  - `profundidad_maxima`: máxima profundidad encontrada.
  - `operadores`: sumatoria de operadores en todos los casos.
  - `mutaciones`: total de mutaciones aplicadas.
  - `tiempos_ms`: tiempo total y promedio (en milisegundos) por categoría.

---

## Roles del equipo

- **Cristian Wigand**  
  Implementación de `cfg_parser.py` (lectura y análisis de la gramática).

- **Ignacio De Celis**  
  Implementación de `derivador.py` (derivación de cadenas válidas y extremas).

- **Maximiliano Sierra**  
  Implementación de `generador_validas.py` (generación de casos, mutaciones e informe estadístico).

- **Matías Araya**  
  Implementación de `main_miembro1.py` (interfaz por consola e integración) y definición de la gramática base (`gramatica.txt`).

---