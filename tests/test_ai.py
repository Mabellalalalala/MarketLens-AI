import sys, json
sys.path.insert(0,'src')
from marketlens_ai.ai import validate_output
def test_evidence_validation():
 out=validate_output(json.dumps({'summary':'ok','evidence_refs':['e1']}),['e1'])
 assert out['status']=='ok'
def test_policy_block():
 out=validate_output(json.dumps({'summary':'明天涨多少','evidence_refs':[]}),[])
 assert out['status']=='policy_blocked'
def test_ask_policy_refusal():
    from marketlens_ai.ai import ask_marketlens
    out=ask_marketlens('明天沪深300会涨还是跌？', {'evidence':[{'id':'e1'}]})
    assert out['status']=='policy_blocked'
def test_ask_missing_context():
    from marketlens_ai.ai import ask_marketlens
    out=ask_marketlens('为什么偏弱？', {'evidence':[]})
    assert out['status']=='insufficient_evidence'
