# cfg_parser.py

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class Grammar:
    start_symbol: str
    nonterminals: Set[str]
    terminals: Set[str]
    productions: Dict[str, List[List[str]]] = field(default_factory=dict)


def load_grammar(path: str) -> Grammar:
    """
    Carga una gramática libre de contexto desde un archivo de texto.

    Formatos aceptados (mezclables en el mismo archivo):
        START: E
        NONTERMINALS: E, T, F
        TERMINALS: +, -, *, /, %, (, ), num
        E -> E + T | T
        T -> T * F | F
        F -> ( E ) | num

    Reglas:
    - Las producciones usan '->' y alternativas separadas por '|'.
    - Los símbolos en el lado derecho van separados por espacios.
    - Líneas que comienzan con '#' se ignoran.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f]

    production_specs = []
    nonterminals_declared: Set[str] = set()
    terminals_declared: Set[str] = set()
    start_symbol = None

    for line in raw_lines:
        if not line or line.startswith("#"):
            continue

        upper = line.upper()
        if upper.startswith("START:") or upper.startswith("INICIO:"):
            start_symbol = line.split(":", 1)[1].strip()
        elif upper.startswith("NONTERMINALS:") or upper.startswith("NO TERMINALES:"):
            part = line.split(":", 1)[1]
            for name in part.replace(",", " ").split():
                if name:
                    nonterminals_declared.add(name.strip())
        elif upper.startswith("TERMINALS:") or upper.startswith("TERMINALES:"):
            part = line.split(":", 1)[1]
            for name in part.replace(",", " ").split():
                if name:
                    terminals_declared.add(name.strip())
        else:
            if "->" not in line:
                raise ValueError(f"Línea inválida en gramática (falta '->'): {line}")
            left, right = line.split("->", 1)
            lhs = left.strip()
            if not lhs:
                raise ValueError(f"Lado izquierdo vacío en producción: {line}")
            nonterminals_declared.add(lhs)
            production_specs.append((lhs, right))

    if not nonterminals_declared:
        raise ValueError("La gramática no contiene producciones.")

    if start_symbol is None:
        # Primer no terminal declarado será el símbolo inicial
        start_symbol = next(iter(nonterminals_declared))

    productions: Dict[str, List[List[str]]] = {nt: [] for nt in nonterminals_declared}
    rhs_tokens_all: List[str] = []

    for lhs, right in production_specs:
        alts = [alt.strip() for alt in right.split("|")]
        for alt in alts:
            if alt == "" or alt == "ε":
                tokens: List[str] = []
            else:
                # Se asume que los símbolos vienen separados por espacios
                tokens = alt.split()
            productions[lhs].append(tokens)
            rhs_tokens_all.extend(tokens)

    if not terminals_declared:
        # Inferir terminales si no se declararon
        for tok in rhs_tokens_all:
            if tok and tok != "ε" and tok not in nonterminals_declared:
                terminals_declared.add(tok)

    return Grammar(
        start_symbol=start_symbol,
        nonterminals=nonterminals_declared,
        terminals=terminals_declared,
        productions=productions,
    )


def is_nonterminal(token: str, grammar: Grammar) -> bool:
    """Retorna True si el token es un no terminal de la gramática."""
    return token in grammar.nonterminals
