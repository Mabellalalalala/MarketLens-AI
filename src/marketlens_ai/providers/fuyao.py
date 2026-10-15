import os, requests
class FuyaoProvider:
    name = "扶摇 API"
    def __init__(self, base_url=None, api_key=None):
        self.base_url=base_url or os.getenv("FUYAO_API_BASE_URL")
        self.api_key=api_key or os.getenv("FUYAO_API_KEY")
    def index_history(self, symbol="沪深300", periods=20):
        if not self.base_url or not self.api_key:
            return {"source": self.name, "status":"unconfigured", "error":"缺少 FUYAO_API_BASE_URL/FUYAO_API_KEY"}
        r=requests.get(self.base_url.rstrip('/')+'/index/history', params={"symbol":symbol,"periods":periods}, headers={"Authorization":f"Bearer {self.api_key}"}, timeout=15)
        r.raise_for_status(); return {"source":self.name,"status":"ok","raw":r.json()}
