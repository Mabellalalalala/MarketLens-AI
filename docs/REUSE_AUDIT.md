# 旧项目复用审计

旧项目为当前父目录 `ai-market-monitor`（本地目录名为 github_public）。审计确认：`data_fetcher.py` 全部调用 Tushare；`market_temperature.py`、`sector_rotation.py` 依赖该数据层及全局 `pro`；`research_engine.py` 混合取数、计算和 LLM 编排；`llm_client.py` 是 requests 版 DeepSeek 客户端；`app.py` 内含明确虚构的 `DEMO_REPORT`。

|旧路径|新路径|处理|原因/验证|
|---|---|---|---|
|data_fetcher.py|providers/fuyao.py, providers/ifind.py|重写|旧 Tushare 不得成为主链路；扶摇接口待授权验证|
|market_temperature.py|metrics.py|重写最小纯函数|先移除 Tushare 全局耦合，保留可复核计算思想|
|sector_rotation.py|待迁移|暂不采用|依赖大量未验证 Tushare 行业字段|
|llm_client.py|待迁移|暂不复制|先完成真实数据和 evidence 校验，避免旧自由文本输出进入 MVP|
|app.py/templates|app.py/templates/index.html|重写|移除虚构演示数据，建立真实失败可见的研究入口|
|portfolio/run_daily|无|隐藏|与本题市场大势研判无关|
