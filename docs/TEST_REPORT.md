# 测试说明

## 自动化测试

```text
PYTHONPATH=src python3 -m pytest -q
11 passed
```

测试覆盖指标计算、Evidence 校验、AI 合规拦截、扶摇 Provider mock 响应和 MCP 表格标准化。

## 主链路

|场景|预期|状态|
|---|---|---|
|沪深300近20交易日研究|真实扶摇行情→计算→Evidence→Market State|已验证|
|市场宽度|成分股快照分批→上涨/下跌/平盘/覆盖率|已验证|
|风格差|沪深300 vs 中证1000，DERIVED|代码已实现，本机需复跑确认|
|交易活跃度|Volume/Turnover及20日比率|已验证|
|Evidence Detail|显示来源、时点、单位、方法、状态|已验证|
|Ask MarketLens|仅基于当前上下文回答并引用 Evidence|已验证|

## 异常与边界

|场景|预期行为|状态|
|---|---|---|
|扶摇 timeout/网络失败|标记 ERROR/UNAVAILABLE，不静默补全|已实现并有 Provider 测试|
|空数据|对应维度不可用，Market State 降级|已实现|
|批量成分股部分失败|保留成功 batch，记录失败 batch 和 coverage|已实现|
|覆盖率不足|Breadth 不计算为正常结果|已实现|
|关键 Evidence 缺失|状态显示数据不足|已实现|
|数据时点不一致|进入 limitation，不冒充同一时点|已实现|
|DeepSeek 超时/失败|返回失败状态，不生成完整研判|已实现|
|非法 JSON|Validator 拒绝|已测试|
|虚构 evidence_id|Validator 拒绝|已测试|
|预测问题|合规拒答并提供证据研究替代方向|已测试|
|买卖/仓位问题|合规拒答|已实现|
|Important Events|UNAVAILABLE，不调用第三方新闻|已实现|

## 本机人工验收

1. 运行 `scripts/build_snapshot.py`；
2. 运行 `scripts/validate_snapshot.py`；
3. 启动 Flask 并打开本地页面；
4. 点击开始研究；
5. 查看五维状态、矛盾、Evidence；
6. 在 Ask MarketLens 输入正常问题和合规边界问题。

## 说明

自动化测试使用 mock 仅验证错误处理和纯函数，不将 mock 写入 REAL Snapshot。真实行情验证使用 Mac 本机扶摇 API，不能由 Codex 沙箱网络结果替代。
