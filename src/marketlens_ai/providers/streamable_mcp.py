import os, time, requests
class StreamableMCP:
    def __init__(self, url, authorization, session=None):
        self.url=url; self.authorization=authorization; self.session=session or requests.Session(); self.session.trust_env=False; self.sid=None
    def _headers(self):
        h={'Authorization':self.authorization,'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
        if self.sid: h['Mcp-Session-Id']=self.sid
        return h
    def initialize(self):
        payload={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'marketlens-ai','version':'0.1'}}}
        r=self.session.post(self.url,headers=self._headers(),json=payload,timeout=20); self.sid=r.headers.get('Mcp-Session-Id'); return r
    def list_tools(self):
        if not self.sid: self.initialize()
        r=self.session.post(self.url,headers=self._headers(),json={'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},timeout=20); return r
    def call(self,name,arguments):
        if not self.sid: self.initialize()
        return self.session.post(self.url,headers=self._headers(),json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':name,'arguments':arguments}},timeout=30)
