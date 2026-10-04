# -*- coding: utf-8 -*-
"""为我们自己的 13 块语料生成对齐的 3-10 评测集。
策略：取作者每条 gold_chunk 的一个稳定特征片段（该块 note 指明的条文短句），
在我们的块里做归一化包含匹配，映射到我们的 chunk_id。"""
import json
import re
from pathlib import Path

CR = Path(r"D:\ai-agent-book-main\chapter3\contextual-retrieval")
STORE = json.loads((CR / "document_store.json").read_text(encoding="utf-8"))
AUTHOR_EVAL = json.loads((CR / "evaluation" / "retrieval_eval.json").read_text(encoding="utf-8"))

clean = lambda s: re.sub(r"\s+", "", s)

# 我们的块（id -> 归一化原文）
mine = {cid: clean(e["metadata"]["original_text"]) for cid, e in STORE.items()}

# 作者每块的代表性特征短句（人工取自 gold note 与正文，保证唯一可定位）
FEATURE = {
    "宪法_chunk_0": "1982年12月4日第五届全国人民代表大会第五次会议通过",
    "宪法_chunk_1": "国家的根本任务是，沿着中国特色社会主义道路",
    "宪法_chunk_2": "坚持互相尊重主权和领土完整、互不侵犯、互不干涉内政、平等互利、和平共处的五项原则",
    "宪法_chunk_3": "各少数民族聚居的地方实行区域自治",
    "宪法_chunk_4": "国家保护个体经济、私营经济等非公有制经济",
    "宪法_chunk_6": "国家在必要时得设立特别行政区",
    "宪法_chunk_7": "对于任何国家机关和国家工作人员的违法失职行为，有向有关国家机关提出申诉、控告或者检举的权利",
    "宪法_chunk_10": "第六十七条全国人民代表大会常务委员会行使下列职权",
    "宪法_chunk_12": "中华人民共和国主席根据全国人民代表大会的决定",
    "宪法_chunk_14": "地方各级人民代表大会是地方国家权力机关",
    "宪法_chunk_15": "县级以上的地方各级人民代表大会设立常务委员会",
    "宪法_chunk_17": "中华人民共和国设立最高人民检察院",
    "检察官法_2019_04_23_chunk_0": "为了全面推进高素质检察官队伍建设",
    "检察官法_2019_04_23_chunk_2": "对检察官的考核",
    "检察官法_2019_04_23_chunk_3": "检察官的职业保障",
}


def map_gold(author_gold):
    feat = clean(FEATURE[author_gold])
    hits = [cid for cid, txt in mine.items() if feat in txt]
    return hits


out_queries = []
for q in AUTHOR_EVAL["queries"]:
    hits = map_gold(q["gold_chunk_id"])
    if len(hits) != 1:
        raise SystemExit(f"{q['id']} gold={q['gold_chunk_id']} 映射不唯一: {hits}")
    out_queries.append({
        "id": q["id"],
        "query": q["query"],
        "gold_chunk_id": hits[0],
        "author_gold_chunk_id": q["gold_chunk_id"],
    })

out = {
    "description": "3-10 本地 13 块语料对齐评测集（gold 经特征短句映射自官方 retrieval_eval.json）",
    "queries": out_queries,
}
path = Path(r"d:\ai-agent-book\task2\3-10_local_eval.json")
path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("映射完成：")
for q in out_queries:
    print(f"  {q['id']}: {q['author_gold_chunk_id']} -> {q['gold_chunk_id']}")
print(f"已写入 {path}")
