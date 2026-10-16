# AI 使用与验证记录

## 使用的 AI 工具

- Codex：项目审计、代码迁移、扶摇 REST/MCP 适配、确定性指标、Evidence Layer、测试和文档。
- DeepSeek：仅用于基于 Research Snapshot 的自然语言解释，不负责取数、计算、阈值或状态决定。

## DeepSeek 输入

DeepSeek 只接收：

- 当前 Market State；
- 已计算 facts/inferences；
- Contradiction Radar；
- Evidence Registry；
- 数据质量和限制；
- 用户的 Ask MarketLens 问题。

未经标准化的原始行情不会直接交给模型作为计算输入，DeepSeek 不调用 MCP、不联网搜索事件，也不能修改确定性结果。

## AI 参与环节

1. 解释当前市场状态；
2. 归纳已由规则识别的主要矛盾；
3. 说明数据限制和不确定性；
4. 描述需要观察的客观条件；
5. 回答基于当前 Evidence 的继续研究问题。

## 验证和修正记录

|问题|修正|
|---|---|
|模型可能引用不存在的 evidence_id|后端校验所有 evidence_refs，未注册 ID 直接拒绝|
|模型可能把缺失证据说成完整结论|数据质量门禁；不足/错误上下文不生成完整研判|
|模型可能输出买卖、仓位或预测|Prompt 约束 + 禁止词 Validator 双重拦截|
|模型可能自行计算或修改指标|只发送确定性计算结果，禁止模型决定阈值|
|模型可能把历史数据称为今日数据|输入 evidence as_of，并要求回答先说明数据时点|
|模型可能把事件搜索结果混入同花顺证据|Important Events 固定为 UNAVAILABLE，禁止联网补全|

## 实际验证

- DeepSeek 真实调用成功，返回结构化 JSON；
- `evidence_refs` 与 Evidence Registry 校验通过；
- 预测问题返回合规拒答；
- 缺少 Evidence 时返回证据不足；
- API/网络失败时不生成貌似完整的正常结论。
