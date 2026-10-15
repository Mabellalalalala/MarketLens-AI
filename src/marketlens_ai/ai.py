import json, os, requests
ALLOWED={'facts','inferences','contradictions','uncertainties','watch_conditions','follow_ups','evidence_refs','summary'}
FORBIDDEN=('明天涨','明天跌','应该买','应该卖','满仓','买入','卖出','持有','仓位','收益保证','目标价','止损')
def validate_output(text, evidence_ids):
    try: obj=json.loads(text)
    except Exception as e: return {'status':'invalid_json','error':str(e)}
    if not isinstance(obj,dict) or not ALLOWED.issuperset(obj): return {'status':'invalid_schema','error':'字段不符合结构化契约'}
    refs=obj.get('evidence_refs',[])
    if not isinstance(refs,list) or any(x not in evidence_ids for x in refs): return {'status':'invalid_evidence_refs','error':'模型引用了不存在的 evidence_id'}
    flat=json.dumps(obj,ensure_ascii=False)
    if any(x in flat for x in FORBIDDEN): return {'status':'policy_blocked','error':'输出包含预测、买卖或仓位建议'}
    return {'status':'ok','result':obj}
def generate(payload, evidence_ids):
    key=os.getenv('DEEPSEEK_API_KEY')
    if not key: return {'status':'unconfigured','error':'未配置 DEEPSEEK_API_KEY'}
    system='''你是 MarketLens AI 的 A 股市场状态研究助手。只使用输入中的真实字段和证据，不补造数字。输出必须帮助用户理解当前市场状态、主要矛盾、哪些可观察条件会改变判断。严格区分 facts（事实）、inferences（归纳）、contradictions（可比指标背离）、uncertainties（缺失或时点问题）、watch_conditions（可观察变量和阈值）。不得预测未来涨跌，不得给买入、卖出、持有、仓位、收益目标或交易时点建议。follow_ups 只能是继续研究问题或数据核查动作。只返回 JSON，字段为 summary,facts,inferences,contradictions,uncertainties,watch_conditions,follow_ups,evidence_refs。facts 和 evidence_refs 必须引用输入中存在的证据。'''
    try:
        r=requests.post('https://api.deepseek.com/v1/chat/completions',headers={'Authorization':f'Bearer {key}'},json={'model':'deepseek-chat','messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}],'temperature':0.1},timeout=30)
        r.raise_for_status(); text=r.json()['choices'][0]['message']['content']; return validate_output(text,evidence_ids)
    except Exception as e: return {'status':'failed','error':str(e)}
