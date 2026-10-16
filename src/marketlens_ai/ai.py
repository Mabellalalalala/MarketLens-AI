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

ASK_FORBIDDEN=('明天涨','明天跌','未来涨','未来跌','目标价','上涨概率','下跌概率','推荐一只','推荐股票','买入','卖出','应该买','应该卖','仓位','资产配置','会涨还是跌','会涨','会跌')
def ask_marketlens(question, context):
    q=(question or '').strip()
    if not q: return {'status':'invalid_request','error':'请输入研究问题'}
    if any(word in q for word in ASK_FORBIDDEN):
        return {'status':'policy_blocked','answer':'当前产品不提供价格方向预测、个股推荐、买卖或资产配置建议。可以基于当前证据解释市场状态、指标关系和需要重新评估的客观条件。','evidence_refs':[],'limitation':'问题超出 Evidence-grounded Market Research 范围。'}
    evidence=context.get('evidence',[]); ids=[e.get('id') for e in evidence]
    if not evidence or context.get('data_quality',{}).get('level') in ('不足','ERROR','UNAVAILABLE'):
        return {'status':'insufficient_evidence','answer':'当前研究上下文没有足够证据回答这个问题。你可以继续查看市场宽度、风格或交易活跃度相关数据。','evidence_refs':[],'limitation':'当前 Evidence 不足。'}
    key=os.getenv('DEEPSEEK_API_KEY')
    if not key: return {'status':'unconfigured','error':'未配置 DEEPSEEK_API_KEY'}
    system='''你是 Ask MarketLens，Evidence-grounded Market Research 助手。只基于用户当前研究上下文回答，不重新取数、不计算新指标、不修改 Market State 或 Contradiction。回答 JSON：answer,evidence_refs,limitation,what_would_change_this_view。必须引用已有 evidence_id；无法支持的问题要明确说证据不足。若用户询问“今日/今天”，先根据 evidence 的 as_of 说明实际数据日期；如果 as_of 不是当天，明确写“当前最新数据截至 YYYY-MM-DD，并非实时今日数据”。不得预测涨跌、推荐股票、买卖、仓位、目标价或资产配置。'''
    payload={'question':q,'market_state':context.get('market_state'),'evidence':evidence,'contradictions':context.get('contradictions',[]),'limitations':context.get('limitations',[]),'data_quality':context.get('data_quality')}
    try:
        r=requests.post('https://api.deepseek.com/v1/chat/completions',headers={'Authorization':f'Bearer {key}'},json={'model':'deepseek-chat','messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}],'temperature':0.1},timeout=30); r.raise_for_status(); obj=json.loads(r.json()['choices'][0]['message']['content'])
        refs=obj.get('evidence_refs',[])
        if any(x not in ids for x in refs): return {'status':'invalid_evidence_refs','error':'回答引用了当前上下文不存在的 Evidence'}
        flat=json.dumps(obj,ensure_ascii=False)
        if any(x in flat for x in ASK_FORBIDDEN): return {'status':'policy_blocked','error':'回答包含被禁止的投资建议或预测'}
        return {'status':'ok',**obj}
    except Exception as e: return {'status':'failed','error':str(e)}
