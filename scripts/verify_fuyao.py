import json, os, sys
from datetime import datetime, timedelta, timezone
import requests
key=os.getenv('FUYAO_API_KEY') or os.getenv('API_KEY')
if not key: raise SystemExit('缺少 FUYAO_API_KEY 或 API_KEY')
end=datetime.now(timezone.utc); start=end-timedelta(days=45)
url='https://fuyao.aicubes.cn/api/a-share-index/prices/historical'
r=requests.get(url,params={'thscode':'000300.SH','interval':'1d','start':int(start.timestamp()*1000),'end':int(end.timestamp()*1000)},headers={'X-api-key':key},timeout=20)
body=r.json(); data=body.get('data') or {}; items=data.get('item') or []
print(json.dumps({'http_status':r.status_code,'code':body.get('code'),'message':body.get('message'),'request_id':body.get('request_id'),'data_timestamp':data.get('timestamp'),'item_count':len(items),'first':items[0] if items else None,'last':items[-1] if items else None},ensure_ascii=False,indent=2))
if r.status_code != 200 or body.get('code') != 0 or len(items)<20: sys.exit(2)
