from marketlens_ai.metrics import index_return, classify_state
def test_index_return():
 rows=[{'date':str(i),'close':100+i} for i in range(21)]
 value,e=index_return(rows,20)
 assert round(value,2)==20.0 and e.id=='ev-index-return'
def test_missing_data(): assert index_return([],20)==(None,None)
def test_state(): assert classify_state(None,None)=='数据不足'
