# 测试报告

- `PYTHONPATH=src pytest -q tests`：覆盖区间收益计算、缺失数据、状态分类。
- iFinD MCP：已实际调用 `index_data`，因 DNS 解析失败返回 ConnectionError；记录于 DATA_CAPABILITY_MATRIX。
- 主链路真实行情：未通过，原因是扶摇凭据/endpoint 未配置，iFinD 网络不可达。
