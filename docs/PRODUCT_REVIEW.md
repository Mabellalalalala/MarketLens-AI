# MarketLens AI｜产品与技术 Review 文档

## 1. 产品定位

MarketLens AI 是一个以证据为核心的 A 股市场状态研究助手。它帮助有基本金融知识的投资者和初级研究员理解：

- 当前市场发生了什么；
- 哪些真实数据支持这个判断；
- 哪些证据之间存在结构性矛盾；
- 当前判断有什么限制；
- 哪些新的客观条件出现后需要重新评估。

产品不预测涨跌，不推荐股票，不提供买卖、仓位或资产配置建议。

## 2. 用户主链路

```text
用户选择指数与区间/输入研究问题
        ↓
Research Request
        ↓
确定取数计划
        ↓
扶摇真实数据
        ↓
标准化与确定性计算
        ↓
Evidence Registry
        ↓
Market State
        ↓
Contradiction Radar
        ↓
DeepSeek 结构化解释
        ↓
Evidence Detail 与 Ask MarketLens
```

用户可以先研究“沪深300近20个交易日”，再继续询问：

- 为什么当前状态是这样？
- 指数和市场宽度是否分化？
- 大盘股和中小盘有什么差异？
- 哪些数据可能改变当前判断？

Ask MarketLens 只使用当前 Research Context，不重新让模型取数或搜索互联网。

## 3. 当前功能

### 3.1 Market Structure

使用扶摇指数历史 K 线，保存开盘价、最高价、最低价、收盘价、成交量和成交额。

已实现：

- 20 个交易日区间收益；
- 数据截至日期；
- 原始字段和计算方法；
- REAL 状态标记。

### 3.2 Market Breadth

当前使用沪深300成分股行情快照计算市场宽度 proxy，不宣称是完整 A 股宽度。

保存：

- 成分股总数；
- 有效快照数；
- 覆盖率；
- 上涨家数；
- 下跌家数；
- 平盘家数；
- 上涨占比。

计算：

```text
上涨占比 = 上涨家数 / 有效成分股快照数 × 100%
覆盖率 = 有效快照数 / 成分股总数 × 100%
```

状态为 `DERIVED`，方法说明为：

> Derived from REAL Fuyao constituent snapshots; constituent breadth is a proxy, not full A-share breadth.

### 3.3 Style Rotation

比较沪深300与中证1000的同区间收益。

计算：

```text
相对表现差 = 中证1000 20D 收益 - 沪深300 20D 收益
```

确定性规则：

```text
差值 > +2 个百分点 → Small/mid-cap leadership
差值 < -2 个百分点 → Large-cap leadership
其他 → Mixed
```

这是过去区间的相对表现描述，不是未来风格预测。

状态为 `DERIVED`。

### 3.4 Trading Activity

Trading Activity 只描述成交活跃度，不等同于完整 Liquidity。

原始数据：

- Volume：成交量；
- Turnover/Amount：成交额。

派生指标：

```text
Volume ratio = 最新成交量 / 前20日平均成交量
Amount ratio = 最新成交额 / 前20日平均成交额
```

确定性规则：

```text
ratio > 1.2   → Elevated
0.8–1.2       → Normal
ratio < 0.8   → Weak
```

状态拆分：

- 原始 Volume/Turnover：`REAL`；
- ratio 和活跃度等级：`DERIVED`。

### 3.5 Market State

Market State 由确定性规则生成，AI 不得自行改名或改变阈值。

可用状态包括：

- 广泛参与；
- 结构偏弱；
- 结构性分化；
- 信号混合；
- 数据不足。

当关键证据缺失时，系统不生成过度确定的市场结论，而是显示数据覆盖限制。

### 3.6 Contradiction Radar

只由代码确定性触发，AI 只负责解释。

当前规则：

1. **Index vs Breadth**

```text
指数收益明显为负 + 宽度仍然较高
或指数收益明显为正 + 宽度偏低
```

2. **Price vs Trading Activity**

```text
价格区间变化明显 + Volume/Amount ratio 偏弱
```

3. **Large-cap vs Small-cap**

```text
沪深300与中证1000相对表现差超过 2 个百分点
```

缺少任一必要证据时，结果为 `insufficient/not_evaluable`，不制造矛盾。

### 3.7 Evidence Detail

每条关键证据可查看：

- Evidence ID；
- Source；
- Provider；
- Endpoint 或工具；
- 原始字段；
- 数值；
- 单位；
- As of；
- Methodology；
- Status；
- Freshness；
- Coverage；
- Limitations。

### 3.8 Ask MarketLens

Ask MarketLens 是证据驱动的继续研究，不是开放式金融 Chatbot。

它接收：

- 当前 Market State；
- 当前有效 Evidence；
- 当前 Contradiction Radar；
- 数据质量与限制；
- 用户问题。

它可以解释证据关系和不确定性，但不能：

- 预测涨跌；
- 推荐股票；
- 给买卖建议；
- 给仓位建议；
- 给目标价；
- 自行搜索互联网；
- 自行调用 MCP；
- 创造不存在的数据或事件。

## 4. Status 语义

|Status|定义|
|---|---|
|REAL|原始数据直接来自真实授权数据源|
|DERIVED|基于 REAL 数据由确定性代码计算|
|LIMITED|数据存在，但历史长度、覆盖范围或口径有限|
|UNAVAILABLE|当前授权环境无法提供该能力|
|ERROR|本次调用实际失败|
|STALE|数据超过允许时效|

当前维度状态：

```text
Market Structure   REAL
Market Breadth     DERIVED
Style Rotation     DERIVED
Trading Activity   REAL / DERIVED
Valuation          LIMITED
Sentiment          UNAVAILABLE
Important Events   UNAVAILABLE
```

## 5. AI 与候选人的分工

### 候选人/产品经理主导

- 定义用户问题和产品范围；
- 规定不预测、不推荐、不提供仓位建议；
- 选择证据框架和状态标签；
- 确认 Market Breadth 是 proxy；
- 确认 Trading Activity 不等同于 Liquidity；
- 决定估值历史分位不可用时显示 LIMITED；
- 决定事件和情绪数据不可用时显示 UNAVAILABLE；
- 对 AI 结果进行人工复核和验收；
- 根据真实错误修正产品口径和 Prompt。

### Codex/工程实现

- 审计旧项目并建立独立项目；
- 连接扶摇 REST 与补充 MCP；
- 完成数据标准化、批量请求和错误处理；
- 实现确定性指标、状态和矛盾规则；
- 建立 Evidence Registry 和 Snapshot；
- 实现 DeepSeek 调用和 Validator；
- 实现 Web UI、测试和交付文档。

### DeepSeek 角色

DeepSeek 只做证据综合、主要矛盾归纳、不确定性解释、观察条件和继续研究引导。核心数字、阈值、状态和矛盾由后端确定性代码负责。

## 6. 数据架构

生产默认数据源：扶摇 REST。

```text
Fuyao REST / iFinD MCP 补充
        ↓
Normalization
        ↓
Deterministic Metrics
        ↓
Evidence Registry
        ↓
Market State / Contradiction Radar
        ↓
Research Snapshot
        ↓
Flask Web UI / DeepSeek / Ask MarketLens
```

Research Snapshot 保存在：

```text
data/snapshots/latest.json
```

Render 启动时如果不存在快照，会使用服务端环境变量尝试生成；失败时显式显示不可用，不依赖开发者本机文件。

## 7. 代码导航

|路径|职责|
|---|---|
|`src/marketlens_ai/app.py`|Flask app、网页路由和 API 路由|
|`src/marketlens_ai/core_research.py`|研究主链路编排|
|`src/marketlens_ai/providers/fuyao.py`|扶摇 REST Provider|
|`src/marketlens_ai/providers/mcp.py`|官方工具名约束的 MCP Provider|
|`src/marketlens_ai/providers/streamable_mcp.py`|Streamable HTTP MCP Client|
|`src/marketlens_ai/normalization.py`|iFinD MCP 表格标准化|
|`src/marketlens_ai/metrics.py`|收益、活跃度、风格和 Evidence 计算|
|`src/marketlens_ai/analysis.py`|Market State 和 Contradiction 基础规则|
|`src/marketlens_ai/ai.py`|DeepSeek 调用、Ask MarketLens 和合规 Validator|
|`scripts/build_snapshot.py`|生成 `latest.json`|
|`scripts/validate_snapshot.py`|校验 Snapshot schema 和 status|
|`scripts/test_official_mcp_config.py`|验证官方 MCP 配置和真实 schema|
|`scripts/render_start.sh`|Render 启动、快照 bootstrap 和 Gunicorn|
|`tests/`|确定性计算、Provider、AI 合规测试|
|`docs/`|审计、数据能力、AI、测试、验收和交付文档|

## 8. 题目要求映射

|题目要求|实现|
|---|---|
|真实数据主链路|扶摇 REST 已在 Mac 本机真实验证|
|事实/归纳/不确定性|结构化研究输出与 AI Prompt 契约|
|证据、时点、单位、口径|Evidence Registry 和 Evidence Detail|
|状态切换条件|watch conditions 与确定性状态规则|
|继续研究|Ask MarketLens、风格/宽度/活跃度路径|
|AI 使用记录|`docs/AI_USAGE_AND_VALIDATION.md`|
|测试说明|`docs/TEST_REPORT.md`|
|源代码与 README|GitHub 仓库与本 README|
|Web Demo|Render 部署版本；URL 由提交环境提供|

## 9. 已知边界与未做事项

- Market Breadth 是沪深300成分股 proxy，不是全 A 股宽度；
- Trading Activity 是 Volume/Turnover limited measure，不是完整流动性；
- 估值当前只有 snapshot，历史分位不可用；
- Sentiment 当前授权环境未验证可用，显示 UNAVAILABLE；
- Important Events 当前授权环境未提供，显示 UNAVAILABLE；
- MCP 已完成连接和能力验证，但不替换已验证的 REST 主链路；
- 未实现自动交易、个股推荐、仓位优化和复杂预测模型；
- 视频演示不纳入本次交付。
