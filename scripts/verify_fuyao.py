"""验证扶摇沪深300历史行情；仅使用 Python 标准库，避免额外依赖。"""
import json, os, sys
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
key=os.getenv('FUYAO_API_KEY') or os.getenv('API_KEY')
if not key: raise SystemExit('缺少 FUYAO_API_KEY 或 API_KEY，请先 export')
end=datetime.now(timezone.utc); start=end-timedelta(days=45)
params=urlencode({'thscode':'000300.SH','interval':'1d','start':int(start.timestamp()*1000),'end':int(end.timestamp()*1000)})
req=Request('https://fuyao.aicubes.cn/api/a-share-index/prices/historical?'+params,headers={'X-api-key':key,'Accept':'application/json'})
try:
    with urlopen(req, timeout=20) as resp:
        status=resp.status; body=json.loads(resp.read().decode('utf-8'))
except HTTPError as exc:
    status=exc.code
    body=json.loads(exc.read().decode('utf-8')) if exc.fp else {'message':str(exc)}
except (URLError, TimeoutError) as exc:
    raise SystemExit(f'网络请求失败: {exc}')
data=body.get('data') or {}; items=data.get('item') or []
print(json.dumps({'http_status':status,'code':body.get('code'),'message':body.get('message'),'request_id':body.get('request_id'),'data_timestamp':data.get('timestamp'),'item_count':len(items),'first':items[0] if items else None,'last':items[-1] if items else None},ensure_ascii=False,indent=2))
if status != 200 or body.get('code') != 0 or len(items)<20: sys.exit(2)
