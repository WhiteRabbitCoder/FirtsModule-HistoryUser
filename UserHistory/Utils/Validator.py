"""
Archivo: `validators.py`

Funciones de validación y parseo para usar en el proyecto:
- is_non_empty_string, clean_string
- is_valid_name
- is_positive_int_str / parse_positive_int
- is_positive_decimal_str / parse_positive_decimal
- is_unique_name
- format_decimal
- parse_bool
"""

import re
from typing import Iterable, Optional

def is_non_empty_string(value: Optional[str]) -> bool:
    """True si value es un string no vacío después de strip()."""
    return isinstance(value, str) and bool(value.strip())


def clean_string(value: Optional[str]) -> str:
    """Devuelve value.strip() o cadena vacía si es None."""
    return (value or "").strip()


_NAME_RE = re.compile(r"^(?!\d)[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9\s\-\._']+$")


def is_valid_name(value: Optional[str], min_len: int = 1, max_len: int = 100) -> bool:
    """
    Válida un nombre de producto básico:
    - no vacío (según min_len)
    - longitud entre min_len y max_len
    - no empieza por dígito
    - solo caracteres razonables (letras, números, espacios, - . _ ')
    """
    s = clean_string(value)
    if not (min_len <= len(s) <= max_len):
        return False
    return bool(_NAME_RE.match(s))

def is_valid_number(value: Optional[float]) -> bool:
    """
    Válida si el valor es un número (int o float).
    """
    return isinstance(value, (int, float))


def is_positive_int(value: int) -> bool:
    """True si value representa un entero positivo (>0)."""
    try:
        n = int(value)
        return n > 0
    except Exception:
        return False

def is_positive_int_str(value: str) -> bool:
    """True si value es un string que representa un entero positivo (>0)."""
    if not isinstance(value, str):
        return False
    s = value.strip()
    if not s.isdigit():
        return False
    try:
        return int(s) > 0
    except Exception:
        return False


def parse_positive_int(value: str) -> int:
    """
    Convierte value a int positivo (>0).
    Lanza ValueError si no es válido.
    """
    try:
        n = int(value)
    except Exception:
        raise ValueError("No es un entero válido.")
    if n <= 0:
        raise ValueError("El entero debe ser mayor que 0.")
    return n


_DECIMAL_RE = re.compile(r"^[+-]?\d+([.,]\d+)?$")


def is_positive_decimal(value: str) -> bool:
    """True si value es decimal u entero positivo (acepta ',' o '.')."""
    if not isinstance(value, str):
        return False
    s = value.strip().replace(" ", "")
    if not _DECIMAL_RE.match(s):
        return False
    try:
        return float(s.replace(",", ".")) > 0
    except Exception:
        return False

def is_valid_decimal(value: str) -> bool:
    """True si value es decimal o entero (acepta ',' o '.')."""
    if not isinstance(value, str):
        return False
    s = value.strip().replace(" ", "")
    if not _DECIMAL_RE.match(s):
        return False
    try:
        float(s.replace(",", "."))
        return True
    except Exception:
        return False


def parse_positive_decimal(value: str) -> float:
    """
    Convierte value a float positivo (>0). Acepta coma o punto como separador.
    Lanza ValueError si no es válido.
    """
    if not isinstance(value, str):
        raise ValueError("Valor no es una cadena.")
    s = value.strip().replace(" ", "")
    if not _DECIMAL_RE.match(s):
        raise ValueError("Formato decimal inválido.")
    f = float(s.replace(",", "."))
    if f <= 0:
        raise ValueError("El número debe ser mayor que 0.")
    return f


def is_unique_name(name: str, container: Iterable[str]) -> bool:
    """
    Comprueba si name no está en container (case-insensitive).
    container puede ser keys de un dict o lista de nombres.
    """
    if not is_non_empty_string(name):
        return False
    name_norm = clean_string(name).lower()
    return all(name_norm != clean_string(c).lower() for c in container)


def format_decimal(value: float, decimals: int = 2, decimal_sep: str = ",") -> str:
    """
    Formatea un número con `decimals` decimales y usa `decimal_sep`
    (por ejemplo \",\") como separador decimal.
    """
    fmt = f"{{:.{decimals}f}}".format(value)
    if decimal_sep != ".":
        fmt = fmt.replace(".", decimal_sep)
    return fmt


def parse_bool(value: str) -> Optional[bool]:
    """
    Interpreta respuestas yes/no en múltiples idiomas.
    Devuelve True/False o None si no puede interpretarse.
    Acepta: y/n, s/n, yes/no, true/false (case-insensitive).
    """
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    true_set = {"y", "yes", "s", "si", "true", "t", "1"}
    false_set = {"n", "no", "false", "f", "0"}
    if v in true_set:
        return True
    if v in false_set:
        return False
    return None
