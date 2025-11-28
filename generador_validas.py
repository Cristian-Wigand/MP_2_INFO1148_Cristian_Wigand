# generador_validas.py
 
from typing import Dict, List, Tuple
import time
import random
import json

from cfg_parser import Grammar
from derivador import derive_valid_string, derive_extreme_string, OPERADORES


def _contar_operadores(cadena: str) -> Dict[str, int]:
    return {op: cadena.count(op) for op in OPERADORES}


def _estimar_profundidad(cadena: str) -> int:
    """
    Estima la profundidad del 'árbol' a partir del anidamiento de paréntesis.
    No es exacto, pero es una buena aproximación para expresiones aritméticas.
    """
    depth = 0
    max_depth = 0
    for ch in cadena:
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth = max(depth - 1, 0)
    return max_depth


def _crear_caso(
    cadena: str,
    tipo: str,
    mutaciones: Dict[str, int] | None = None,
) -> Dict:
    caso: Dict = {
        "cadena": cadena,
        "tipo": tipo,
        "longitud": len(cadena),
        "profundidad": _estimar_profundidad(cadena),
        "operadores": _contar_operadores(cadena),
    }
    if mutaciones is None:
        caso["mutaciones"] = {"eliminacion": 0, "sustitucion": 0, "insercion": 0}
    else:
        caso["mutaciones"] = mutaciones
    return caso


def generar_casos_validos(
    grammar: Grammar, cantidad: int, max_depth: int, max_len: int
) -> Tuple[List[Dict], float]:
    casos: List[Dict] = []
    t0 = time.time()
    for _ in range(cantidad):
        cadena, _ = derive_valid_string(grammar, max_depth, max_len, mode="random")
        casos.append(_crear_caso(cadena, "valida"))
    t1 = time.time()
    tiempo_total_ms = (t1 - t0) * 1000.0
    return casos, tiempo_total_ms


def _mutar_cadena(cadena: str, max_mutaciones: int = 2) -> Tuple[str, Dict[str, int]]:
    """
    Genera una versión inválida de la cadena mediante mutaciones sintácticas simples:
    - Eliminación de caracteres
    - Sustitución por operadores u otros símbolos
    - Inserción de operadores/paréntesis
    """
    mut_counts = {"eliminacion": 0, "sustitucion": 0, "insercion": 0}
    if not cadena:
        return cadena, mut_counts

    num_mut = random.randint(1, max_mutaciones)
    s = cadena
    for _ in range(num_mut):
        if not s:
            break
        mtype = random.choice(["eliminacion", "sustitucion", "insercion"])
        idx = random.randrange(0, len(s))
        if mtype == "eliminacion":
            s = s[:idx] + s[idx + 1 :]
            mut_counts["eliminacion"] += 1
        elif mtype == "sustitucion":
            pool = list(OPERADORES) + ["a", "b", "?"]
            new_char = random.choice(pool)
            s = s[:idx] + new_char + s[idx + 1 :]
            mut_counts["sustitucion"] += 1
        elif mtype == "insercion":
            pool = list(OPERADORES) + [")", "(", "?"]
            new_char = random.choice(pool)
            s = s[:idx] + new_char + s[idx:]
            mut_counts["insercion"] += 1
    return s, mut_counts


def generar_casos_invalidos_desde_validos(
    casos_validos: List[Dict], cantidad: int, max_mutaciones: int = 2
) -> Tuple[List[Dict], float]:
    """
    Genera 'cantidad' de casos inválidos mutando cadenas válidas ya generadas.
    """
    if not casos_validos or cantidad <= 0:
        return [], 0.0

    casos: List[Dict] = []
    t0 = time.time()
    for _ in range(cantidad):
        base = random.choice(casos_validos)["cadena"]
        mutada, mut_counts = _mutar_cadena(base, max_mutaciones)
        casos.append(_crear_caso(mutada, "invalida", mut_counts))
    t1 = time.time()
    tiempo_total_ms = (t1 - t0) * 1000.0
    return casos, tiempo_total_ms


def generar_casos_extremos(
    grammar: Grammar, cantidad: int, max_depth: int, max_len: int
) -> Tuple[List[Dict], float]:
    casos: List[Dict] = []
    t0 = time.time()
    for _ in range(cantidad):
        cadena, _ = derive_extreme_string(grammar, max_depth, max_len)
        casos.append(_crear_caso(cadena, "extrema"))
    t1 = time.time()
    tiempo_total_ms = (t1 - t0) * 1000.0
    return casos, tiempo_total_ms


def calcular_estadisticas(
    casos: List[Dict], tiempos_ms_por_tipo: Dict[str, float]
) -> Dict:
    """
    Calcula las métricas pedidas en el enunciado:
    - Cantidad total
    - Distribución porcentual por categoría
    - Longitud promedio
    - Profundidad máxima
    - Conteo de operadores
    - Niveles de mutación por tipo
    - Tiempos de ejecución por categoría
    """
    total_casos = len(casos)
    if total_casos == 0:
        return {
            "total": 0,
            "porcentajes": {"validas": 0.0, "invalidas": 0.0, "extremas": 0.0},
            "longitud_promedio": 0.0,
            "profundidad_maxima": 0,
            "operadores": {op: 0 for op in OPERADORES},
            "mutaciones": {"eliminacion": 0, "sustitucion": 0, "insercion": 0},
            "tiempos_ms": {},
        }

    conteo_por_tipo = {"valida": 0, "invalida": 0, "extrema": 0}
    longitudes: List[int] = []
    profundidades: List[int] = []
    operadores_totales = {op: 0 for op in OPERADORES}
    mut_totales = {"eliminacion": 0, "sustitucion": 0, "insercion": 0}

    for caso in casos:
        tipo = caso.get("tipo", "valida")
        if tipo in conteo_por_tipo:
            conteo_por_tipo[tipo] += 1
        longitudes.append(caso.get("longitud", len(caso.get("cadena", ""))))
        profundidades.append(caso.get("profundidad", 0))
        ops = caso.get("operadores", {})
        for op in OPERADORES:
            operadores_totales[op] += ops.get(op, 0)
        muts = caso.get("mutaciones", {})
        for k in mut_totales:
            mut_totales[k] += muts.get(k, 0)

    porcentajes = {
        "validas": round(conteo_por_tipo["valida"] * 100.0 / total_casos, 2),
        "invalidas": round(conteo_por_tipo["invalida"] * 100.0 / total_casos, 2),
        "extremas": round(conteo_por_tipo["extrema"] * 100.0 / total_casos, 2),
    }

    longitud_promedio = round(sum(longitudes) / len(longitudes), 2) if longitudes else 0.0
    profundidad_maxima = max(profundidades) if profundidades else 0

    tiempos_detalle: Dict[str, Dict[str, float]] = {}
    # tiempos_ms_por_tipo usa claves "validas", "invalidas", "extremas"
    for clave_tiempo, tipo_caso in [
        ("validas", "valida"),
        ("invalidas", "invalida"),
        ("extremas", "extrema"),
    ]:
        total_ms = tiempos_ms_por_tipo.get(clave_tiempo, 0.0)
        n = conteo_por_tipo[tipo_caso]
        tiempos_detalle[clave_tiempo] = {
            "total_ms": round(total_ms, 3),
            "promedio_ms": round(total_ms / n, 3) if n > 0 else 0.0,
        }

    reporte = {
        "total": total_casos,
        "porcentajes": porcentajes,
        "longitud_promedio": longitud_promedio,
        "profundidad_maxima": profundidad_maxima,
        "operadores": operadores_totales,
        "mutaciones": mut_totales,
        "tiempos_ms": tiempos_detalle,
    }
    return reporte


def guardar_json(casos: List[Dict], reporte: Dict, nombre: str = "resultados.json") -> None:
    """
    Exporta todos los casos y el reporte general en un archivo JSON.
    """
    data = {
        "casos": casos,
        "reporte_general": reporte,
    }
    with open(nombre, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
