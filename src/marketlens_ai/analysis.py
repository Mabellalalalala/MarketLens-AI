from .metrics import Evidence

def contradiction(index_return_pct, breadth_pct):
    if index_return_pct is None or breadth_pct is None: return {'status':'insufficient','reason':'缺少可比指数收益或市场宽度'}
    if index_return_pct > 0 and breadth_pct < 40: return {'status':'detected','label':'指数上涨与参与度偏低背离','threshold':'区间收益>0且上涨占比<40%'}
    if index_return_pct < 0 and breadth_pct > 60: return {'status':'detected','label':'指数下跌与参与度仍广泛背离','threshold':'区间收益<0且上涨占比>60%'}
    return {'status':'none'}

def research_output(scope, facts, evidence, quality, index_return_pct=None, breadth_pct=None):
    return {'research_scope':scope,'market_state':{'label':'信号混合' if quality!='不足' else '数据不足'},'facts':facts,'inferences':[],'contradictions':[contradiction(index_return_pct,breadth_pct)],'uncertainties':([] if quality=='充分' else ['数据覆盖不足，暂不生成完整市场判断']),'watch_conditions':['后续交易日市场宽度连续低于40%或高于60%时重新评估'],'follow_ups':['深入研究风格','深入研究行业/风险变量'],'evidence_refs':[e.id for e in evidence],'data_quality':{'level':quality}}
