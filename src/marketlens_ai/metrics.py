from dataclasses import dataclass
from typing import Any

@dataclass
class Evidence:
    id: str
    category: str = 'market_structure'
    status: str = 'REAL'
    freshness: str = 'CURRENT'
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
    return round(value, 4), Evidence(id='ev-index-return', source='fuyao', field='close', value=value, unit='%', as_of=end.get('date',''), method=f"({end['close']} / {start['close']} - 1) × 100")

def classify_state(return_pct: float|None, breadth_pct: float|None) -> str:
    if return_pct is None: return "数据不足"
    if breadth_pct is not None and abs(return_pct) < 2 and breadth_pct < 40: return "结构分化"
    if breadth_pct is not None and breadth_pct >= 60: return "广泛参与"
    return "信号混合"

def trading_activity(rows: list[dict], window: int = 20):
    """Volume + Turnover activity proxy; returns ratios and traceable evidence."""
    if len(rows) < window + 1: return None, []
    ordered=sorted(rows,key=lambda x:x.get('date',''))
    latest=ordered[-1]; hist=ordered[-(window+1):-1]
    def ratio(field):
        try:
            cur=float(latest[field]); avg=sum(float(x[field]) for x in hist if x.get(field) is not None)/len([x for x in hist if x.get(field) is not None])
            return round(cur/avg,4) if avg else None
        except (KeyError,TypeError,ValueError,ZeroDivisionError): return None
    vr, ar=ratio('volume'), ratio('turnover')
    if vr is None and ar is None: return None, []
    level='Elevated' if max(x for x in (vr,ar) if x is not None)>1.2 else ('Weak' if max(x for x in (vr,ar) if x is not None)<0.8 else 'Normal')
    ev=[Evidence(id='ev-volume-activity',source='fuyao',field='volume',value=vr,unit='ratio',as_of=str(latest.get('date','')),method='latest volume / prior 20D average volume',category='trading_activity'),Evidence(id='ev-turnover-activity',source='fuyao',field='turnover',value=ar,unit='ratio',as_of=str(latest.get('date','')),method='latest turnover / prior 20D average turnover',category='trading_activity')]
    return {'volume_ratio':vr,'amount_ratio':ar,'level':level}, ev
