import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from marketlens_ai.providers.streamable_mcp import StreamableMCP
url=os.getenv('IFIND_INDEX_MCP_URL','https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-index-mcp'); auth=os.getenv('IFIND_MCP_AUTHORIZATION')
if not auth: raise SystemExit('缺少 IFIND_MCP_AUTHORIZATION（仅从本地 .env 读取）')
m=StreamableMCP(url,auth)
out={}
try:
 r=m.initialize(); out['initialize']={'http_status':r.status_code,'session':bool(m.sid)}
 r=m.list_tools(); body=r.json(); tools=[x.get('name') for x in body.get('result',{}).get('tools',[])]; out['tools_count']=len(tools); out['tools_sample']=tools[:20]
 out['requested_tools']={x:('available' if x in tools else 'NOT_VERIFIED') for x in ['get_a_share_index_constituents_ths_stock_list','get_a_share_index_prices_snapshot','get_a_share_index_catalog_ths_index_list']}
except Exception as e: out['error']=str(e)
print(json.dumps(out,ensure_ascii=False,indent=2))
