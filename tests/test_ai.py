import sys, json
sys.path.insert(0,'src')
from marketlens_ai.ai import validate_output
def test_evidence_validation():
 out=validate_output(json.dumps({'summary':'ok','evidence_refs':['e1']}),['e1'])
 assert out['status']=='ok'
def test_policy_block():
 out=validate_output(json.dumps({'summary':'明天涨多少','evidence_refs':[]}),[])
 assert out['status']=='policy_blocked'
