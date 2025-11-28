# main_miembro1.py

import os
from pathlib import Path

from cfg_parser import load_grammar
from generador_validas import (
    generar_casos_validos,
    generar_casos_invalidos_desde_validos,
    generar_casos_extremos,
    calcular_estadisticas,
    guardar_json,
)


def _pedir_entero(mensaje: str, por_defecto: int) -> int:
    """
    Pide un entero por consola, con valor por defecto si el usuario
    solo presiona Enter o ingresa algo inválido.
    """
    try:
        texto = input(f"{mensaje} [{por_defecto}]: ").strip()
    except EOFError:
        # Por si se ejecuta en un entorno sin stdin
        return por_defecto

    if not texto:
        return por_defecto
    try:
        return int(texto)
    except ValueError:
        print("Valor inválido, se usará el valor por defecto.")
        return por_defecto


def main() -> None:
    print("=== Proyecto 2 INFO1148: Generador Automático de Casos de Prueba ===\n")

    # Ruta absoluta a 'gramatica.txt' en la MISMA carpeta que este archivo
    script_dir = Path(__file__).resolve().parent
    ruta_gramatica = script_dir / "gramatica.txt"

    print(f"Cargando gramática desde '{ruta_gramatica}'...\n")
    grammar = load_grammar(str(ruta_gramatica))

    print(f"Símbolo inicial : {grammar.start_symbol}")
    print(f"No terminales   : {', '.join(sorted(grammar.nonterminals))}")
    print(f"Terminales      : {', '.join(sorted(grammar.terminals))}\n")

    n_validas = _pedir_entero("Cantidad de casos VÁLIDOS a generar", 20)
    n_invalidas = _pedir_entero("Cantidad de casos INVÁLIDOS a generar", 20)
    n_extremas = _pedir_entero("Cantidad de casos EXTREMOS a generar", 10)

    max_depth = _pedir_entero("Profundidad máxima de derivación", 6)
    max_len = _pedir_entero("Longitud máxima de la cadena", 40)

    try:
        nombre_json = input(
            "Nombre del archivo JSON de salida [resultados.json]: "
        ).strip()
    except EOFError:
        nombre_json = ""

    if not nombre_json:
        nombre_json = "resultados.json"

    print("\n--- Generación de casos ---")
    print("Generando casos válidos...")
    casos_validos, t_validas = generar_casos_validos(
        grammar, n_validas, max_depth, max_len
    )
    print(f"  -> {len(casos_validos)} válidos generados.")

    print("Generando casos extremos...")
    casos_extremos, t_extremas = generar_casos_extremos(
        grammar, n_extremas, max_depth, max_len
    )
    print(f"  -> {len(casos_extremos)} extremos generados.")

    print("Generando casos inválidos (a partir de válidos mutados)...")
    casos_invalidos, t_invalidas = generar_casos_invalidos_desde_validos(
        casos_validos, n_invalidas
    )
    print(f"  -> {len(casos_invalidos)} inválidos generados.")

    casos_todos = casos_validos + casos_invalidos + casos_extremos

    tiempos_ms = {
        "validas": t_validas,
        "invalidas": t_invalidas,
        "extremas": t_extremas,
    }

    print("\nCalculando estadísticas...")
    reporte = calcular_estadisticas(casos_todos, tiempos_ms)

    print(f"Guardando resultados en '{nombre_json}'...")
    guardar_json(casos_todos, reporte, nombre_json)

    print("\n=== Resumen del Proceso ===")
    print(f"Total de casos generados: {reporte['total']}")
    for categoria, porcentaje in reporte["porcentajes"].items():
        print(f"  {categoria}: {porcentaje}%")
    print(f"Longitud promedio : {reporte['longitud_promedio']}")
    print(f"Profundidad máxima: {reporte['profundidad_maxima']}")
    print(f"Archivo JSON generado: {nombre_json}")
    print("\nFin de la ejecución.\n")


if __name__ == "__main__":
    main()
