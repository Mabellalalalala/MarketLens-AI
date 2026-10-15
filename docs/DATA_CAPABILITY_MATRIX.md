# 数据能力矩阵

|维度|来源|工具/接口|真实调用|线上可用性|备注|
|---|---|---|---|---|---|
|指数历史行情|iFinD MCP|index/index_data|失败（2026-10-16，本机 DNS 无法解析 api-mcp.51ifind.com:8643）|未验证|不得宣称成功；需确认网络/服务端鉴权|
|指数历史行情|扶摇 REST|`/api/a-share-index/prices/historical`|已按文档接入，待网络/密钥实调|待验证|单指数、1d、近5年、毫秒时间戳|
|市场宽度/行业/估值|扶摇/iFinD|待按授权核实|未测试|未验证|UI 应显示未覆盖|

补充：已根据 PM 提供的官方说明确认扶摇 REST 鉴权为请求头 `X-api-key`，快照端点为 `/api/a-share/prices/snapshot?thscodes=...`，响应使用 `code/message/request_id/data` 信封。代码已接入该端点；历史指数行情已按完整文档接入；待网络/密钥实调。

已从完整接口文档确认并接入：指数历史 K 线 `/api/a-share-index/prices/historical`（仅单指数、1d、近5年）；交易日历 `/api/a-share/calendar/trading-days`（无参数、近一年）。沪深300映射为 `000300.SH`。

Mac 本机已成功调用扶摇指数历史 K 线：`000300.SH` 返回 26 条日线，HTTP 200、`code=0`，请求 ID `aa52bdca108c4788833d7e501a12802c`。字段标准化已覆盖日期、OHLC、成交量和成交额。
