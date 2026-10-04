# 《深入理解 AI Agent：设计原理与工程实践》学习档案

- 作者：李博杰（Pine AI 首席科学家），版本 2.0
- 核心公式：**Agent = LLM + 上下文 + 工具**（大脑 + 眼睛 + 手脚）
- 本地教程路径：`D:\ai-agent-book-main`
  - 中文正文：`D:\ai-agent-book-main\book\`（introduction.md、chapter1.md~chapter10.md、afterword.md）
  - 实验代码：`D:\ai-agent-book-main\chapter1\` ~ `chapter10\`，每章 README.md 是实验索引
  - 共 109 个实验；✅可运行 / 📖复现指南（需 clone 外部仓库）/ 🚧设计文档
- 环境：Python 3.11–3.13；按章装依赖 `python -m pip install -e ".[chN]"`（在仓库根目录）；API Key 配置见根目录 `.env.example`
- 开始日期：2026-09-14

---

## 共学营路线（2026-09-23 按老师最新通知更新；节奏：学习章节 → 跑通所有可运行实验 → 独立打卡）

**打卡门槛**：老师规定每个 Task「至少跑通 1 个实验」；我们自定标准为**教程标 ✅ 且本机/预算可行的实验全部跑通**，📖 类读复现指南（能离线验证的验证），🚧 类读懂设计即可。

| 阶段 | 内容 | 章节 | 截止（北京时间 03:00） | 状态 |
|---|---|---|---|---|
| Task 0 | 基础与环境：AI Agent 简介、环境配置、跑通基础实验 | Ch.1 | 2026-09-17 | ✅ 完成（2026-09-15 打卡） |
| Task 1 | 上下文工程 | Ch.2 | 2026-09-20 | ✅ 完成（2026-09-19 合并打卡已上传） |
| Task 2 | 用户记忆和知识库 | Ch.3 | 2026-09-23 | ✅ 全部 10 个实验跑通；打卡笔记已提交（2026-09-23，无截图，说明主要实验上次已提交），等老师反馈 |
| Task 3 | Tools（Tool Calling · MCP） | Ch.4 | 2026-09-26（比原计划 +3 天） | ✅ 已提交（2026-09-25，6 个实验全部跑通） |
| Task 4 | Coding Agent 与通用 Agent | Ch.5~6 | 2026-09-29（比原计划 +3 天） | ✅ 完成（2026-09-27）：Ch.5 核心主线 + Ch.6 异步核心 6-2，3 个实验 |
| Task 5 | 多 Agent 协作（范围确认 = 仅 Ch.10，Ch.9 不含） | Ch.10 | 2026-10-02 | ✅ 完成并已提交（2026-10-03 用户确认通过，无反馈问题） |
| Task 7（选做，不计入打卡） | 补齐 Ch.7~9：5 个离线实验 + 9-3 真实 API 闭环 | Ch.7~9 | 2026-10-03 完成 | ✅ 选做完成，6 个实验全部跑通 |
| Task 6 | 共学总结（五选一）：学习总结 / Mini Agent Demo / 知识地图 / 项目改造 / Issue 或 PR；须独立完成 | 全书 | 2026-10-05（周一）03:00 | ✅ 完成（2026-10-04 一天做完前三选：学习总结＋Mini Agent＋知识地图），待提交 |

**产物区文件夹与新 Task 编号的对应**（2026-09-23 重排）：
- `task0/` = Ch.1；`task1/` = Ch.2 实验产物；`task2/` = Ch.3 实验产物（2026-09-23 新建，Ch.3 全部实验在此；早先 3-6/3-8 产物仍在 task1/）
- 老师 Task 2 若需单独打卡，笔记放 `task2/打卡笔记.md`（引用 task1/task2 的实验产物，实验不重跑）
- 此后文件夹按老师编号：Ch.4 → `task3/`，Ch.5~6 → `task4/`，多 Agent → `task5/`
- 2026-10-03 自学加餐：Ch.7~9 补学实验 → `task7/`（六个子目录：7-public-health、7-elo、8-qlearning、9-1-verifier、9-3-prompt-opt、9-9-longitudinal）；编号跳过 6 是为避免与老师 Task 6 混淆

---

## 全书 10 章结构

### 第一部分：如何构建 Agent（Ch.1–6）

1. **AI Agent 入门**（4 实验）：核心公式；上下文五组件（系统提示词、工具定义、用户消息、模型回复、工具结果）；ReAct 循环（思考→行动→观察）；轨迹 = 静态前缀 + 动态消息历史；Harness；从工作流到自主 Agent
2. **上下文工程**（10 实验，全书最关键）：消息结构与核心循环、KV Cache、提示工程与提示注入攻防、Agent Skills 按需加载、状态栏、上下文压缩
3. **用户记忆和知识库**（12 实验）：用户记忆四种策略、RAG 完整技术栈（文本搜索、排序）、结构化索引、知识图谱、Agentic RAG、多模态记忆
4. **工具**（5 实验）：MCP 协议、五类工具（感知/执行/协作/事件触发/用户沟通）、多模态感知三路线、执行工具安全机制
5. **Coding Agent 与通用 Agent**（16 实验）：代码是"能创造新工具的工具"；以 OpenClaw 架构为主线；辅助思考、知识库、动态造工具、Agent 自举
6. **交互：观察与动作空间的扩展**（14 实验）：异步与事件驱动、语音交互（实时尺度）、Computer Use（GUI）、机器人操作（物理世界）；共享原语：唤醒、安全点、取消、抢占、快慢路径分离

### 第二部分：如何提升 Agent 能力（Ch.7–10）

7. **Agent 的评估**（14 实验）：评估环境（工具调用型/人机交互型/仿真）、数据集设计、LLM-as-a-Judge、统计显著性、评估驱动选型、改进闭环
8. **模型后训练**（19 实验，最重，多需 GPU）：预训练/SFT/RL 三阶段；核心论点"SFT 记忆、RL 泛化""数据与环境比算法重要"；奖励设计（二元→过程奖励→验证路径惩罚）；单轮/多轮 RL；样本效率
9. **Agent 的持续进化**（9 实验）：学习信号（环境结果、过程规则、LLM Rubric）；四种更新载体（知识文档、Prompt/Skills、程序/Harness、模型参数）；验证、灰度、回滚
10. **多 Agent 协作**（6 实验）：分类框架（上下文共享/独立 × 对等/管理者/去中心化）、翻译 Agent、电话+电脑协同、Agent 社会与经济

---

## 各 Task 推荐上手实验（已核对本地目录均存在）

- **Task 0**：`chapter1/context/`（实验 1-1 ★★ 上下文消融实验，5 种模式：full / no_history / no_reasoning / no_tool_calls / no_tool_results）
- **Task 1**（Ch.2，已完成）：`chapter2/kv-cache/`、`chapter2/prompt-engineering/`、`chapter2/context-compression/`
- **Task 2**（Ch.3，10 个实验全部完成）：user-memory（3-1/3-2 memobase+mem0）、dense-embedding 3-4、retrieval-pipeline 3-6、raptor 3-7、agentic-rag 3-8/3-9、contextual 3-10、dual-memory 3-11、structured-extraction 3-12
- **Task 3**（Ch.4）：`chapter4/execution-tools/`、`chapter4/active-tool-discovery/`、`chapter4/active-tool-selection/`、`chapter4/collaboration-tools/`（MCP 散见各项目）
- **Task 4**（Ch.5~6）：`chapter5/coding-agent/`、`chapter5/agent-creator/`、`chapter6/async-agent/`；`chapter6/claude-computer-use-native/` 等语音/机器人实验有硬件或外部仓库门槛，按 📖 档处理
- **自学**（Ch.7~8，不打卡）：`chapter7/model-benchmark/`、`chapter7/elo-leaderboard/` 纯 API 可跑；`chapter8/` 训练实验多需 GPU，读 README + 正文即可
- **Task 5**（Ch.9~10 待确认）：`chapter9/prompt-auto-optimization/`、`chapter9/self-modifying-agent/`、`chapter10/book-translation/`、`chapter10/parallel-web-research/`

---

## 环境与运行约定

- **教程代码**：`D:\ai-agent-book-main`（zip 下载，无 .git）；运行时工作目录必须是项目根目录（代码用相对路径找 fixtures/、agentbook 包），命令一律 `uv run python ...`（uv 自带 CPython 3.12.13，系统 3.14 不兼容）
- **学习产物区**：`d:\ai-agent-book\task0\`、`task1\`……按打卡 Task 编号直接建在工作区根目录（实验产物跑完从项目根目录归档到这里，避免污染项目；.gitignore 本就忽略这些文件）
- **笔记/作业**：写在 `d:\ai-agent-book` 工作区；代码实验在教程目录跑
- 每章依赖按需安装：`uv sync --locked --extra chN`
- API：DeepSeek 按量付费，Key 在教程根目录 `.env`（load_dotenv 不向上递归，.env 必须放根目录），运行必须显式 `--provider deepseek`；火山 Coding Plan 禁止用于实验（/api/v3 按量扣费，/api/coding/v3 违反套餐条款）

## Task 0 执行清单（截止 2026-09-17 03:00）

1. [x] 读完 `book/chapter1.md`（2026-09-15，用户表示第一课内容可理解）
2. [x] Python 环境：系统 3.14.3 不兼容（要求 <3.14），uv 已用自带 CPython 3.12.13 在 `.venv` 建环境
3. [x] 已执行 `uv sync --locked --extra ch1`（58 个包安装成功，2026-09-14）；运行一律用 `uv run python ...`
4. [x] API 方案已定（2026-09-14）：**不用火山 Coding Plan**——教程默认端点 `ark.../api/v3` 是按量付费（曾被扣费）；Coding Plan 必须用 `/api/coding/v3` + 套餐内模型，且官方条款规定套餐仅限 AI 编程工具、禁止 API 调用（有封禁风险）。最终选 **DeepSeek 开放平台按量付费**（platform.deepseek.com）
5. [x] Key 已填入仓库根目录 `.env` 的 `DEEPSEEK_API_KEY=`（2026-09-14 已保存，load_dotenv 不向上递归，必须放根目录/运行目录）
6. [x] 单次任务跑通（2026-09-14）：模型 deepseek-v4-flash，3 轮迭代 4 次工具调用（3 次并行汇率换算 + 1 次计算），结果正确；输出详情存 task_result_full.json
7. [x] 消融实验跑通（2026-09-14）：注意默认单 case 的 PDF 链接是 GitHub 国内打不开（已浪费少量 token，及时停止）；改用 `--cases 2` 跑两个纯离线财务任务（5 模式 × 2 任务 = 10 组）。结果：full/no_reasoning 均完成；no_history 两组都跑满 10 轮 30+ 次工具调用无答案；no_tool_calls/no_tool_results 虽"完成"但 grounding_verdict=ungrounded（编造数字）。报告/数据/图表已归档至 `d:\ai-agent-book\task0\`（ablation_study_report.md、ablation_results.json、ablation_study_results.png、task_result_full.json）
8. [~] 按营地要求打卡（截止 2026-09-17 03:00）：草稿已写好 `d:\ai-agent-book\task0\打卡笔记.md`（2026-09-15），待用户复制到打卡平台提交

## Task 1 执行清单（截止 2026-09-20 03:00）

目标：上下文窗口与组织、短期上下文 vs 长期记忆、RAG 作用、至少 1 个实验（已超额完成 2 个实验 + 扩展对比）

1. [x] 精读 chapter2.md（2026-09-19 串讲）：静态前缀+动态轨迹、KV Cache 三铁律、提示工程消融、Skills 渐进披露、状态栏、上下文压缩
2. [x] 精读 chapter3.md（2026-09-19 串讲）：三层评估框架、记忆三套分类、RAG 流水线（分块/稠密/BM25/RRF/重排）、Agentic RAG、contextual retrieval、双层记忆
3. [x] 环境：SiliconFlow key 已入根目录 .env（`SILICONFLOW_API_KEY`，账户 ¥16 代金券）。坑：① ch3 整包 `uv sync --extra ch3` 在 Windows 失败（annoy 无预编译 wheel，需 MSVC），改用 `uv pip install rank-bm25 jieba openai python-dotenv colorama rich pyyaml` 只装所需；② 书默认模型 Qwen/Qwen3-235B-A22B-Thinking-2507 已在平台下架（Model disabled 30003），验证后改用 **Qwen/Qwen3.5-35B-A3B**（¥0.4/¥3.2 per M token）
4. [x] 实验 3-6 retrieval-pipeline（2026-09-19，纯本地零 API 费）：`evaluate.py --no-dense --no-rerank` 得 BM25 Recall@3=0.833/MRR=0.792；稠密模型 MiniLM-L6-v2（90MB，用 HF_ENDPOINT=https://hf-mirror.com 镜像下载）：Dense 1.0/0.917，Hybrid-RRF 全部满分 1.0，Weighted 0.958。跳过 1.1GB 重排模型。产物 task1/3-6_bm25_result.json、3-6_hybrid_result.json
5. [x] 实验 3-1 user-memory（2026-09-19，SiliconFlow 代金券，花费约几分钱）：demo 模式写死 user_id=demo_user（--user 不生效），json_cards 与 notes 各跑一次。结论：notes=5 条平铺句子 1922B（名字重复、无独立身份字段、不能原地更新）；json_cards=两层树 1445B（独立 identity、每叶子 source+时间戳、可精确覆盖更新）。产物 task1/3-1_user_memory_{notes,json_cards}/
6. [x] 【已完成 2026-09-19 波谷补跑】3-8 agentic-rag：① 离线 `compare_offline.py`（零费用，21372 法条分块）整体证据召回 48%→100%、复杂题 8%→100%、平均检索 1.0→1.3 次，产物 3-8_offline_compare.json；② DeepSeek 在线 compare（默认模型 deepseek-reasoner，4 轮 16 次检索，约几分钱）：同一多跳题"醉酒过失致人重伤+盗窃前科"，非 agentic 单次检索只捞到不适用的 §115/§234 后放弃，agentic 分解检索找到 §18 醉酒应负刑责/§235 过失致人重伤三年以下并分层作答。注意 compare 模式不写 JSON，用控制台重定向 txt 归档
7. [x] 【已完成 2026-09-19】2-10 context-compression（DeepSeek-v4-flash + 无 Serper 的 mock 数据）：128K 预算 6 轮 no_compression=24,087 tokens vs context_aware=7,136（省 70%），压缩比 3.6%（书实测 3.0%）；mock 页面太小不溢出，另写临时脚本把 CONTEXT_WINDOW_SIZE 收紧到 3K：无压缩第 4 轮 last_prompt 2635 撞 80% 阈值溢出终止，context_aware 同轮数零溢出（1909 tokens）；边界发现：3K+10 轮 context_aware 也溢出 4 次（工具定义+压缩摘要有固定下限）。mock 数据只有 4 个创始人导致两策略都未给 final answer，教学上以 token/溢出指标为准。临时脚本已删，产物 2-10_mock_compare.json、2-10_small_window*.json
8. [x] 打卡笔记已起草：task1/打卡笔记.md（含 Context/Memory/RAG 三者关系专节，老师指定提交要求）+ 150 字心得体会（对话框给出版本）。2026-09-19 晚重跑实验补齐 4 张终端截图：3-6 evaluate 表、3-1 json_cards demo（先删 data/conversations/demo_user_history.json 与 data/memories/demo_user_memory.json）、3-8 compare --no-verbose、2-10（可复用脚本 task1/run_2-10_compare.py，在仓库根目录设 LLM_PROVIDER=deepseek/MODEL_NAME/MAX_ITERATIONS=6 后运行）。打卡已上传（2026-09-19），Task 1 全部完成

## Task 2 执行清单（截止 2026-09-23 03:00）

目标：Ch.3 用户记忆与知识库，教程标 ✅ 的实验全部跑通（2026-09-23 一天内完成剩余 7 个）

1. [x] 已有实验（随旧 Task 1）：3-1 user-memory、3-6 retrieval-pipeline、3-8 agentic-rag（产物在 task1/）
2. [x] 3-3 记忆策略演示、3-5 记忆评测、3-7 RAPTOR/GraphRAG 离线 demo（此前完成，产物 task2/）
3. [x] 3-9 Agentic RAG offline-demo、3-10 上下文感知检索对比、3-11 双层记忆 compare（此前完成，产物 task2/）
4. [x] 3-4 dense-embedding（2026-09-23）：annoy/hnswlib 在 Win 无 wheel，改用 **numpy 手写 RPForest**（50 树复刻 ANNOY）+ **usearch**（HNSW，有 Win wheel）；向量走 SiliconFlow bge-m3，语料口径同官方 benchmark。结果 recall@10：RPForest 0.99 / HNSW 1.0；HNSW 构建快 14 倍、体积小 15 倍、增量插入 3.86ms 无需重建（RPForest 增量 114ms 需全量重建）。产物 task2/bench_3-4.py、3-4_benchmark.json
5. [x] 3-2 memobase 手写版（2026-09-23）：改 agent.py 把记忆上下文并入唯一 system 消息（SiliconFlow 不允许多 system），demo 三组场景全部 200 OK。产物 task2/3-2_memobase_demo.txt
6. [x] 3-12 结构化知识抽取（2026-09-23）：用官方 66 案合成集跑通四段流水线（因子发现→JSON 抽取 6 并发 45s→KMeans 聚 10 个案件原型→对话式建议 Agent），匹配到入户盗窃原型#5（15 例，刑期中位 49 月）。与官方 420 案 campaign 的差别已在结果中说明。产物 task2/run_3-12.py、3-12_summary.json
7. [x] 3-2 mem0（2026-09-23）：真实 mem0ai 2.x，LLM=Qwen2.5-14B、embedder=bge-m3、本地 Qdrant。三个坑：`embedding_model_dims` 默认 1536（显式设 1024）、`history_db_path` 默认在用户目录被沙箱拦（指向 task2/data/）、新版 search/get_all 必须用 `filters={"user_id":...}`。结果：两条事实抽取正确，检索正确召回「搬到上海」。产物 task2/run_3-2_mem0.py、3-2_mem0_result.json
8. [x] 打卡笔记已起草（2026-09-23，用户确认需单独打卡）：task2/打卡笔记.md（六段式，覆盖全部 10 个实验），待用户复制提交

## Task 3 执行清单（截止 2026-09-26 03:00）

目标：Ch.4 Tools，章 README 索引的 6 个实验全部跑通（2026-09-25 完成）；LLM 走 SiliconFlow（代金券），离线实验零费用

1. [x] **4-1 active-tool-discovery**（离线，8 任务×3 策略）：全量注入 8/8 @11,630 tok；检索预筛选 4/8 @~1,030 tok（汇率+天气等多步任务第二领域系统性漏召回）；主动发现 8/8 @~974 tok，省 11.9 倍。产物 task3/4-1_offline*
2. [x] **active-tool-selection**（离线）：retrieval top-5 保 100% 召回、省 98.7%（40,258→522 tok）；扩展曲线 35→400 工具时 all-tools 线性涨到 40,258，retrieval 恒定 ~522。产物 task3/selection_*
3. [x] **4-2 perception-tools**：MCP **版本分裂**——本项目用 MCP v2（mcp 2.2.0，协议 2026-07-28，独立 venv `.venv-mcp2`）；127 工具 smoke 通；离线 pytest 34 passed（2 个符号链接用例受 Windows 非管理员特权限制）；真实 API：北京天气、100 USD=672 CNY、PubChem 14 passed + aspirin 实测。产物 task3/4-2_*
4. [x] **4-4 execution-tools**（MCP v1+fastmcp）：7 步全通（语法拦截、代码执行、shell、1000→102 行长输出截断落盘、危险命令 fail-safe）。**跨平台修复** multilang_executor.py（硬编码 python3/`/bin/bash` → sys.executable+平台分支）与 cli.py 步骤 5（Unix wc → PowerShell，读 $env:WORKSPACE_DIR 避引号）。产物 task3/4-4_demo_run.txt
5. [x] **4-5 collaboration-tools**（MCP v1）：离线 demo + pytest 63 passed；真实 SiliconFlow：sync spawn 正确批准；双策略对比 minimal 86 上下文/267 prompt tok vs llm_generated 125 上下文+494 额外合成/300 prompt tok，均不泄漏卡号；async、HITL 批准/超时、通知 preflight 验证。产物 task3/4-5_*
6. [x] **4-3 multimodal-agent**：离线 create_sample.py 生成 chart（精确季度数字仅在柱状图）+PDF 报告；最小适配 config.py/agent.py 支持 OPENAI_BASE_URL 与 qwen-vl 模型配置（原硬编码 OpenAI 端点与 gpt-5.6-luna 模型名）；SiliconFlow **Qwen3-VL-8B-Instruct** 三范式全部正确读出 Q4=$180M——native、extract-to-text（caption 恰好保留了数值）、extract+tools；发现 function-calling 幻觉文件名问题（给绝对路径规避）；PDF 原生仅 Gemini 路径（受限），改用 pypdf 抽文本+内嵌图混合范式跑通；pytest 19 passed。产物 task3/4-3_*
7. [x] 打卡：task3/打卡笔记.md 已提交（2026-09-25）；4 个适配 py 已归档 task3/ 根目录

**网络环境结论（打卡素材）**：Open-Meteo/汇率 API/PubChem 可达；arxiv(406)/wikipedia/Yahoo(403)/youtube 受限；本机无代理端口开放——境外站点不可达属环境问题非代码问题。

## Task 5 执行清单（截止 2026-10-02 03:00）

目标：Ch.10 多 Agent 协作，三个 ✅ 实验全部跑通（2026-10-01 完成）；LLM 走 SiliconFlow Qwen/Qwen3-8B（代金券），Tavily 用用户指定 key

1. [x] **10-2 book-translation**（管理者模式主线）：14 测试通过 + dry-run；真实双臂对比 4 章小书。Manager 上下文峰值 883 tok vs 单 Agent 2101（2.4 倍）；指定术语遵从率 100% vs 27%；术语内部一致率 89% vs 78%；总 token 管理者 14672（四 Agent 合计）vs 单 Agent 8293——多臂总 token 更高，换来的是上下文峰值与一致性。产物 task5/10-2/
2. [x] **10-1 multi-role-transfer**：14 测试通过；demo 自主移交链 triage→research→coding→writing（3 次移交）跑通，注：本次 Tavily 返回错误销量（11.9 万辆，实际 352 万），机制正常、数据质量问题如实记录；配对对比 3 任务×3 trials：**Skill 3/9 通过 vs Transfer 0/9**，Skill 平均 8.3 次调用 vs Transfer 4.3，Transfer 移交后无法收敛收尾。产物 task5/10-1/local_qwen3_8b.json
3. [x] **10-4 parallel-web-research**（Starter）：13 测试通过；真实 Chromium 跑 Stanford 站点——not_found 场景（医/法/教育学院）并行 23.5s vs 串行 30.3s，加速 1.285；found 场景（profiles 页命中）单次 terminate 广播级联终止，并行 39.7s vs 49.9s，加速 1.257；6+6 context 全部关闭。注：profiles 页是另一位同名 人（财务岗），证据约束原样保留渲染文本无幻觉。产物 task5/10-4/
4. [x] 打卡笔记已起草并**提交通过**（2026-10-03 用户确认：老师无问题反馈）

## Task 7 执行清单（选做 · 自学加餐，2026-10-03 一天完成）

目标：补齐 Ch.7 评估、Ch.8 后训练、Ch.9 持续进化三章中本机可行的实验。筛选自三章共 39 个编号实验：Ch.8 除 Q-learning 外全部需 GPU；9-6 需 Docker；9-2 需 tau2；9-5 内嵌整个 browser-use；9-8 Hermes 链路过长；7-1/7-2 需 clone 外部基准；7-13/14 需 GPU/模拟器。最终 5 个离线零费用 + 9-3 真实 API

1. [x] **7-public-health**（Ch.7 评估方法综合，离线）：demo 30/30 满分（5 任务各 6/6），pytest 19 passed。产物 task7/7-public-health/
2. [x] **7-elo**（Bradley-Terry/Elo 排行榜，离线）：5000 场模拟对战（8 模型、平局率 0.1、seed 42），恢复排序与真值完全一致（gpt-4 1127.5 第一…vicuna-13b 856.4 末位），bootstrap 100 次，42 passed。产物 task7/7-elo/
3. [x] **8-qlearning**（Ch.8 唯一不需 GPU 的 RL 实验）：1 万局学习曲线与官方一致（1000 局 0.3%→6000 局 55.9% 拐点→10000 局 98.1%，Q 表 142 状态），贪婪评估 100%（平均 12 步），训练 2.25s，11 passed。产物 task7/8-qlearning/
4. [x] **9-1 trajectory-verifier**（三层验证器，离线）：四类轨迹（正常退款/虚假承诺/违规泄露/过度拒绝）诊断正确，7 维度与专家标签 100% 一致（precision/recall=1.0），10 tests OK。产物 task7/9-1-verifier/
5. [x] **9-9 longitudinal**（参考 Agent 三臂，离线）：evolving（transfer 1.0 / retain 1.0 / 规则变化后 1 题即恢复）、append_only（retain 0.667 / change 0，卡旧规则）、static（全 0）；9 passed、1 failed（zip 哈希锚点打包错位，证据内容本身全部合法：126 回执、9 runs、门禁通过，与本机无关，如实记录未刷绿）。产物 task7/9-9-longitudinal/
6. [x] **9-3 prompt-auto-optimization**（真实 API 闭环）：SiliconFlow Qwen/Qwen3-8B。先 --quick（4 用例，512s，48.5k tokens，候选 holdout 提升但 boundary 0/2→0/2，reject_candidate）；再完整 10 用例（1136s 约 19 分钟，93.7k tokens，52 次 task_agent + 21 次 judge + 1 次 Coding Agent，74 份无凭据回执）——候选消除全部过度转接、boundary 0/5→1/5 ✓，但 holdout 4/5→3/5 退化 ✗（H1/H2），发布门再次正确拦截；人工对照 holdout 4/5、boundary 2/5 更稳。10 项验收门禁全 passed、execution_accepted=true；结果主张如实不刷绿；候选只写 runtime 工作副本，稳定版未覆盖。产物 task7/9-3-prompt-opt/（quick_run.json/full_run.json + .txt 摘要 + candidate_system_prompt_working.txt + probe_siliconflow.py）

## Task 6 执行清单（截止 2026-10-05 03:00，2026-10-04 一天完成）

用户定调：五选一里做前三个（学习总结＋Mini Agent＋知识地图），4/5 不做。产物在 `task6/`

1. [x] **Mini Agent**（`task6/mini-agent/agent.py`，独立单文件）：融合 Ch.2（稳定系统前缀+状态栏+结果截断）、Ch.3（手写 BM25 索引教程 10 章＋jieba 分词＋JSON 跨会话记忆）、Ch.4（OpenAI tool-calling、ReAct、计算器 AST 白名单沙箱）。**21 个离线测试全过**
2. [x] **真实 API demo**（SiliconFlow Qwen3-8B，代金券）：4 脚本场景全对——RAG 有依据回答、写入记忆、**新会话**记忆直接召回不调工具、计算器 36*0.25=9.0。产物 real_run.txt、offline_run.txt、data/last_demo.json
3. [x] **知识地图**（`task6/knowledge-map/knowledge_map.html`，自包含）：10 章核心概念脉络＋109 实验口径（各章 README 表格提取：106 行＋2-8/8-2/10-3 三个合并编号），30 个"我跑过"徽章标注产物位置；数据底表 experiments.json
4. [x] **学习总结**（`task6/学习总结.md`）：六个被实验砸实的认知（每个附真实数据）＋9 条踩坑表＋150 字版＋全产物索引
5. [x] 踩坑（写自己的 Agent 踩的）：多轮历史里的旧 tool 结果污染下一轮判断 → "本轮是否执行过工具"只能看最后一条消息；tool_calls 重建漏 `type:function` 字段；.env 需 dotenv 显式加载
6. [~] 待用户提交（截止 10-05 03:00）

**全书实跑实验 30 个**（去重计数）：1-1；2-3/2-5/2-10；3-1/3-2/3-4/3-6/3-7/3-8/3-10/3-11/3-12；4-1~4-5；5-10/5-12；6-2；7-1/7-3/7-11；9-1/9-3/9-9；10-1/10-2/10-4

---

## 学习日志

### 2026-09-14
- 通读仓库整体结构、README、引言、chapter1 实验索引；理清"环境配置/基础实验"的含义（正文无教程，配置方法在 chapter1/context/README.md）
- 确认本地 zip 中 chapter1 只有 context/（实验 1-1）一个项目；其余章节实验目录齐全（chapter2~10）
- 环境搭建完成：uv + CPython 3.12.13 虚拟环境，ch1 依赖装好；API 选定 DeepSeek 按量付费（火山 Coding Plan 因端点扣费风险+套餐条款弃用）
- 实验 1-1 跑通：单次任务成功（3 轮 ReAct、4 次工具调用）；消融实验 5 模式 × 2 任务 = 10 组全部跑完，结论：历史缺失→死循环，工具/结果缺失→编造数字，思考缺失→简单任务无影响
- 踩坑：① .env 编辑后需 Ctrl+S 保存才生效；② 消融默认任务的 PDF 在 GitHub 上国内打不开，改用 `--cases 2` 离线任务；③ 实验产物已归档到 d:\ai-agent-book\task0\
- Task 0 进度 7/8，只剩读 chapter1.md 正文 + 打卡
- **明天继续：读/讨论第 1 章正文（重点 ReAct 循环 L161、编排模式 L372），然后起草打卡笔记，截止 09-17 03:00**

### 2026-09-15
- 用户读完 chapter1.md，表示内容可理解
- 核对 ablation_results.json 全部 10 组真实数据，起草打卡笔记 `d:\ai-agent-book\task0\打卡笔记.md`（环境搭建/踩坑/ReAct 单次任务/消融对比表/四点结论/产物清单）
- 待用户提交打卡后 Task 0 即 8/8 完成；下一阶段 Task 1（Ch.2~3 上下文与记忆，截止 09-20）

### 2026-09-19
- Task 1 启动：串讲 chapter2（KV Cache/提示工程/Skills/状态栏/压缩）与 chapter3（记忆分类/RAG 流水线/Agentic RAG）
- 装环境踩坑：ch3 整包因 annoy 在 Win+Py3.12 无 wheel 失败 → 按需 pip 装轻量包；SiliconFlow 书默认模型 Qwen3-235B 已下架 → 实测 Qwen/Qwen3.5-35B-A3B 可用
- 实验 3-6 跑通（零 API 费）：BM25 0.833 → Dense 0.917 → Hybrid-RRF 1.0 满分；BM25 死穴=语义改写/跨语言，Dense 死穴=近重复编码（XR-7003 排到 XR-7001）
- 实验 3-1 跑通 json_cards + notes 对比（扩展选做）：结构化卡片更省 token（1445B vs 1922B）、有独立 identity、支持叶子级 UPDATE；notes 名字重复 5 次、无姓名字段
- **下次继续：波谷时段补跑 DeepSeek 的 2-10 压缩和 3-8 Agentic RAG；然后写 Task 1 打卡笔记（截止 09-20 03:00）**

### 2026-09-19（晚，波谷补跑完成）
- 3-8 离线召回对比跑通（零费用）：复杂题单次 8% → 分解检索 100%；3-8 DeepSeek 在线 compare：非 agentic 放弃作答，agentic（deepseek-reasoner，4 轮 16 检索）找到刑法 §18/§235 分层作答
- 2-10 压缩实验跑通（deepseek-v4-flash + mock）：上下文感知压缩省 70% token，压缩比 3.6% 对齐书里 3.0%；小窗口实验验证无压缩第 4 轮溢出、压缩策略同预算零溢出；边界：预算极端小（3K）时压缩也救不了（工具定义是固定开销）
- **Task 1 四个实验全部完成（3-6/3-1/3-8/2-10，超额完成），下次：写打卡笔记，截止 09-20 03:00**

### 2026-09-19（深夜，Task 1 收尾）
- 打卡笔记完成：task1/打卡笔记.md（含 Context/Memory/RAG 三者关系）+ 155 字心得体会
- 为提交要求重跑实验补 4 张终端截图（3-6/3-1/3-8/2-10）；沉淀可复用脚本 task1/run_2-10_compare.py
- **Task 1 打卡已上传，路线图标记完成。下一阶段 Task 2：Chapter 4 Tools 与 MCP，截止 2026-09-23 03:00**

### 2026-09-23（老师调整课程安排）
- 通知：每个 Task 打卡门槛降为「至少跑通 1 个实验」；旧合并 Task（Ch.2+3）拆为 Task 1（截止 09-20）/Task 2（截止 09-23）；Tools→Task 3（09-26）、Coding Agent→Task 4（09-29）各 +3 天；多 Agent→Task 5（10-02 不变）；总结→Task 6（10-05 不变）；**Ch.7~8 移出打卡轨道**
- 三人共识（经确认）：① 时间按新规定；② 内容不降标准——教程标 ✅ 且本机/预算可行的实验全部跑通，📖🚧 档读指南/设计；③ Ch.7~8 自学保留（Ch.7 跑纯 API 实验，Ch.8 只读）
- **待办（用户）：确认 Task 2 是否必须单独打卡**；确认后从 task1/打卡笔记.md 拆 Ch.3 专版到 task2/打卡笔记.md（实验不重跑，产物引用 task1/）
- 同时待确认：Task 5 范围是否含 Ch.9

### 2026-09-23（Task 2 实验全部跑通）
- 用户确认「知识库」3-6/3-8 早已完成后，指令把 Ch.3 剩余实验全部跑掉；一天内自主跑通 3-4、3-2 memobase、3-12、3-2 mem0
- **3-4**：annoy/hnswlib 无 Win wheel → numpy 手写 RPForest（50 树复刻 ANNOY 超平面二分）+ usearch HNSW；bge-m3 向量。recall 0.99/1.0，实测验证 HNSW 更快更小、增量插入无需全量重建
- **3-2 memobase**：SiliconFlow 仅允许一个 system 消息，把记忆上下文并入 system 后三组 demo 全通
- **3-12**：66 案合成集跑通四段流水线（35B 模型平台拥塞，换 Qwen2.5-14B，抽取 6 并发 45s），聚出 10 个案件原型，对话 Agent 正确匹配入户盗窃原型并给出刑期区间建议
- **3-2 mem0**：真实 mem0ai 2.x 跑通 ADD-only 事实抽取 + 向量检索；修三个配置坑（维度 1024、history_db_path 重定向、filters 新签名）
- **Ch.3 共 10 个实验全部完成**；学习档案已回写
- **待办（用户）：确认 Task 2 是否必须单独打卡**；下一阶段主线 Task 3 Ch.4 Tools，截止 2026-09-26 03:00

### 2026-09-25（Task 3 六个实验全部跑通）
- 按讨论计划（全部可行项跑通 + SiliconFlow）一天内完成 Ch.4 全部 6 个实验
- **4-1/active-tool-selection**（纯离线）：主动工具发现 8/8 且省 11.9 倍 token；检索式在 400 工具规模仍恒定 522 tok
- **4-2 perception-tools**：踩 MCP 版本分裂（v2 独立 venv），127 工具 smoke + 34 离线测试 + 天气/汇率/PubChem 真实调用
- **4-4 execution-tools**：Windows 跨平台修复（python3/bash 硬编码、wc→PowerShell），7 步 demo 全通
- **4-5 collaboration-tools**：子 Agent 双策略真实对比（minimal vs llm_generated token 账），HITL/async/通知验证
- **4-3 multimodal-agent**：最小适配 OPENAI_BASE_URL+qwen-vl 配置；Qwen3-VL-8B 三范式均读出 Q4=$180M；观察到模型 function-calling 幻觉文件名；PDF 走 pypdf+内嵌图混合路径（原生 PDF 仅 Gemini，受限标注）；19 测试通过
- 产物全部归档 task3/（20 个文件），档案已回写
- Task 3 打卡笔记已于当日提交（含 4 个适配 py 归档 task3/）。下一阶段 Task 4 Ch.5~6，截止 09-29

### 2026-09-27（Task 4：Ch.5 核心主线完成）
- 先讨论「Coding Agent vs 通用 Agent」：非并列关系——Coding Agent 是核心内核（七工具+测试修复循环），通用 Agent 还含文件系统中枢/Deep Research/Computer Use；代码是「能创造新工具的工具」即元能力
- 按用户定调（核心主线 + 省费用），完成 2 个实验，产物在 task4/
- **coding-agent 本体**：--list-tools 列出 16 个工具（离线）；pytest 162 passed / 3 failed，3 个失败均为测试用例硬编码 bash 方言（false/export）的平台差异，如实记录不刷绿
- **真实 SiliconFlow 闭环**：模型 Qwen/Qwen3-8B，任务=写 hello_world.py 并运行验证。首跑踩出真实「死亡螺旋」——连续 13 次重复执行，根因是子进程 PATH 中 python 解析到 WindowsApps 商店占位程序（退出码 9009、空输出）。三处适配：①write/edit/multi_edit 的 python3→sys.executable；②main.py 自定义 base_url 时跳过 gpt-/o1- 前缀校验；③支持 WORKING_DIRECTORY 环境变量 + 解释器目录前置子进程 PATH。修后 4 轮迭代 3 次工具调用闭环成功
- **5-12 dynamic-form（离线零费用）**：内置机票 schema 确定性渲染 5043 字符自包含表单，6 项结构化校验全过（show_when 返程级联 + options_when 舱位-行李级联），模拟往返提交→订票摘要闭环；自带 13 测试通过
- 打卡笔记 task4/打卡笔记.md 已起草，待用户提交。Ch.6（交互/Computer Use）是否在本次打卡展开待讨论

### 2026-09-27（补 Ch.6 异步核心，Task 4 完成）
- 按讨论只做 **6-2 async-agent（Flux ★★★）**，Ch.6 其余实验按门槛跳过
- 三个离线能力实测（零费用）：①四只读工具并行 4.55s→1.50s（3.03x）；②打断三任务进度冻结 36/24/12%，系统无损并跑完新任务 T4；③检查点轨迹+任务进度跨会话还原（运行中任务→suspended）
- 两个坑：DEFAULT_INPUT 按 ../../book/chapter4.md 相对定位→复制 chapter4.md 到 d:\ai-agent-book\book\；test_real_tasks 的 os.kill(pid,0) 是 POSIX 断言（Windows 不抛 ProcessLookupError），取消逻辑本身正确，记为平台差异
- canonical 验收 run_real_experiment.py（19.2s）：四场景真实白名单子进程（shell=False），9 项门禁全 passed
- Task 4 打卡笔记已更新为 3 个实验完整版（Ch.5 两实验 + Ch.6 6-2），待用户提交。下一阶段 Task 5 多 Agent 协作（Ch.10，Ch.9 是否含待确认），截止 10-02

### 2026-10-01（Task 5：三个实验全部跑通）
- 先讨论确定范围：10-1 + 10-2 + 10-4（用户选定）；Tavily key 用户指定；10-4 先试官方 Stanford 站点
- ch10 环境装好（pytest 需额外 --extra dev）；Playwright Chromium 1228 下载完成
- **10-2**：真实双臂对比，Manager 峰值 883 vs 单 Agent 2101，指定术语遵从 100% vs 27%；多臂总 token 反而更多（14672 vs 8293），多 Agent 的收益在上下文峰值与一致性而非省总量
- **10-1**：demo 移交链跑通；配对 3×3 结果 Skill 3/9 vs Transfer 0/9，与 2025 版 qwen-flash 结论一致——弱模型下 Transfer 移交后无法收尾；首轮曾挂起一次（网络调用卡死），--resume + 60s 超时跑完
- **10-4**：Stanford 网络可达（浏览器能开故 API 也通），两种场景真实浏览器均跑通：not_found 加速 1.285、found 级联终止加速 1.257；profiles 同名 人事件验证了证据约束（无幻觉）
- 产物归档 task5/，档案已回写。**待办：起草 Task 5 打卡笔记，截止 10-02 03:00**

### 2026-10-03（Task 5 收官，Task 6 启动前讨论）
- 用户确认 Task 5 已提交、老师无问题反馈。打卡轨道只剩 Task 6（截止 10-05 03:00，约剩 2 天）
- 讨论 Ch.7/8/9 的自学价值（结论已口头给出）：Ch.7、Ch.9 与应用层工程强相关值得补，Ch.8 概念级阅读即可；但优先保 Task 6
- 目录事实核对：本地 zip 的 ch7/ch9 实验代码目录**实际存在**（elo-leaderboard、trajectory-verifier 等均在；早先"只有 README"的判断是 glob 模式问题）

### 2026-10-03（Task 7 选做完成：Ch.7~9 六个实验全部跑通）
- 用户定调：今天补 Ch.7/8/9，明天做 Task 6；选定范围「离线 5 个 + 9-3 真实跑」。建 `task7/` 六个子目录
- **Ch.7**：7-public-health 评估方法综合 demo 满分 30/30 + 19 passed；7-elo 用 5000 场模拟对战验证 Bradley-Terry 能从嘈杂成对结果中精确恢复 8 模型真值排序 + 42 passed。直观理解了 Elo/bootstrap 在排行榜场景的用法
- **Ch.8**：8-qlearning 手搓表格 Q-learning（ε-贪婪、状态哈希、lr=0.2、γ=0.99），学习曲线 6000 局拐点、万局 98.1% 与官方一致；贪婪评估 100%。补上了 RL「试错—奖励—价值更新」最小闭环的体感
- **Ch.9**：9-1 三层验证器（环境结果/过程规则/语言质量）对四类轨迹诊断与专家标签 100% 一致；9-9 三臂纵向实验证明「只追加不修订」会卡在旧规则（retain 0.667/change 0），持续进化机制规则变化后 1 题即恢复；9-9 有 1 个测试因教程 zip 哈希锚点错位失败，非环境问题，如实记录
- **9-3 真实 API**（SiliconFlow Qwen3-8B，代金券）：跑完「评测→三维诊断→Coding Agent 出最小 diff→holdout/boundary 双集回归→发布门」完整闭环。两次发布决定都是 reject_candidate：quick 是 boundary 未提升，完整跑是 boundary 改善但 holdout 退化——门禁成功拦截了「拆东墙补西墙」的候选；人工调优版（holdout 4/5、boundary 2/5）仍更稳。完整跑 19 分钟、93.7k tokens、74 份回执、10 项验收门禁全过
- 踩坑：① 7-elo 需 `uv sync --locked --extra ch6 --extra dev`；② Tee-Object 对长任务缓冲导致假挂起，改用 `python -u` + JSON 文件取证；③ Qwen3 是推理模型，简单调用也烧 ~335 reasoning tokens、15s+/次
- 三章核心收获：Ch.7「没有度量就没有改进」、Ch.8「SFT 记忆 RL 泛化、数据环境比算法重要」、Ch.9「提案—回归—灰度—回滚，候选永远不直接覆盖稳定版」
- **Task 7 为选做，不计入打卡。明天（2026-10-04 周日）一天做完 Task 6 结业作业（五选一，须独立完成），周一（2026-10-05）03:00 前提交**

### 2026-10-04（Task 6 结业：三件套一天完成）
- 用户定调：五选一做前三个（学习总结/Mini Agent/知识地图）。执行顺序：Mini Agent（风险最高先啃）→ 知识地图 → 学习总结
- **Mini Agent**：独立单文件，BM25（手写，jieba）索引教程 10 章＋JSON 跨会话记忆＋计算器 AST 沙箱。21 离线测试全过；SiliconFlow Qwen3-8B 真实 demo 4 场景全对（新会话记忆召回不调工具是关键验证）
- 自测踩坑：①历史旧 tool 结果污染 → 只看最后一条消息；②tool_calls 重建漏 type:function（首轮无历史没暴露）；③.env 需显式 dotenv
- **知识地图**：各章 README 提取 109 实验口径（注意新版 README 有合并编号行＋下方"外部仓库溯源表"需用状态 emoji 排除），30 个我跑过徽章
- **学习总结**：六个认知全附真实数据＋9 条踩坑＋150 字版；计数核对后从误写的 27 改为 30
- **全部结业作品完成，待用户在 10-05 03:00 前提交**
