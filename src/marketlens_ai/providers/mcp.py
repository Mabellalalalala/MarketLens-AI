"""Fuyao MCP adapter using only officially specified server/tool names."""
import os, json, time, requests

TOOLS={
 'constituents':('fuyao-a-share-index-mcp','get_a_share_index_constituents_ths_stock_list'),
 'stock_snapshot':('fuyao-a-share-mcp','get_a_share_prices_snapshot'),
 'index_snapshot':('fuyao-a-share-index-mcp','get_a_share_index_prices_snapshot'),
 'index_catalog':('fuyao-a-share-index-mcp','get_a_share_index_catalog_ths_index_list'),
}
class FuyaoMCPProvider:
    name='扶摇 MCP'; provider='mcp'
    def __init__(self, endpoint=None, api_key=None, session=None):
        self.endpoint=endpoint or os.getenv('FUYAO_MCP_ENDPOINT')
        self.api_key=api_key or os.getenv('FUYAO_API_KEY') or os.getenv('API_KEY')
        self.session=session or requests.Session(); self.session.trust_env=False
    def call(self, capability, params):
        if not self.endpoint: return {'status':'NOT_VERIFIED','server':TOOLS[capability][0],'tool':TOOLS[capability][1],'error':'FUYAO_MCP_ENDPOINT 未配置；官方指南未提供可直接确认的 endpoint'}
        if not self.api_key: return {'status':'ERROR','error':'缺少 FUYAO_API_KEY'}
        server,tool=TOOLS[capability]; started=time.time()
        payload={'jsonrpc':'2.0','id':int(started*1000),'method':'tools/call','params':{'name':tool,'arguments':params}}
        try:
            r=self.session.post(self.endpoint,headers={'X-api-key':self.api_key,'Content-Type':'application/json'},json=payload,timeout=20)
            body=r.json(); status='ok' if r.status_code<400 and 'error' not in body else 'ERROR'
            return {'status':status,'server':server,'tool':tool,'http_status':r.status_code,'retrieved_at':time.time(),'raw':body,'error':body.get('error')}
        except Exception as e: return {'status':'ERROR','server':server,'tool':tool,'error':str(e)}
    def constituents(self, thscode='000300.SH'): return self.call('constituents',{'thscode':thscode})
    def stock_snapshot(self, thscodes): return self.call('stock_snapshot',{'thscodes':','.join(thscodes)})
    def index_snapshot(self, thscodes): return self.call('index_snapshot',{'thscodes':','.join(thscodes)})
    def index_catalog(self, tag='cn_concept'): return self.call('index_catalog',{'tag':tag})
