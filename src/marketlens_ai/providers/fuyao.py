import os
from typing import Any
import requests

class FuyaoProvider:
    """扶摇 REST API adapter. Credentials are read only from the server environment."""
    name = "扶摇 API"
    def __init__(self, base_url=None, api_key=None, session=None):
        self.base_url = (base_url or os.getenv("FUYAO_API_BASE_URL") or "https://fuyao.aicubes.cn").rstrip("/")
        self.api_key = api_key or os.getenv("FUYAO_API_KEY") or os.getenv("API_KEY")
        self.session = session or requests.Session()

    def _get(self, path, params):
        if not self.api_key:
            return {"source": self.name, "status": "unconfigured", "error": "缺少 FUYAO_API_KEY/API_KEY"}
        try:
            response = self.session.get(
                self.base_url + path,
                params=params,
                headers={"X-api-key": self.api_key, "Accept": "application/json"},
                timeout=15,
            )
            response.raise_for_status()
            envelope = response.json()
            if envelope.get("code") not in (None, 0):
                return {"source": self.name, "status": "api_error", "error": envelope.get("message"), "request_id": envelope.get("request_id")}
            return {"source": self.name, "status": "ok", "request_id": envelope.get("request_id"), "raw": envelope.get("data", envelope)}
        except requests.RequestException as exc:
            return {"source": self.name, "status": "network_error", "error": str(exc)}
        except ValueError as exc:
            return {"source": self.name, "status": "invalid_response", "error": str(exc)}

    def snapshot(self, thscodes: str = "000300.SH") -> dict[str, Any]:
        """Real-time snapshot endpoint documented by Fuyao."""
        return self._get("/api/a-share/prices/snapshot", {"thscodes": thscodes})

    def index_history(self, symbol: str = "沪深300", periods: int = 20) -> dict[str, Any]:
        # Historical endpoint varies by Fuyao entitlement; keep this explicit rather than guessing.
        return {"source": self.name, "status": "unsupported", "error": "待根据账号可用 API 参考确认历史行情 endpoint", "symbol": symbol, "periods": periods}
