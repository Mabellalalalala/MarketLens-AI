import os
from flask import Flask, jsonify, request, render_template
from .providers.fuyao import FuyaoProvider
from .metrics import index_return, classify_state
from .analysis import research_output
app=Flask(__name__, template_folder='templates')

def research(symbol='沪深300', periods=20):
    provider=FuyaoProvider()
    data=provider.index_history(symbol, periods)
    raw=data.get('raw') if isinstance(data,dict) else None
    rows=(raw or {}).get('rows',[]) if isinstance(raw,dict) else []
    ret,evidence=index_return(rows, periods)
    quality='充分' if evidence else ('不足' if data.get('status')!='ok' else '部分充分')
    base = research_output({'symbol':symbol,'periods':periods}, ([{'text':f'{periods}日区间收益率为 {ret}%','evidence_id':evidence.id}] if ret is not None else []), ([evidence] if evidence else []), quality, ret, None)
    base['plan']=[{'step':'index_history','provider':provider.name,'status':data.get('status','unknown')}]
    base['data_quality'].update({'provider':provider.name,'error':data.get('error')})
    base['raw']=data
    return base
@app.get('/')
def index(): return render_template('index.html')
@app.get('/api/research')
def api_research(): return jsonify(research(request.args.get('symbol','沪深300'), int(request.args.get('periods',20))))
