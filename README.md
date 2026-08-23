# Option Analyze Agent

一个面向美股期权链分析的单 Agent 应用。它从 OptionCharts 获取期权链数据，使用确定性代码计算 GEX、DEX、OI 与 Max Pain，再由 LLM 将结果解释为自然语言回复。

当前版本为 **V3.0**：在 LangGraph V2 的状态图、记忆和缓存基础上，加入了原生 LLM Tool Calling、FastAPI 服务、Web/桌面界面、会话持久化和本地结构化 Trace。

> 仅供学习与研究使用，不构成投资建议。外部市场数据源可能延迟、不可用或发生结构变化。

## 功能

- 抓取到期日信息和期权链 HTML，并解析为统一的 `OptionChainResult`。
- 计算 GEX、DEX、OI 与 Max Pain；指标计算由确定性 Python 代码完成。
- 使用 LLM 原生 Tool Calling 决定是否调用 `run_option_analysis`。
- 对工具参数进行 JSON 解析、白名单校验和业务校验，模型不能直接调用数据源。
- 识别部分自然语言日期，如“本周五”“下周五”“今天”“明天”。
- 支持追问解释：当已有分析结果仍在五分钟新鲜期内，可直接基于现有上下文回答。
- 使用 `ticker + expiration` 作为键，在进程内缓存期权链五分钟；用户明确要求更新时绕过缓存。
- 使用 LangGraph SQLite Checkpointer 保存会话 State、短期记忆和摘要记忆。
- 使用独立 SQLite 数据库存储网页侧会话列表、标题和完整展示历史。
- 提供 FastAPI 接口、浏览器聊天页面与 PyWebView 本地桌面端。
- 将一次请求中的决策、缓存、抓取、计算、回答和记忆步骤写入 JSONL Trace。
- 将外部数据源超时、连接失败和非成功 HTTP 响应转换为用户可读提示，同时保留诊断日志。

## 架构

```text
Web / Desktop / CLI
        |
        v
 FastAPI POST /chat
        |
        | thread_id + trace_id
        v
 LangGraph StateGraph
        |
        +--> agent_decide_node
        |       |
        |       +--> direct_answer_node
        |       |
        |       +--> execute_tool_call_node
        |                 |
        |                 v
        |           OptionToolExecutor
        |                 |
        |                 v
        |           AnalysisRunner
        |                 |
        |                 +--> OptionChainCache
        |                 +--> OptionCharts Client -> Parser
        |                 +--> GEX / DEX / OI / Max Pain Tools
        |
        +--> generate_answer_node
        +--> update_short_term_memory_node
        +--> summarize_conversation_node (when required)
        |
        v
 ChatResponse + SQLite conversation history + JSONL trace
```

### 模块边界

```text
agent/          LLM 调用、Tool Schema、Tool Executor、结果解释
analysis/       GEX、DEX、OI、Max Pain 的确定性计算
api/            FastAPI 路由、生命周期和 API Contracts
cache/          五分钟 OptionChainResult 内存缓存
core/           Runtime、Runner、校验、异常、Checkpoint 与 Trace
data/           浏览器会话、OptionCharts Client、HTML Parser
graph/          LangGraph State、Nodes、Routing 和 Graph 装配
memory/         本地 SQLite 会话与 Checkpoint 数据库
schemas/        跨层使用的数据结构
tools/          期权链、市场时间、日期解析与指标工具
web/            HTML、CSS、JavaScript 聊天界面
test/           离线单元测试与集成/冒烟测试脚本
desktop_app.py  PyWebView 桌面启动器
```

## 核心请求流程

1. 前端将用户输入和 `thread_id` 发送到 `POST /chat`。
2. API 为本轮生成 `trace_id`，并调用带 SQLite Checkpointer 的 LangGraph。
3. Agent 读取对话状态、摘要和分析新鲜度，决定直接回答或发起 Tool Call。
4. 若调用工具，`OptionToolExecutor` 校验模型生成的 JSON 参数。
5. `AnalysisRunner` 先查询五分钟缓存；未命中或强制刷新时再获取、解析期权链。
6. 选择的指标工具计算结果，`ResultFormatter` 生成受控分析上下文。
7. LLM 只能基于工具返回的上下文生成最终说明。
8. 图更新短期记忆；达到阈值时摘要旧消息。网页历史另外写入 `conversations.db`。

## 环境要求

- Python 3.12+
- DeepSeek API Key（通过 OpenAI Python SDK 兼容接口调用）
- Playwright Chromium 浏览器二进制

安装：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

在项目根目录创建 `.env`：

```env
DEEPSEEK_API_KEY=your_api_key_here
```

不要提交 `.env`、`venv/`、`logs/` 或本地 SQLite 数据库。

## 启动

### 桌面端（推荐）

```powershell
python -m desktop_app
```

桌面端会启动本地 FastAPI 服务并打开 PyWebView 窗口。

### 浏览器 / API 开发模式

```powershell
uvicorn api.app:app
```

打开：

```text
http://127.0.0.1:8000/
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### CLI 版本

```powershell
python -m run_graph_agent
```

输入 `exit`、`quit` 或 `退出` 可结束 CLI。

## 示例请求

```text
分析 TSLA 2026-08-21 的 GEX 和 DEX
分析特斯拉下周五的信息
再帮我看一下 OI 并分析
再详细解释一下
更新一下数据，再次分析
```

## 状态、记忆与缓存

### LangGraph 会话状态

LangGraph Checkpoint 默认保存在：

```text
memory/option_agent_checkpoints.db
```

同一 `thread_id` 可以恢复最近的分析上下文、短期对话历史、运行摘要和最近一次成功请求。

旧消息达到摘要条件时，系统会压缩历史并保留最近原始消息，减少后续 LLM 上下文长度。

### 网页会话历史

网页侧的会话标题与完整展示消息保存在：

```text
memory/conversations.db
```

它服务于左侧会话列表和历史展示；并不意味着所有历史消息都会原样发送给 LLM。

### 期权链缓存与新鲜度

- 缓存键：`ticker + expiration`
- TTL：5 分钟
- `cache hit`：直接复用已解析的期权链，不再请求或解析 HTML。
- `cache miss`：重新抓取并解析数据。
- `cache bypass`：用户明确要求刷新时忽略缓存。
- 分析上下文超过五分钟后，系统不会把旧市场数据当作当前数据直接回答。

缓存仅存在内存中，Python 进程退出后自动清空。

## Trace 与故障诊断

本地 Trace 写入：

```text
logs/option_agent.jsonl
```

每次聊天请求有独立 `trace_id`。常见事件包括：

- `chat_started` / `chat_completed`
- `agent_decision_started` / `agent_decision_completed`
- `option_chain_cache_hit` / `option_chain_cache_miss` / `option_chain_cache_bypassed`
- `option_chain_fetch_started` / `option_chain_fetch_completed`
- `analysis_calculation_started` / `analysis_calculation_completed`
- `answer_generation_started` / `answer_generation_completed`
- `short_term_memory_updated`
- `conversation_summary_completed`
- `chat_data_source_unavailable`

查看最近日志：

```powershell
Get-Content .\logs\option_agent.jsonl -Tail 50
```

## 测试

以下测试不需要 DeepSeek API、浏览器 Cookie 或外部期权链请求：

```powershell
python -m test.test_option_chain_cache
python -m test.test_option_chain_tool_cache
python -m test.test_graph_routing
python -m test.test_natural_date_resolver
python -m test.test_optionchart_client_errors
```

运行语法检查：

```powershell
python -m py_compile core\exceptions.py data\optionchart_client.py core\trace.py api\app.py
```

项目中另有需要真实 API、浏览器或市场数据源的集成测试；运行它们会使用本机配置的外部服务。

## 当前限制与后续方向

- 当前是单用户本地应用；`graph_lock` 会串行执行聊天请求。
- SQLite、内存缓存和 JSONL Trace 适合学习与本地运行，不适合多人生产环境。
- OptionCharts 是外部依赖，可能出现验证码、限流、HTTP 错误或 HTML 结构变化。
- 项目尚未实现用户认证、多租户隔离、Redis、PostgreSQL、集中监控或重试策略。
- 当前只有一个聚合分析 Tool；未实现 MCP、Skills、多 Agent 或 RAG。
- 本项目未将实时市场分析向量化为 RAG 记忆，避免旧行情被检索后误认为实时数据。

面向公司内部多用户部署时，下一步应是：中心化 FastAPI 服务、认证与权限、PostgreSQL 会话存储、Redis 缓存、受授权的数据源和集中可观测性。

