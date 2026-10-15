import sys
sys.path.insert(0, 'src')
from marketlens_ai.providers.fuyao import FuyaoProvider
class Resp:
    status_code=200; text='{"code":0}'
    def raise_for_status(self): pass
    def json(self): return {'code':0,'request_id':'r1','data':{'item':[{'close':1}]}}
class Session:
    def get(self,*args,**kwargs): return Resp()
def test_snapshot_envelope():
    out=FuyaoProvider(api_key='test',session=Session(),retries=0).snapshot('000300.SH')
    assert out['status']=='ok' and out['request_id']=='r1' and out['raw']['item'][0]['close']==1
def test_history_requires_explicit_path(monkeypatch):
    monkeypatch.delenv('FUYAO_INDEX_HISTORY_PATH', raising=False)
    assert FuyaoProvider(api_key='test').index_history()['status']=='unsupported'
