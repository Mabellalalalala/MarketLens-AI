import json, sys
from pathlib import Path
ALLOWED={'REAL','DERIVED','LIMITED','UNAVAILABLE','STALE','ERROR'}
required={'snapshot_id','created_at','as_of','market','universe','lookback','evidence','market_state','contradiction_radar','data_quality'}
p=Path(sys.argv[1] if len(sys.argv)>1 else 'data/snapshots/latest.json'); d=json.loads(p.read_text())
missing=required-set(d); assert not missing, f'missing {missing}'
ids=[]
for cat,items in d['evidence'].items():
 for e in items:
  if 'evidence_id' in e: ids.append(e['evidence_id'])
  if 'status' in e: assert e['status'] in ALLOWED, e['status']
assert len(ids)==len(set(ids)), 'duplicate evidence IDs'
# Evidence status semantics: raw values REAL, deterministic calculations DERIVED.
for cat,items in d['evidence'].items():
 for e in items:
  if e.get('status') == 'REAL' and e.get('category') in ('market_breadth','style_rotation','trading_activity') and e.get('methodology','').startswith('Derived'):
   raise AssertionError(f'derived evidence marked REAL: {e.get("evidence_id")}')
print('snapshot validation: PASS',p)
