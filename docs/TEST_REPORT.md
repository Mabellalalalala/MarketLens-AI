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
