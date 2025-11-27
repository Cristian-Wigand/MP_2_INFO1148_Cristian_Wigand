# derivador.py

from typing import List, Tuple
import random

from cfg_parser import Grammar, is_nonterminal

OPERADORES = {"+", "-", "*", "/", "%"}


def _contains_nonterminal(tokens: List[str], grammar: Grammar) -> bool:
    return any(is_nonterminal(t, grammar) for t in tokens)


def _select_nonterminal_index(tokens: List[str], grammar: Grammar, mode: str) -> int | None:
    indices = [i for i, t in enumerate(tokens) if is_nonterminal(t, grammar)]
    if not indices:
        return None
    if mode == "balanced":
        # Izquierda primero (tipo derivación más "ordenada")
        return indices[0]
    # Aleatorio
    return random.choice(indices)


def _tokens_to_string(tokens: List[str]) -> str:
    """
    Convierte la lista de tokens en una cadena.
    Reemplaza 'num' / 'numero' / 'n' por dígitos aleatorios.
    """
    result: List[str] = []
    for tok in tokens:
        lower = tok.lower()
        if lower in {"num", "numero", "n"}:
            result.append(str(random.randint(0, 9)))
        else:
            result.append(tok)
    return "".join(result)


def derive_valid_string(
    grammar: Grammar, max_depth: int, max_len: int, mode: str = "random"
) -> Tuple[str, int]:
    """
    Genera una cadena válida a partir de la gramática usando derivación controlada.
    Retorna (cadena, profundidad_aproximada_por_pasos).
    """
    tokens: List[str] = [grammar.start_symbol]
    depth = 0
    max_depth_reached = 0
    steps = 0
    max_steps = max(max_depth * 10 + 50, 50)

    while _contains_nonterminal(tokens, grammar) and depth < max_depth and steps < max_steps:
        idx = _select_nonterminal_index(tokens, grammar, mode)
        if idx is None:
            break
        nt = tokens[idx]
        prod_list = grammar.productions.get(nt)
        if not prod_list:
            replacement: List[str] = []
        else:
            replacement = random.choice(prod_list)
        tokens = tokens[:idx] + replacement + tokens[idx + 1 :]
        depth += 1
        steps += 1
        max_depth_reached = max(max_depth_reached, depth)
        if len(tokens) > max_len * 2:
            break

    # Intento de terminar derivando alternativas poco recursivas
    safety = 0
    while _contains_nonterminal(tokens, grammar) and safety < max_steps:
        safety += 1
        idx = _select_nonterminal_index(tokens, grammar, "balanced")
        if idx is None:
            break
        nt = tokens[idx]
        prod_list = grammar.productions.get(nt, [])
        if not prod_list:
            replacement = []
        else:
            best = None
            best_score = None
            for alt in prod_list:
                score = sum(1 for t in alt if is_nonterminal(t, grammar))
                if best is None or score < best_score:
                    best = alt
                    best_score = score
            replacement = best or []
        tokens = tokens[:idx] + replacement + tokens[idx + 1 :]

    s = _tokens_to_string(tokens)
    if len(s) > max_len:
        s = s[:max_len]
    return s, max_depth_reached


def derive_extreme_string(grammar: Grammar, max_depth: int, max_len: int) -> Tuple[str, int]:
    """
    Genera una cadena 'extrema', intentando llegar a la profundidad y longitud máximas.
    """
    tokens: List[str] = [grammar.start_symbol]
    depth = 0
    max_depth_reached = 0
    steps = 0
    max_steps = max(max_depth * 15 + 100, 100)

    # Fase 1: privilegiar producciones recursivas para aumentar profundidad
    while _contains_nonterminal(tokens, grammar) and depth < max_depth and steps < max_steps:
        idx = _select_nonterminal_index(tokens, grammar, "balanced")
        if idx is None:
            break
        nt = tokens[idx]
        prod_list = grammar.productions.get(nt, [])
        if not prod_list:
            replacement = []
        else:
            recursive = []
            non_recursive = []
            for alt in prod_list:
                if nt in alt:
                    recursive.append(alt)
                else:
                    non_recursive.append(alt)
            if recursive:
                replacement = random.choice(recursive)
            else:
                replacement = random.choice(prod_list)
        tokens = tokens[:idx] + replacement + tokens[idx + 1 :]
        depth += 1
        steps += 1
        max_depth_reached = max(max_depth_reached, depth)
        if len(tokens) > max_len * 2:
            break

    # Fase 2: cerrar derivaciones con alternativas no recursivas
    safety = 0
    while _contains_nonterminal(tokens, grammar) and safety < max_steps:
        safety += 1
        idx = _select_nonterminal_index(tokens, grammar, "balanced")
        if idx is None:
            break
        nt = tokens[idx]
        prod_list = grammar.productions.get(nt, [])
        if not prod_list:
            replacement = []
        else:
            non_recursive = [alt for alt in prod_list if nt not in alt]
            if non_recursive:
                replacement = random.choice(non_recursive)
            else:
                replacement = random.choice(prod_list)
        tokens = tokens[:idx] + replacement + tokens[idx + 1 :]
        if len(tokens) > max_len * 2:
            break

    s = _tokens_to_string(tokens)

    # Si quedó muy corta, extenderla agregando operadores y números
    while len(s) < max_len:
        op = random.choice(list(OPERADORES))
        s = f"({s}{op}{random.randint(0,9)})"
        if len(s) > max_len * 2:
            break

    if len(s) > max_len:
        s = s[:max_len]
    return s, max_depth_reached or depth or 1

