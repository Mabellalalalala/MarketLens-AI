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

def style_rotation(large_rows, small_rows, periods=20):
    large, le = index_return(large_rows, periods); small, se = index_return(small_rows, periods)
    if large is None or small is None: return {'status':'UNAVAILABLE','large_return':large,'small_return':small,'difference':None}, [x for x in (le,se) if x]
    diff=round(small-large,4); label='Small/mid-cap leadership' if diff < -2 else ('Large-cap leadership' if diff > 2 else 'Mixed')
    ev=Evidence(id='ev-style-difference',source='fuyao',field='20d_return_difference',value=diff,unit='percentage_points',as_of=max(le.as_of,se.as_of),method='中证1000 20D收益 - 沪深300 20D收益',category='style_rotation')
    return {'status':'DERIVED','large_return':large,'small_return':small,'difference':diff,'label':label}, [le,se,ev]

def activity_contradiction(index_return_pct, activity):
    if index_return_pct is None or not activity or activity.get('volume_ratio') is None or activity.get('amount_ratio') is None: return {'status':'insufficient','reason':'缺少价格或交易活跃度数据'}
    active=max(activity['volume_ratio'],activity['amount_ratio'])
    if abs(index_return_pct)>=2 and active<0.8: return {'status':'detected','label':'价格变化明显但交易活跃度偏弱','threshold':'|20D收益|>=2%且Volume/Amount ratio<0.8','evidence_ids':['ev-index-return','ev-volume-activity','ev-turnover-activity']}
    if abs(index_return_pct)>=2 and active>1.2: return {'status':'detected','label':'价格变化伴随交易活跃度上升','threshold':'|20D收益|>=2%且Volume/Amount ratio>1.2','evidence_ids':['ev-index-return','ev-volume-activity','ev-turnover-activity']}
    return {'status':'none'}
