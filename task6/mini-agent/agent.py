"""Mini Agent —— 共学营学习助手（Task 6 结业作品，独立实现）

一个文件融合教程三章的核心机制：
- Ch.2 上下文工程：稳定系统前缀 + 工具定义 + 状态栏 + 长结果落盘截断
- Ch.3 记忆与知识库：BM25 中文检索（jieba 分词，直接索引教程 10 章正文）
                 + JSON 跨会话长期记忆
- Ch.4 工具：ReAct 循环、OpenAI tool-calling 协议、计算器 AST 安全沙箱

运行：
  python agent.py index                      # 查看索引统计（离线）
  python agent.py demo --offline             # 脚本化演示，零 API 费用
  python agent.py demo                       # 真实 API（SiliconFlow Qwen3-8B）
  python agent.py ask "你的问题" --user u1   # 单轮提问
"""
from __future__ import annotations

import argparse
import ast
import json
import operator
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path

import jieba

# API Key 统一放在教程根目录的 .env（与前面 Task 的约定一致）
try:
    from dotenv import load_dotenv

    load_dotenv(r"D:\ai-agent-book-main\.env")
except ImportError:
    pass

# ---------------- 配置 ----------------

BOOK_DIR = Path(os.getenv("BOOK_DIR", r"D:\ai-agent-book-main\book"))
DATA_DIR = Path(os.getenv("AGENT_DATA", str(Path(__file__).parent / "data")))
MAX_ITER = int(os.getenv("MAX_ITER", "6"))
MAX_TOOL_CHARS = 1200  # Ch.2：过长工具结果截断，防止上下文爆炸


def provider_config() -> tuple[str, str, str]:
    """返回 (base_url, api_key, model)。默认 SiliconFlow，可用 DeepSeek。"""
    if os.getenv("LLM_PROVIDER", "siliconflow") == "deepseek":
        return (
            "https://api.deepseek.com",
            os.environ["DEEPSEEK_API_KEY"],
            os.getenv("MODEL_NAME", "deepseek-chat"),
        )
    return (
        "https://api.siliconflow.cn/v1",
        os.environ["SILICONFLOW_API_KEY"],
        os.getenv("MODEL_NAME", "Qwen/Qwen3-8B"),
    )


# ---------------- Ch.3：本地知识库 BM25 ----------------

@dataclass
class Chunk:
    source: str   # 文件名
    heading: str  # 章节标题路径
    text: str


def _split_sections(name: str, content: str) -> list[Chunk]:
    """按 markdown 的 ## 标题切块，标题路径保留在块上。"""
    title_match = re.search(r"^#\s+(.+)$", content, re.M)
    chapter_title = title_match.group(1).strip() if title_match else name
    chunks: list[Chunk] = []
    parts = re.split(r"\n##\s+", content)
    # 第一段是章首内容
    head = parts[0].strip()
    if len(head) > 120:
        chunks.append(Chunk(name, chapter_title, head))
    for part in parts[1:]:
        lines = part.split("\n", 1)
        heading = f"{chapter_title} / {lines[0].strip()}"
        body = lines[1].strip() if len(lines) > 1 else ""
        if body:
            chunks.append(Chunk(name, heading, body))
    return chunks


def tokenize_zh(text: str) -> list[str]:
    """jieba 分词 + 英文小写化，去掉空白和纯标点。"""
    return [t.strip().lower() for t in jieba.lcut(text) if t.strip() and re.search(r"[\w一-鿿]", t)]


class BM25:
    """手写 BM25Okapi（不依赖第三方检索库）。"""

    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.n = len(docs)
        self.k1, self.b = k1, b
        self.df: dict[str, int] = {}
        self.doc_len = [len(d) for d in docs]
        self.avgdl = (sum(self.doc_len) / self.n) if self.n else 0.0
        self.tf: list[dict[str, int]] = []
        for doc in docs:
            freq: dict[str, int] = {}
            for t in doc:
                freq[t] = freq.get(t, 0) + 1
            self.tf.append(freq)
            for t in freq:
                self.df[t] = self.df.get(t, 0) + 1
        self.idf = {
            t: __import__("math").log(1 + (self.n - df + 0.5) / (df + 0.5))
            for t, df in self.df.items()
        }

    def search(self, query: list[str], k: int = 3) -> list[tuple[float, int]]:
        scores: list[tuple[float, int]] = []
        for i in range(self.n):
            s = 0.0
            dl = self.doc_len[i] or 1
            norm = self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
            for q in query:
                if q not in self.tf[i]:
                    continue
                f = self.tf[i][q]
                s += self.idf.get(q, 0.0) * f * (self.k1 + 1) / (f + norm)
            if s > 0:
                scores.append((s, i))
        scores.sort(reverse=True)
        return scores[:k]


class KnowledgeBase:
    """教程正文知识库：加载 → 切块 → BM25 索引（进程内单例）。"""

    _instance: "KnowledgeBase | None" = None

    def __init__(self, book_dir: Path):
        files = sorted(book_dir.glob("*.md"))
        self.chunks: list[Chunk] = []
        for f in files:
            if f.name.startswith(("chapter", "introduction", "afterword")):
                self.chunks.extend(_split_sections(f.name, f.read_text(encoding="utf-8")))
        self.bm25 = BM25([tokenize_zh(c.text + " " + c.heading) for c in self.chunks])

    @classmethod
    def get(cls) -> "KnowledgeBase":
        if cls._instance is None:
            cls._instance = cls(BOOK_DIR)
        return cls._instance

    def search(self, query: str, k: int = 3) -> list[dict]:
        hits = self.bm25.search(tokenize_zh(query), k)
        return [
            {
                "score": round(score, 3),
                "heading": self.chunks[i].heading,
                "source": self.chunks[i].source,
                "text": self.chunks[i].text[:MAX_TOOL_CHARS],
            }
            for score, i in hits
        ]


# ---------------- Ch.3：跨会话长期记忆 ----------------

class Memory:
    """每用户一个 JSON 文件：事实只追加，按查询词重叠召回。"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.path = DATA_DIR / f"{user_id}_memory.json"
        self.facts: list[dict] = []
        if self.path.exists():
            self.facts = json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, content: str) -> dict:
        fact = {"id": len(self.facts) + 1, "content": content.strip(),
                "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
        self.facts.append(fact)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.facts, ensure_ascii=False, indent=2), encoding="utf-8")
        return fact

    def recall(self, query: str, k: int = 5) -> list[dict]:
        q = set(tokenize_zh(query))
        scored = []
        for f in self.facts:
            overlap = len(q & set(tokenize_zh(f["content"])))
            if overlap:
                scored.append((overlap, f["id"], f))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return [f for _, _, f in scored[:k]]


# ---------------- Ch.4：工具与安全沙箱 ----------------

_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}
_ALLOWED_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_ALLOWED_FUNCS = {"abs": abs, "round": round, "min": min, "max": max, "pow": pow}


def safe_calc(expression: str) -> float:
    """AST 白名单求值：拒绝属性访问、名字调用（防 __import__ / open 等）。"""
    tree = ast.parse(expression, mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            left, right = _eval(node.left), _eval(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 6:
                raise ValueError("幂次过大")
            return _ALLOWED_BINOPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
            return _ALLOWED_UNARYOPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = _ALLOWED_FUNCS.get(node.func.id)
            if fn is None:
                raise ValueError(f"不允许的函数: {node.func.id}")
            return fn(*[_eval(a) for a in node.args])
        raise ValueError(f"不允许的表达式节点: {type(node).__name__}")

    return _eval(tree)


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_book",
            "description": "在《深入理解 AI Agent：设计原理与工程实践》教程正文中做 BM25 关键词检索。需要书中概念、定义、结论时优先使用。",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "检索关键词或问题"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "把一条关于用户的长期事实写入记忆，跨会话保留。只记用户明确要求记住的事实。",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string", "description": "要记住的事实"}},
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "安全的数学计算器，支持 + - * / % ** 与 abs/round/min/max/pow。任何数值计算必须使用此工具，不得心算。",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "数学表达式，如 36*0.25"}},
                "required": ["expression"],
            },
        },
    },
]


def build_tools(memory: Memory, kb: KnowledgeBase):
    def search_book(query: str) -> str:
        hits = kb.search(query)
        if not hits:
            return json.dumps({"results": [], "hint": "未检索到相关章节，请换关键词"}, ensure_ascii=False)
        return json.dumps({"results": hits}, ensure_ascii=False)

    def remember(fact: str) -> str:
        saved = memory.add(fact)
        return json.dumps({"status": "saved", "fact": saved}, ensure_ascii=False)

    def calculator(expression: str) -> str:
        try:
            return json.dumps({"expression": expression, "result": safe_calc(expression)}, ensure_ascii=False)
        except Exception as exc:  # noqa: BLE001 - 工具错误要回传给模型
            return json.dumps({"expression": expression, "error": str(exc)}, ensure_ascii=False)

    return {"search_book": search_book, "remember": remember, "calculator": calculator}


# ---------------- Ch.2 + Ch.4：ReAct 主循环 ----------------

SYSTEM_PREFIX = """你是「共学营学习助手」，服务于《深入理解 AI Agent：设计原理与工程实践》共学营学员。

铁律：
1. 回答涉及书中内容时，必须先调用 search_book 检索，并以检索到的原文为依据，不得凭印象编造。
2. 任何数值计算必须调用 calculator，禁止心算。
3. 用户明确说「记住」的内容才调用 remember；记忆中的事实可直接使用，无需再检索。
4. 用中文回答，简洁、有条理，引用结论时注明来自哪一章。"""


def build_system(memory: Memory, query: str) -> str:
    """稳定前缀在前（利于 KV Cache），动态记忆块在后。"""
    facts = memory.recall(query)
    if not facts:
        return SYSTEM_PREFIX
    memory_block = "\n\n【长期记忆】\n" + "\n".join(f"- {f['content']}" for f in facts)
    return SYSTEM_PREFIX + memory_block


def est_context_chars(messages: list[dict]) -> int:
    """粗略估算上下文体量（中文约 1 字 ≈ 1 token，仅用于状态栏展示）。"""
    return len(json.dumps(messages, ensure_ascii=False))


class RealLLM:
    def __init__(self):
        from openai import OpenAI

        base_url, api_key, model = provider_config()
        self.model = model
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def chat(self, messages: list[dict]) -> dict:
        resp = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=TOOL_SCHEMAS,
            tool_choice="auto", temperature=0.2, max_tokens=1024,
        )
        m = resp.choices[0].message
        return {
            "role": "assistant",
            "content": m.content or "",
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in (m.tool_calls or [])
            ],
        }


class OfflineLLM:
    """确定性模拟 LLM：按规则产生工具调用，零费用，用于测试与离线演示。"""

    def chat(self, messages: list[dict]) -> dict:
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m["content"] for m in messages if m["role"] == "user"]
        question = user_msgs[-1] if user_msgs else ""
        # 只看最后一条：本轮刚执行完工具时末尾才是 tool；
        # 历史轮次留下的 tool 结果不能算作本轮已执行
        already_called = messages[-1]["role"] == "tool"

        if not already_called:
            # 长期记忆里能直接对上 → 不走工具
            mem_hit = re.search(r"【长期记忆】\n(.+)", system, re.S)
            if mem_hit:
                qtokens = set(tokenize_zh(question))
                for line in mem_hit.group(1).splitlines():
                    if len(qtokens & set(tokenize_zh(line))) >= 2:
                        return {"role": "assistant", "content": f"根据长期记忆：{line.lstrip('- ')}", "tool_calls": []}
            # 数值计算 → calculator：取句中含运算符的最长数字串
            expr_match = re.findall(r"[0-9][0-9\.\+\-\*\/\(\)\s]*[0-9\)]", question)
            expr = next((e.strip() for e in expr_match if re.search(r"[\+\-\*\/]", e)), None)
            if ("计算" in question or "总共" in question) and expr:
                return _tool_call("calculator", {"expression": expr})
            # 明确记忆 → remember
            m = re.search(r"记住[：:]\s*(.+)", question)
            if m:
                return _tool_call("remember", {"fact": m.group(1).strip()})
            # 其余一律检索教程：去掉疑问/语气词，让检索词更干净
            cleaned = re.sub(r"(是什么|有哪些|什么是|请|？|\?|的|呢|吗|给我|介绍一下|解释一下)",
                             " ", question).strip()
            return _tool_call("search_book", {"query": cleaned[:60] or question[:60]})

        # 已有工具结果 → 收尾
        tool_result = next(m["content"] for m in reversed(messages) if m["role"] == "tool")
        data = json.loads(tool_result)
        if "results" in data and data["results"]:
            top = data["results"][0]
            answer = re.sub(r"\s+", " ", top["text"])[:160]
            return {"role": "assistant",
                    "content": f"根据《{top['heading']}》：{answer}……（依据 {top['source']}，检索得分 {top['score']}）",
                    "tool_calls": []}
        if "fact" in data:
            return {"role": "assistant", "content": f"好的，已记住：{data['fact']['content']}", "tool_calls": []}
        if "result" in data:
            return {"role": "assistant", "content": f"计算结果是 {data['result']}。", "tool_calls": []}
        return {"role": "assistant", "content": f"工具未能完成：{tool_result[:120]}", "tool_calls": []}


def _tool_call(name: str, args: dict) -> dict:
    return {"role": "assistant", "content": "",
            "tool_calls": [{"id": f"call_{name}_{int(time.time()*1000)%100000}",
                            "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}]}


def run_turn(user_id: str, message: str, history: list[dict] | None = None,
             llm=None, verbose: bool = True) -> tuple[str, list[dict]]:
    """跑一个用户回合的 ReAct 循环，返回 (最终回答, 本回合完整消息)。"""
    kb = KnowledgeBase.get()
    memory = Memory(user_id)
    tools = build_tools(memory, kb)
    llm = llm or OfflineLLM()

    messages = [{"role": "system", "content": build_system(memory, message)}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": message})

    for step in range(1, MAX_ITER + 1):
        if verbose:
            print(f"  [状态栏] step={step} 消息数={len(messages)} 上下文≈{est_context_chars(messages)} 字符")
        assistant = llm.chat(messages)
        messages.append(assistant)
        calls = assistant.get("tool_calls") or []
        if not calls:
            return assistant["content"], messages
        for call in calls:  # Ch.4：执行工具，结果按 tool 协议回灌
            fn_name = call["function"]["name"]
            fn_args = json.loads(call["function"]["arguments"] or "{}")
            result = tools[fn_name](**fn_args)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})

    return "（已达到最大迭代轮次，被迫停止）", messages


# ---------------- 脚本化演示 ----------------

DEMO_SCRIPT = [
    {"session": 1, "question": "Agent 的核心公式是什么？请给出依据。", "tag": "RAG 检索"},
    {"session": 1, "question": "记住：我的学习目标是在年底独立开发一个 RAG Agent 项目。", "tag": "写入记忆"},
    {"session": 2, "question": "我的学习目标是什么？", "tag": "新会话调用跨会话记忆"},
    {"session": 2, "question": "我一共跑了 36 个实验，平均每个实验花费 0.25 元，计算总花费：36*0.25", "tag": "计算器工具"},
]


def run_demo(real: bool, user_id: str = "demo_user") -> list[dict]:
    # 每次演示清空旧的演示记忆，保证可复现
    mem_file = DATA_DIR / f"{user_id}_memory.json"
    if mem_file.exists():
        mem_file.unlink()

    llm = RealLLM() if real else OfflineLLM()
    label = getattr(llm, "model", "offline-mock")
    print(f"=== Mini Agent 演示（模型：{label}）===")
    transcript: list[dict] = []
    history: list[dict] = []
    current_session = 1

    for item in DEMO_SCRIPT:
        if item["session"] != current_session:
            print(f"\n--- 新会话开始（清空对话历史，长期记忆保留）---")
            history = []
            current_session = item["session"]
        print(f"\n[{item['tag']}] 用户：{item['question']}")
        answer, full_messages = run_turn(user_id, item["question"], history, llm=llm)
        print(f"  助手：{answer}")
        # 保留跨轮历史时，去掉 system，只保留 user/assistant/tool
        history = [m for m in full_messages if m["role"] != "system"]
        transcript.append({"tag": item["tag"], "question": item["question"],
                           "answer": answer, "messages": full_messages})

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / "last_demo.json"
    out.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完整轨迹已保存：{out}")
    return transcript


# ---------------- CLI ----------------

def main():
    parser = argparse.ArgumentParser(description="共学营学习助手 Mini Agent")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("index", help="查看知识库索引统计")
    p_demo = sub.add_parser("demo", help="脚本化演示")
    p_demo.add_argument("--real", action="store_true", help="使用真实 API（默认离线模拟）")
    p_demo.add_argument("--user", default="demo_user")
    p_ask = sub.add_parser("ask", help="单轮提问")
    p_ask.add_argument("question")
    p_ask.add_argument("--user", default="u1")
    p_ask.add_argument("--real", action="store_true")

    args = parser.parse_args()

    if args.cmd == "index":
        kb = KnowledgeBase.get()
        print(f"BOOK_DIR = {BOOK_DIR}")
        print(f"文档块数：{len(kb.chunks)}")
        for c in kb.chunks:
            print(f"  - {c.source} :: {c.heading}（{len(c.text)} 字）")
        demo_hits = kb.search("Agent 核心公式 LLM 上下文 工具")
        print("\n检索自测 query='Agent 核心公式'：")
        for h in demo_hits:
            print(f"  {h['score']}  {h['heading']}")
    elif args.cmd == "demo":
        run_demo(real=args.real, user_id=args.user)
    elif args.cmd == "ask":
        llm = RealLLM() if args.real else OfflineLLM()
        answer, _ = run_turn(args.user, args.question, llm=llm)
        print(answer)


if __name__ == "__main__":
    main()
