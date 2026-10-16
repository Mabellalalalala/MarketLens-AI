import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from marketlens_ai.providers.streamable_mcp import StreamableMCP
url=os.getenv('IFIND_INDEX_MCP_URL','https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-index-mcp'); auth=os.getenv('IFIND_MCP_AUTHORIZATION')
if not auth: raise SystemExit('缺少 IFIND_MCP_AUTHORIZATION（仅从本地 .env 读取）')
m=StreamableMCP(url,auth); out={}
try:
 r=m.initialize(); out['initialize']={'http_status':r.status_code,'session':bool(m.sid)}
 r=m.list_tools(); body=r.json(); definitions=body.get('result',{}).get('tools',[]); out['tools_count']=len(definitions); out['schemas']={x.get('name'):x.get('inputSchema') for x in definitions}
 by={x.get('name'):x for x in definitions}
 # These queries are only sent when the documented schema exposes a query field.
 for name,query in [('index_data','沪深300和中证1000过去20个交易日的收盘点数、成交量、成交额'),('sector_data','A股行业板块过去5个交易日的表现')]:
  schema=(by.get(name) or {}).get('inputSchema') or {}; props=schema.get('properties') or {}
  if 'query' in props:
   rr=m.call(name,{'query':query});
   try: data=rr.json()
   except Exception: data={'text':rr.text[:500]}
   out[name]={'http_status':rr.status_code,'response':data}
  else: out[name]={'status':'NOT_TESTED','reason':'实际 schema 未暴露 query 参数'}
 name='index_highfreq_quotes'; schema=(by.get(name) or {}).get('inputSchema') or {}; props=schema.get('properties') or {}
 if name in by and all(k in props for k in ('symbols','data_mode','indicators')):
  rr=m.call(name,{'symbols':'000300.SH','data_mode':'real_time','indicators':'最新价,涨跌幅,成交量,成交额'})
  try: data=rr.json()
  except Exception: data={'text':rr.text[:500]}
  out[name]={'http_status':rr.status_code,'response':data}
 else: out[name]={'status':'NOT_TESTED','schema_properties':list(props)}
except Exception as e: out['error']=str(e)
print(json.dumps(out,ensure_ascii=False,indent=2))
