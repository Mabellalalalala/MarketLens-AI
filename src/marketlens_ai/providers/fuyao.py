import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any
import requests

class FuyaoProvider:
    """扶摇 REST adapter. 密钥只从服务端环境读取。"""
    name = "扶摇 API"
    def __init__(self, base_url=None, api_key=None, session=None, retries=2, timeout=15):
        self.base_url = (base_url or os.getenv("FUYAO_API_BASE_URL") or "https://fuyao.aicubes.cn").rstrip("/")
        self.api_key = api_key or os.getenv("FUYAO_API_KEY") or os.getenv("API_KEY")
        self.session = session or requests.Session()
        # 本机常见代理会导致扶摇连接被远端关闭；默认直连，可由调用方传入自定义 session。
        self.session.trust_env = False
        self.retries = retries
        self.timeout = timeout

    def _get(self, path, params):
        if not self.api_key:
            return {"source": self.name, "status": "unconfigured", "error": "缺少 FUYAO_API_KEY/API_KEY"}
        headers = {"X-api-key": self.api_key, "Accept": "application/json"}
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(self.base_url + path, params=params, headers=headers, timeout=self.timeout)
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
        codes = {"沪深300": "000300.SH", "上证指数": "000001.SH", "深证成指": "399001.SZ", "创业板指": "399006.SZ", "中证1000": "000852.SH"}
        thscode = codes.get(symbol, symbol)
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=max(periods * 3, 45))
        out = self._get("/api/a-share-index/prices/historical", {
            "thscode": thscode, "interval": "1d",
            "start": int(start.timestamp() * 1000), "end": int(end.timestamp() * 1000),
        })
        if out.get("status") == "ok":
            raw = out.get("raw") or {}
            items = raw.get("item", []) if isinstance(raw, dict) else []
            rows = [{"date": str(i.get("date_ms", "")), "close": i.get("close_price"),
                     "open": i.get("open_price"), "high": i.get("high_price"),
                     "low": i.get("low_price"), "volume": i.get("volume"),
                     "turnover": i.get("turnover")} for i in items]
            out["raw"] = {"timestamp": raw.get("timestamp"), "rows": rows, "item": items}
        out["symbol"] = symbol; out["thscode"] = thscode; out["periods"] = periods
        return out


    def index_catalog(self, tag: str = "industry") -> dict[str, Any]:
        return self._get("/api/a-share-index/catalog/ths-index-list", {"tag": tag})

    def index_constituents(self, thscode: str = "000300.SH") -> dict[str, Any]:
        return self._get("/api/a-share-index/constituents/ths-stock-list", {"thscode": thscode})

    def industry_snapshot(self, limit: int = 12) -> dict[str, Any]:
        catalog = self.index_catalog("industry")
        if catalog.get("status") != "ok": return catalog
        items = (catalog.get("raw") or {}).get("item", [])[:limit]
        codes = [x.get("thscode") for x in items if x.get("thscode")]
        if not codes: return {"source":self.name,"status":"empty","error":"行业目录为空"}
        snap = self._get("/api/a-share-index/prices/snapshot", {"thscodes": ",".join(codes)})
        if snap.get("status") == "ok": snap["catalog"] = items
        return snap

    def stock_snapshot(self, thscodes: list[str], batch_size: int = 50) -> dict[str, Any]:
        batches=[]; all_rows=[]; failures=[]
        for i in range(0, len(thscodes), batch_size):
            codes=thscodes[i:i+batch_size]
            out=self._get("/api/a-share/prices/snapshot", {"thscodes": ",".join(codes)})
            record={'batch':i//batch_size+1,'requested':len(codes),'status':out.get('status'),'request_id':out.get('request_id'),'error':out.get('error')}
            if out.get('status')=='ok':
                rows=(out.get('raw') or {}).get('item',[]); all_rows.extend(rows); record['returned']=len(rows)
            else: failures.append(record)
            batches.append(record)
        status='ok' if all_rows else ('error' if failures else 'empty')
        return {'source':self.name,'status':status,'raw':{'item':all_rows,'batches':batches},'failures':failures}

    def breadth_for_index(self, thscode: str = "000300.SH") -> dict[str, Any]:
        members = self.index_constituents(thscode)
        if members.get("status") != "ok": return members
        items=(members.get("raw") or {}).get("item",[]); codes=[x.get("thscode") for x in items if x.get("thscode")]
        if not codes: return {"source":self.name,"status":"empty","error":"成分股为空"}
        snap=self.stock_snapshot(codes); rows=(snap.get("raw") or {}).get("item",[])
        changes=[x.get("price_change_ratio_pct") for x in rows if isinstance(x.get("price_change_ratio_pct"),(int,float))]
        up=sum(x>0 for x in changes); down=sum(x<0 for x in changes); flat=sum(x==0 for x in changes); coverage=len(changes)/len(codes)
        status='ok' if coverage>=0.8 else 'insufficient'
        return {"source":self.name,"status":status,"error":None if status=='ok' else '成分股快照覆盖率低于80%',"raw":{"member_count":len(codes),"sample_count":len(changes),"coverage":round(coverage,4),"up":up,"down":down,"flat":flat,"up_pct":round(up/len(changes)*100,2) if changes else None,"snapshot":rows,"batches":(snap.get('raw') or {}).get('batches',[])},"failures":snap.get('failures',[])}
    def trading_days(self) -> dict[str, Any]:
        return self._get("/api/a-share/calendar/trading-days", {})
