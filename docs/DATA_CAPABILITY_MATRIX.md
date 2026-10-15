# 数据能力矩阵

|维度|来源|工具/接口|真实调用|线上可用性|备注|
|---|---|---|---|---|---|
|指数历史行情|iFinD MCP|index/index_data|失败（2026-10-16，本机 DNS 无法解析 api-mcp.51ifind.com:8643）|未验证|不得宣称成功；需确认网络/服务端鉴权|
|指数历史行情|扶摇|官方 API endpoint 待 PM 提供|未调用|未验证|代码已建立 FuyaoProvider，缺 FUYAO_API_BASE_URL/API_KEY|
|市场宽度/行业/估值|扶摇/iFinD|待按授权核实|未测试|未验证|UI 应显示未覆盖|

补充：已根据 PM 提供的官方说明确认扶摇 REST 鉴权为请求头 `X-api-key`，快照端点为 `/api/a-share/prices/snapshot?thscodes=...`，响应使用 `code/message/request_id/data` 信封。代码已接入该端点；历史行情 endpoint 仍待 API 参考和账号权限确认，未猜测或伪造。
