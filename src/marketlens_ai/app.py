import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from flask import Flask, jsonify, request, render_template
from .providers.fuyao import FuyaoProvider
from .core_research import research
from .ai import generate, ask_marketlens
app=Flask(__name__, template_folder='templates')

@app.get('/')
def index(): return render_template('index.html')
@app.get('/api/research')
def api_research(): return jsonify(research(request.args.get('symbol','沪深300'), int(request.args.get('periods',20))))

@app.get('/api/evidence/<evidence_id>')
def api_evidence(evidence_id):
    result=research(request.args.get('symbol','沪深300'), int(request.args.get('periods',20)))
    for item in result.get('evidence',[]):
        if item.get('id') == evidence_id: return jsonify(item)
    return jsonify({'status':'not_found','evidence_id':evidence_id}), 404

@app.get('/api/research/ai')
def api_research_ai():
    focus=request.args.get('focus')
    result=research(request.args.get('symbol','沪深300'), int(request.args.get('periods',20)), focus)
    return jsonify(generate({'scope':result['research_scope'],'facts':result['facts'],'evidence':result['evidence'],'quality':result['data_quality']}, [e['id'] for e in result['evidence']]))

@app.get('/api/industries')
def api_industries():
    return jsonify(FuyaoProvider().industry_snapshot())

@app.post('/api/ask')
def api_ask():
    payload=request.get_json(silent=True) or {}
    return jsonify(ask_marketlens(payload.get('question',''), payload.get('context') or {}))
