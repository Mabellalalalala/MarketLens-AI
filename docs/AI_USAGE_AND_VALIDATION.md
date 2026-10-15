# AI 使用与验证

本阶段未调用 DeepSeek，避免在真实数据接入前生成无法追溯的结论。后续要求模型只消费 Evidence Registry，并校验 evidence_id、合规边界和 JSON Schema。

当前实现：`/api/research/ai` 仅把后端事实、证据和质量状态发送给 DeepSeek；返回必须是 JSON，`evidence_refs` 必须存在于本次 Evidence Registry，出现买卖/仓位/确定性预测词汇会被拦截。未配置 `DEEPSEEK_API_KEY` 时返回 `unconfigured`。

DeepSeek 本地验证：将 `DEEPSEEK_API_KEY` 注入当前终端后访问 `/api/research/ai`。密钥不写入仓库；部署暂不纳入本阶段。
