"""Fail-closed identity checks for the standalone, inactive 0.4 method."""
from pathlib import Path

from .contract import InvalidInput, digest
from .sd2_contract import ANALYZER, RULES, BYTE_LIMIT, parameters
from .sd2_io import _binding, _bytes, _json
from .sd2_rating import CONFIG, FORMULA, METHOD_ID
from .sd2_rating_identity import METHOD_HASH

_ROOT = Path(__file__).parent


def frozen_method(budget=None):
    if budget is not None:
        budget.check()
    method = _json(_bytes(_ROOT / "sd2_method_0_4.json", BYTE_LIMIT))
    if digest(method) != METHOD_HASH:
        raise InvalidInput("Unknown or changed SD2 difficulty method")
    if (method["format"] != "picross-sd2-method-v1" or method["id"] != METHOD_ID
            or method["formula"] != FORMULA or method["configuration"] != CONFIG
            or method["analyzer"] != ANALYZER or method["rules"] != RULES
            or method["analysis_parameters"] != parameters()):
        raise InvalidInput("SD2 method does not match the exact implemented contract")
    for name, expected in method["artifacts"].items():
        if digest(_json(_bytes(_ROOT / name, BYTE_LIMIT))) != expected:
            raise InvalidInput(f"Changed SD2 method artifact: {name}")
        if budget is not None:
            budget.check()
    for name, expected in method["implementation"].items():
        if _binding(_bytes(_ROOT / name, BYTE_LIMIT))["sha256"] != expected:
            raise InvalidInput(f"Changed frozen SD2 implementation: {name}")
        if budget is not None:
            budget.check()
    return method
