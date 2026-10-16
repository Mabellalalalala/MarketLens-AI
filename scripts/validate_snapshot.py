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
print('snapshot validation: PASS',p)
