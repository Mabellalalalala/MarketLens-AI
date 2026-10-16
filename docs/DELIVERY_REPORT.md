# MarketLens AI 交付报告

## 交付范围

MarketLens AI 是本地运行的 Evidence-grounded A 股市场研判 MVP。用户输入指数和研究区间后，系统通过扶摇真实数据完成确定性计算，生成 Market State、Contradiction Radar、Evidence Detail，并可使用 Ask MarketLens 基于当前研究上下文继续提问。

## 已交付能力

- 扶摇 REST 真实指数历史行情；
- 沪深300成分股快照与市场宽度 proxy；
- 沪深300 / 中证1000 Style Rotation；
- Volume + Turnover Trading Activity；
- Evidence Registry 和 Evidence Detail；
- Market State 确定性规则；
- Index/Breadth、Price/Activity、Large/Small-cap 矛盾雷达；
- DeepSeek 结构化研判与合规校验；
- Ask MarketLens 当前上下文问询；
- Research Snapshot JSON 持久化；
- MCP connectivity 与 iFinD `index_data`/`sector_data` 能力验证；
- 本地测试和异常降级。

## 数据状态

|维度|状态|说明|
|---|---|---|
|Market Structure|REAL|扶摇历史行情|
|Market Breadth|DERIVED|基于 REAL 成分股快照，非全A宽度|
|Style Rotation|DERIVED|沪深300与中证1000区间差|
|Trading Activity|REAL / DERIVED|Volume、Turnover及其比率|
|Valuation|LIMITED|当前估值快照，历史分位不可用|
|Sentiment|UNAVAILABLE|当前授权环境未验证可用情绪接口|
|Important Events|UNAVAILABLE|当前授权环境未提供事件数据|

## 启动

```bash
cd /Users/mabel/portfolio_adjustment/github_public/marketlens-ai
set -a
source .env
set +a
PYTHONPATH=src python3 scripts/build_snapshot.py
python3 scripts/validate_snapshot.py
PYTHONPATH=src python3 -m flask --app marketlens_ai.app run --host 127.0.0.1 --port 5055

Render production start command: `gunicorn --chdir src marketlens_ai.app:app --bind 0.0.0.0:$PORT`
```

浏览器访问 `http://127.0.0.1:5055`。

## 验证结果

```text
11 passed
```

Mac 本机已实际验证扶摇 HTTP 200 / business code 0，并成功调用 DeepSeek 结构化研判。MCP Streamable HTTP 连接成功，但当前 server 工具为 `index_data`、`sector_data`、`index_highfreq_quotes`，未替换 REST 主链路。

## 合规边界

产品解释市场状态、证据关系和判断更新条件，不预测涨跌，不推荐股票，不提供买卖、目标价、仓位或资产配置建议。所有关键数字必须关联 Evidence ID、来源、时点、单位和计算口径。

## 未交付范围

外网部署、实时 WebSocket、完整事件库、历史估值分位、自动交易、个股推荐和复杂用户系统不在本次本地 MVP 范围内。
