"""Mini Agent 离线测试（零 API 费用）：覆盖 BM25、记忆、计算器、ReAct 主循环。"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent as A  # noqa: E402


@pytest.fixture(scope="module")
def kb():
    return A.KnowledgeBase.get()


# ---------------- BM25 知识库 ----------------

def test_index_has_all_ten_chapters(kb):
    sources = {c.source for c in kb.chunks}
    expected = {f"chapter{i}.md" for i in range(1, 11)}
    assert expected <= sources
    assert len(kb.chunks) > 100


def test_bm25_finds_core_formula(kb):
    hits = kb.search("Agent 的核心公式 LLM 上下文 工具")
    assert hits, "应当检索到结果"
    top = hits[0]
    # 公式出自第 1 章；后记中公式作为全书回顾词频更密集，BM25 下也可能排第一
    assert top["source"] in {"chapter1.md", "afterword.md"}
    assert "LLM" in top["text"]
    # 得分应单调不增
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_bm25_semantic_topic(kb):
    # 中文语义改写也应命中对应章节
    hits = kb.search("提示词注入 攻击 防御")
    assert hits
    assert hits[0]["source"] == "chapter2.md"


def test_bm25_no_hit_returns_empty(kb):
    # 纯罕见拉丁 token 才能保证零命中（中文生造句会被切成常用字而误命中）
    assert kb.search("qxzwvkjhfb") == []


# ---------------- 长期记忆 ----------------

@pytest.fixture
def memory(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    return A.Memory("tester")


def test_memory_add_persists_and_recall(memory):
    memory.add("我喜欢用 Python 写 Agent")
    memory.add("我讨厌冗长的会议")

    recalled = memory.recall("Python Agent 开发")
    assert len(recalled) == 1
    assert "Python" in recalled[0]["content"]
    assert recalled[0]["id"] == 1
    assert "ts" in recalled[0]


def test_memory_cross_session(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    A.Memory("cross").add("学习目标是年底做完 RAG 项目")
    # 重新加载（模拟新会话）
    reloaded = A.Memory("cross")
    assert len(reloaded.facts) == 1
    assert reloaded.recall("我的学习目标是什么")


# ---------------- 计算器安全沙箱 ----------------

@pytest.mark.parametrize("expr, expected", [
    ("1 + 2 * 3", 7),
    ("(1 + 2) * 3", 9),
    ("10 / 4", 2.5),
    ("2 ** 5", 32),
    ("abs(-3) + round(2.6)", 6),
])
def test_calculator_valid(expr, expected):
    assert A.safe_calc(expr) == expected


@pytest.mark.parametrize("evil", [
    "__import__('os').system('echo hacked')",
    "open('secret.txt').read()",
    "(lambda: 1)()",
    "().__class__.__bases__",
])
def test_calculator_rejects_attack(evil):
    with pytest.raises(ValueError):
        A.safe_calc(evil)


def test_calculator_rejects_big_power():
    with pytest.raises(ValueError):
        A.safe_calc("2 ** 100")


# ---------------- ReAct 主循环（离线 mock LLM） ----------------

def test_react_rag_turn(kb, tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    answer, messages = A.run_turn("u1", "Agent 的核心公式是什么？", llm=A.OfflineLLM(), verbose=False)
    # 命中第 1 章并注明来源（章首块的前 160 字未必出现 LLM 字样）
    assert "chapter1.md" in answer
    roles = [m["role"] for m in messages]
    assert roles.count("assistant") == 2  # 一次工具调用 + 一次收尾
    assert "tool" in roles


def test_react_calculator_turn(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    answer, _ = A.run_turn("u1", "计算：36*0.25", llm=A.OfflineLLM(), verbose=False)
    assert "9.0" in answer


def test_react_remember_then_recall(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    # 第一回合：要求记住
    ans1, _ = A.run_turn("u2", "记住：我的学习目标是年底做完 RAG 项目",
                         llm=A.OfflineLLM(), verbose=False)
    assert "已记住" in ans1
    # 第二回合（新会话）：记忆应被召回并直接回答，不再调工具
    ans2, messages = A.run_turn("u2", "我的学习目标是什么？",
                                llm=A.OfflineLLM(), verbose=False)
    assert "RAG" in ans2
    assert not any(m["role"] == "tool" for m in messages)


def test_react_terminates_within_max_iter(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    _, messages = A.run_turn("u3", "什么是上下文工程？", llm=A.OfflineLLM(), verbose=False)
    # 一次检索即收尾，远少于 MAX_ITER
    assert len([m for m in messages if m["role"] == "assistant"]) <= 2


def test_demo_script_runs_offline(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "DATA_DIR", tmp_path)
    transcript = A.run_demo(real=False, user_id="demo_user")
    assert len(transcript) == 4
    tags = [t["tag"] for t in transcript]
    assert tags == ["RAG 检索", "写入记忆", "新会话调用跨会话记忆", "计算器工具"]
    # 第 3 条（新会话记忆召回）不应再产生工具调用
    mem_turn = transcript[2]["messages"]
    assert not any(m["role"] == "tool" for m in mem_turn)
    # 第 4 条计算器结果正确
    assert "9.0" in transcript[3]["answer"]
    saved = json.loads((tmp_path / "last_demo.json").read_text(encoding="utf-8"))
    assert len(saved) == 4
