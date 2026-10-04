# -*- coding: utf-8 -*-
"""实验 3-12 运行器（学习路径，旧版合成 66 案）。

官方验收 campaign.py 需处理 420 个真实 CAIL2018 案例；本学习脚本沿用仓库自带的
66 案合成集，完整跑通四段流水线，差别仅在：
  - LLM 走 SiliconFlow（OpenAI 兼容端点），模型 Qwen/Qwen3.5-35B-A3B；
  - 阶段 2 的 66 次逐条抽取改为 ThreadPoolExecutor 6 并发（官方为串行），
    缓存格式与官方 data/extracted.jsonl 完全一致。
阶段 1 因子发现、阶段 3 聚类/重要性、阶段 4 对话建议全部调用官方模块。
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

EXP_DIR = Path(r"D:\ai-agent-book-main\chapter3\structured-knowledge-extraction")
sys.path.insert(0, str(EXP_DIR))

os.environ.setdefault("LLM_PROVIDER", "dashscope")
os.environ.setdefault("DASHSCOPE_BASE_URL", "https://api.siliconflow.cn/v1")
os.environ.setdefault("DASHSCOPE_MODEL", "Qwen/Qwen2.5-14B-Instruct")
if "DASHSCOPE_API_KEY" not in os.environ:
    # 从教程仓库 .env 读取 SiliconFlow key
    env = Path(r"D:\ai-agent-book-main\.env").read_text(encoding="utf-8")
    for line in env.splitlines():
        if line.startswith("SILICONFLOW_API_KEY="):
            os.environ["DASHSCOPE_API_KEY"] = line.split("=", 1)[1].strip()

import archetypes
import discovery
from advisor_agent import LegalAdvisorAgent
from config import MODEL
from extractor import extract_one, load_dataset

CACHE_PATH = EXP_DIR / "data" / "extracted.jsonl"
OUT_DIR = Path(r"d:\ai-agent-book\task2")


def section(title):
    print("\n" + "=" * 74)
    print(title)
    print("=" * 74, flush=True)


def main():
    cases = load_dataset()
    print(f"模型 {MODEL}，案例 {len(cases)} 条", flush=True)

    # ---------- 阶段 1 ----------
    section("阶段 1 / 自下而上因子发现")
    t0 = time.time()
    schema = discovery.discover_schema(cases, batch_size=12, use_cache=True)
    discovery.print_schema(schema)
    stage1_s = time.time() - t0

    # ---------- 阶段 2（并发） ----------
    section("阶段 2 / 结构化抽取（6 并发）")
    t0 = time.time()
    cache = {}
    if CACHE_PATH.exists():
        for line in CACHE_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                cache[rec["id"]] = rec["extracted"]

    todo = [c for c in cases if c["id"] not in cache]
    print(f"待抽取 {len(todo)} 条（缓存 {len(cache)} 条）", flush=True)

    def work(c):
        # 每次调用独立 client，避免跨线程共享
        from config import get_client
        client = get_client()
        return c["id"], extract_one(c["fact"], schema=schema, client=client,
                                    charge=c.get("charge"))

    done_n = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = [pool.submit(work, c) for c in todo]
        for fut in as_completed(futs):
            cid, extracted = fut.result()
            cache[cid] = extracted
            done_n += 1
            if done_n % 10 == 0:
                print(f"  完成 {done_n}/{len(todo)}", flush=True)

    results = [{**c, "extracted": cache[c["id"]]} for c in cases]
    with open(CACHE_PATH, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps({"id": r["id"], "extracted": r["extracted"]},
                                ensure_ascii=False) + "\n")
    stage2_s = time.time() - t0
    print(f"  实际调用 {done_n} 次，用时 {stage2_s:.0f}s", flush=True)

    # ---------- 阶段 3 ----------
    section("阶段 3 / 聚类成案件原型 + 层次因子重要性")
    model = archetypes.fit(schema, results, save=True)
    archetypes.print_model(model)

    # ---------- 阶段 4 ----------
    section("阶段 4 / 对话式量刑建议 Agent")
    agent = LegalAdvisorAgent(schema, model)

    turn1 = ("我朋友之前因为盗窃被判过刑，这次他撬门进了别人家里偷东西，被抓的时候没反抗。"
             "这种情况大概会判多久？")
    print(f"\n用户: {turn1}")
    known = agent.extract_known(turn1)
    print(f"\n已识别因子: {json.dumps(known, ensure_ascii=False)}")
    questions = agent.missing_important_questions(known)
    print("\n追问:")
    for q in questions[:5]:
        print(f"  - [{q['name_cn']} 重要度{q['importance']:.3f}] {q['question']}")

    turn2 = ("补充一下：这次偷的东西价值大概 5 万元，事后他没有退赃，"
             "作案时也没带凶器，是他一个人干的，到了法庭上他认罪认罚了。")
    print(f"\n用户: {turn2}")
    known2 = agent.extract_known(turn1 + " " + turn2)
    print(f"\n更新后因子: {json.dumps(known2, ensure_ascii=False)}")
    arch, advice = agent.advise(known2)
    print(f"\n匹配到 原型#{arch['id']}（典型刑期中位 {arch['months']['median']:.0f} 月，"
          f"区间 {arch['months']['min']:.0f}~{arch['months']['max']:.0f} 月）")
    print(f"\n量刑建议:\n{advice}")

    summary = {
        "model": MODEL,
        "n_cases": len(cases),
        "timing_s": {"stage1_discover": round(stage1_s, 1),
                      "stage2_extract": round(stage2_s, 1)},
        "n_archetypes": model["n_archetypes"],
        "silhouette_mean": round(model["silhouette_mean"], 3),
        "top_global_importance": [
            {"label": x["label"], "score": round(x["score"], 3)}
            for x in model["global_importance"][:8]
        ],
        "matched_archetype": {
            "id": arch["id"], "charge": arch["charge"],
            "months_median": arch["months"]["median"],
            "months_range": [arch["months"]["min"], arch["months"]["max"]],
        },
        "advice": advice,
    }
    out = OUT_DIR / "3-12_summary.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n摘要已写入 {out}")


if __name__ == "__main__":
    main()
