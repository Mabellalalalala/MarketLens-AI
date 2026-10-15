# 测试报告

- `PYTHONPATH=src pytest -q tests`：覆盖区间收益计算、缺失数据、状态分类。
- iFinD MCP：已实际调用 `index_data`，因 DNS 解析失败返回 ConnectionError；记录于 DATA_CAPABILITY_MATRIX。
- 主链路真实行情：未通过，原因是扶摇凭据/endpoint 未配置，iFinD 网络不可达。

## 本机真实验证命令

在已配置 `FUYAO_API_KEY` 的 Mac 终端运行：

```bash
cd /Users/mabel/portfolio_adjustment/github_public/marketlens-ai
python3 scripts/verify_fuyao.py
```

脚本输出 HTTP 状态、业务 `code`、`request_id`、数据时间戳、条数、首尾字段。Codex 沙箱本次真实请求返回 HTTP 200 但业务 `code=2003`、`message=Missing X-api-key`，原因是该沙箱进程没有密钥环境变量；这不能代表接口失败。

## Mac 本机真实成功记录（PM 提供输出）

- 请求：`GET https://fuyao.aicubes.cn/api/a-share-index/prices/historical`
- 参数：`thscode=000300.SH`、`interval=1d`、动态 45 日窗口
- HTTP 状态：200
- 业务状态：`code=0`，`message=success`
- `request_id`：`aa52bdca108c4788833d7e501a12802c`
- 数据时间戳：`1791993600000`
- 返回条数：26
- 已确认字段：`date_ms`、`open_price`、`high_price`、`low_price`、`close_price`、`volume`、`turnover`
- 结论：扶摇真实指数历史行情主链路已完成首次成功验证；Codex 沙箱此前的失败仅是密钥未注入。
