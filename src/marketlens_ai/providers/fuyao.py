import os
import time
from typing import Any
import requests

class FuyaoProvider:
    """扶摇 REST adapter. 密钥只从服务端环境读取。"""
    name = "扶摇 API"
    def __init__(self, base_url=None, api_key=None, session=None, retries=2):
        self.base_url = (base_url or os.getenv("FUYAO_API_BASE_URL") or "https://fuyao.aicubes.cn").rstrip("/")
        self.api_key = api_key or os.getenv("FUYAO_API_KEY") or os.getenv("API_KEY")
        self.session = session or requests.Session()
        self.retries = retries

    def _get(self, path, params):
        if not self.api_key:
            return {"source": self.name, "status": "unconfigured", "error": "缺少 FUYAO_API_KEY/API_KEY"}
        headers = {"X-api-key": self.api_key, "Accept": "application/json"}
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(self.base_url + path, params=params, headers=headers, timeout=15)
                if response.status_code == 429 or response.text.find('"code":4001') >= 0:
                    if attempt < self.retries:
                        time.sleep(0.5 * (2 ** attempt)); continue
                    return {"source": self.name, "status": "rate_limited", "error": "扶摇接口限流（HTTP 429/code=4001）"}
                response.raise_for_status()
                envelope = response.json()
                if envelope.get("code") not in (None, 0):
                    return {"source": self.name, "status": "api_error", "error": envelope.get("message"), "request_id": envelope.get("request_id")}
                return {"source": self.name, "status": "ok", "request_id": envelope.get("request_id"), "raw": envelope.get("data", envelope)}
            except requests.RequestException as exc:
                if attempt < self.retries:
                    time.sleep(0.25 * (2 ** attempt)); continue
                return {"source": self.name, "status": "network_error", "error": str(exc)}
            except ValueError as exc:
                return {"source": self.name, "status": "invalid_response", "error": str(exc)}

    def snapshot(self, thscodes: str = "000300.SH") -> dict[str, Any]:
        return self._get("/api/a-share/prices/snapshot", {"thscodes": thscodes})

    def index_history(self, symbol: str = "沪深300", periods: int = 20) -> dict[str, Any]:
        path = os.getenv("FUYAO_INDEX_HISTORY_PATH")
        if not path:
            return {"source": self.name, "status": "unsupported", "error": "请配置已从扶摇 API 参考确认的 FUYAO_INDEX_HISTORY_PATH；未猜测历史端点", "symbol": symbol, "periods": periods}
        return self._get(path, {"thscodes": symbol, "periods": periods})
