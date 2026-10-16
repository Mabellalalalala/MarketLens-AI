"""Official Fuyao MCP smoke test; never guesses tool names."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from marketlens_ai.providers.mcp import FuyaoMCPProvider
p=FuyaoMCPProvider(); out={}
a=p.constituents('000300.SH'); out['A_constituents']=a
items=((a.get('raw') or {}).get('result') or {}).get('structuredContent',{}).get('item',[]) if a.get('status')=='ok' else []
codes=[x.get('thscode') for x in items if x.get('thscode')]
out['B_snapshot_batches']=[]
for i in range(0,len(codes),50): out['B_snapshot_batches'].append(p.stock_snapshot(codes[i:i+50]))
out['C_index_snapshot']=p.index_snapshot(['000300.SH'])
out['D_CSI1000']='NOT_VERIFIED: official guide supplied no explicit historical MCP tool for 000852.SH'
out['E_concept_catalog']=p.index_catalog('cn_concept')
print(json.dumps({'tool_results':out,'constituent_count':len(codes),'batch_count':len(out['B_snapshot_batches'])},ensure_ascii=False,indent=2))
