from dataclasses import dataclass
from typing import Any

@dataclass
class Evidence:
    id: str
    source: str
    field: str
    value: Any
    unit: str
    as_of: str
    method: str = "原始字段"

def index_return(rows: list[dict], periods: int = 20) -> tuple[float|None, Evidence|None]:
    if len(rows) < periods + 1: return None, None
    rows = sorted(rows, key=lambda x: x.get("date", ""))
    start, end = rows[-(periods+1)], rows[-1]
    try:
        value = (float(end["close"]) / float(start["close"]) - 1) * 100
    except (KeyError, TypeError, ValueError, ZeroDivisionError): return None, None
    return round(value, 4), Evidence("ev-index-return", "fuyao", "close", value, "%", end.get("date", ""), f"({end['close']} / {start['close']} - 1) × 100")

def classify_state(return_pct: float|None, breadth_pct: float|None) -> str:
    if return_pct is None: return "数据不足"
    if breadth_pct is not None and abs(return_pct) < 2 and breadth_pct < 40: return "结构分化"
    if breadth_pct is not None and breadth_pct >= 60: return "广泛参与"
    return "信号混合"
