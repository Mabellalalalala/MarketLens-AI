import sys
sys.path.insert(0, 'src')
from marketlens_ai.providers.fuyao import FuyaoProvider

class Resp:
    status_code=200
    text='{"code":0}'
    def raise_for_status(self): pass
    def json(self): return {'code':0,'request_id':'r1','data':{'item':[{'close_price':1,'date_ms':1}]}}
class Session:
    def __init__(self): self.calls=[]
    def get(self,*args,**kwargs): self.calls.append((args,kwargs)); return Resp()

def test_snapshot_envelope():
    session=Session(); out=FuyaoProvider(api_key='test',session=session,retries=0).snapshot('000300.SH')
    assert out['status']=='ok' and out['request_id']=='r1' and out['raw']['item'][0]['close_price']==1

def test_documented_index_history_endpoint():
    session=Session(); out=FuyaoProvider(api_key='test',session=session,retries=0).index_history('沪深300',20)
    assert out['status']=='ok' and out['thscode']=='000300.SH'
    assert '/api/a-share-index/prices/historical' in session.calls[0][0][0]
    assert session.calls[0][1]['params']['interval']=='1d'

def test_missing_key_is_local_error():
    assert FuyaoProvider(api_key=None, session=Session()).snapshot()['status']=='unconfigured'
