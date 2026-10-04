# -*- coding: utf-8 -*-
"""实验 3-2 mem0 最小验证：真实 mem0ai 框架，LLM/embedder 均指向 SiliconFlow。"""
import json
from pathlib import Path
from mem0 import Memory

KEY = "sk-yvptkepabfmvsytibtsphhaykymqzhxykagvrbxssrtkrgnj"
BASE = "https://api.siliconflow.cn/v1"

config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "Qwen/Qwen2.5-14B-Instruct",
            "openai_base_url": BASE,
            "api_key": KEY,
            "temperature": 0,
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "BAAI/bge-m3",
            "openai_base_url": BASE,
            "api_key": KEY,
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": r"d:\ai-agent-book\task2\data\mem0_qdrant",
            "embedding_model_dims": 1024,
        },
    },
    "version": "v1.1",
    "history_db_path": r"d:\ai-agent-book\task2\data\mem0_history.db",
}

m = Memory.from_config(config)
uid = "u_3_2"
msgs = [
    "我住在北京，是一名后端工程师，平时主要用 Python。",
    "我最近从北京搬到了上海，新工作还是写后端。",
]
for text in msgs:
    r = m.add(text, user_id=uid)
    print("ADD:", json.dumps(r, ensure_ascii=False)[:200], flush=True)

for q in ["这个用户现在住在哪个城市？", "这个用户是做什么工作的？用什么语言？"]:
    r = m.search(q, filters={"user_id": uid})
    print("\nQUERY:", q)
    print(json.dumps(r, ensure_ascii=False, indent=2)[:900], flush=True)

all_mem = m.get_all(filters={"user_id": uid}, top_k=100)
Path(r"d:\ai-agent-book\task2\3-2_mem0_result.json").write_text(
    json.dumps(all_mem, ensure_ascii=False, indent=2), encoding="utf-8")
print("\n记忆条数:", len(all_mem.get("results", [])))
