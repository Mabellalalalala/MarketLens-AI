"""Build one REAL/DERIVED research snapshot. No fixture fallback."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))
from marketlens_ai.core_research import research

def main():
    result=research('沪深300',20)
    now=datetime.now(timezone.utc).isoformat()
    sid=datetime.now(timezone.utc).strftime('snapshot_%Y%m%dT%H%M%SZ')
    evidence=result.get('evidence',[])
    grouped={k:[] for k in ['market_structure','market_breadth','style_rotation','trading_activity','valuation','sentiment','important_events']}
    for e in evidence: grouped.setdefault(e.get('category','market_structure'),[]).append(e)
    grouped['market_breadth'].append({'evidence_id':'ev-breadth-000300','category':'market_breadth','status':'DERIVED' if result.get('market_breadth',{}).get('status')=='DERIVED' else result.get('market_breadth',{}).get('status','UNAVAILABLE'),'metrics':result.get('market_breadth',{}),'source':'Fuyao','source_fields':['price_change_ratio_pct'],'methodology':'Derived from REAL Fuyao constituent snapshots; constituent breadth is a proxy, not full A-share breadth.','unit':'percent'})
    snapshot={'snapshot_id':sid,'created_at':now,'as_of':now,'market':'A-share','universe':'CSI300','lookback':'20 trading days','evidence':grouped,'market_state':result.get('market_state',{}),'contradiction_radar':result.get('contradictions',[]),'data_quality':{'coverage':{x['label']:x['status'] for x in result.get('evidence_coverage',[])},'level':result.get('data_quality',{}).get('level'),'missing_dimensions':[x['label'] for x in result.get('evidence_coverage',[]) if x['status'] in ('UNAVAILABLE','ERROR')],'limitations':result.get('uncertainties',[]),'failed_requests':result.get('raw',{}).get('breadth',{}).get('failures',[])}}
    out=Path(__file__).parents[1]/'data'/'snapshots'; out.mkdir(parents=True,exist_ok=True)
    (out/f'{sid}.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'latest.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'snapshot_id':sid,'path':str(out/'latest.json'),'coverage':snapshot['data_quality']['coverage']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
