import json, os, requests
ALLOWED={'facts','inferences','contradictions','uncertainties','watch_conditions','follow_ups','evidence_refs','summary'}
FORBIDDEN=('明天涨','应该买','满仓','买入','卖出','仓位','收益保证')
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
    system='你是市场研究助手。只基于输入事实，不预测涨跌，不给买卖或仓位建议。只返回 JSON，字段为 summary,facts,inferences,contradictions,uncertainties,watch_conditions,follow_ups,evidence_refs。'
    try:
        r=requests.post('https://api.deepseek.com/v1/chat/completions',headers={'Authorization':f'Bearer {key}'},json={'model':'deepseek-chat','messages':[{'role':'system','content':system},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}],'temperature':0.1},timeout=30)
        r.raise_for_status(); text=r.json()['choices'][0]['message']['content']; return validate_output(text,evidence_ids)
    except Exception as e: return {'status':'failed','error':str(e)}
