import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from flask import Flask, jsonify, request, render_template
from .providers.fuyao import FuyaoProvider
from .metrics import index_return, classify_state, trading_activity, Evidence
from .analysis import research_output
from .ai import generate
app=Flask(__name__, template_folder='templates')

def research(symbol='沪深300', periods=20):
    provider=FuyaoProvider(retries=0, timeout=8)
    data=provider.index_history(symbol, periods)
    raw=data.get('raw') if isinstance(data,dict) else None
    rows=(raw or {}).get('rows',[]) if isinstance(raw,dict) else []
    ret,evidence=index_return(rows, periods)
    activity, activity_evidence=trading_activity(rows, min(periods,20))
    breadth=provider.breadth_for_index({'沪深300':'000300.SH'}.get(symbol,symbol))
    braw=(breadth.get('raw') or {}) if isinstance(breadth,dict) else {}
    breadth_pct=braw.get('up_pct')
    quality='充分' if evidence and breadth.get('status')=='ok' else ('部分充分' if evidence else '不足')
    facts=([{'text':f'{periods}日区间收益率为 {ret}%','evidence_id':evidence.id}] if ret is not None else [])
    evidence_objs=([evidence] if evidence else [])
    if breadth.get('status')=='ok':
        facts.append({'text':f"成分股上涨占比 {breadth_pct}%（上涨{braw.get('up')}、下跌{braw.get('down')}、平盘{braw.get('flat')}，样本{braw.get('sample_count')}）",'evidence_id':'ev-breadth-000300'})
        evidence_objs.append(Evidence('ev-breadth-000300','fuyao','price_change_ratio_pct',breadth_pct,'% ',str(braw.get('timestamp') or 'unknown'),'成分股上涨数 / 有效快照数 × 100'))
    evidence_objs.extend(activity_evidence)
    base = research_output({'symbol':symbol,'periods':periods}, facts, evidence_objs, quality, ret, breadth_pct)
    base['trading_activity']={'status':'ok' if activity else 'unavailable','volume_ratio':(activity or {}).get('volume_ratio'),'amount_ratio':(activity or {}).get('amount_ratio'),'level':(activity or {}).get('level')}
    base['market_breadth']={'status':breadth.get('status'),'up_pct':breadth_pct,'up':braw.get('up'),'down':braw.get('down'),'flat':braw.get('flat'),'sample_count':braw.get('sample_count'),'error':breadth.get('error')}
    base['plan']=[{'step':'index_history','provider':provider.name,'status':data.get('status','unknown')}]
    base['data_quality'].update({'provider':provider.name,'error':data.get('error')})
    base['evidence']=[e.__dict__ for e in evidence_objs]
    base['raw']={'index':data,'breadth':breadth}
    return base
@app.get('/')
def index(): return render_template('index.html')
@app.get('/api/research')
def api_research(): return jsonify(research(request.args.get('symbol','沪深300'), int(request.args.get('periods',20))))

@app.get('/api/research/ai')
def api_research_ai():
    result=research(request.args.get('symbol','沪深300'), int(request.args.get('periods',20)))
    return jsonify(generate({'scope':result['research_scope'],'facts':result['facts'],'evidence':result['evidence'],'quality':result['data_quality']}, [e['id'] for e in result['evidence']]))

@app.get('/api/industries')
def api_industries():
    return jsonify(FuyaoProvider().industry_snapshot())
