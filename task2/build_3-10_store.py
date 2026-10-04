# -*- coding: utf-8 -*-
"""实验 3-10：用官方 DocumentChunker 切分《宪法》《检察官法》，
调 SiliconFlow 实时为每块生成上下文前缀，产出 compare_retrieval.py 所需的 document_store.json。

说明：作者随书 receipts 里的 22 块是章节/条款感知切块（生成脚本未随仓库发布，
无法用单一大小阈值复现）。本实验改用官方 chunking.py 的 DocumentChunker（2048 阈值）
切块，实验目标——验证上下文前缀对召回的提升——不受切块具体实现影响。

用法：
  python build_3-10_store.py --dry-run   # 只切块，不调 API
  python build_3-10_store.py             # 切块 + 生成前缀 + 写 document_store.json
"""
import argparse
import concurrent.futures
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

REPO = Path(r"D:\ai-agent-book-main")
CR_DIR = REPO / "chapter3" / "contextual-retrieval"
STORE_PATH = CR_DIR / "document_store.json"
sys.path.insert(0, str(CR_DIR))

from chunking import DocumentChunker  # noqa: E402

SOURCES = [
    ("宪法", REPO / "chapter3" / "agentic-rag" / "laws" / "1-宪法" / "宪法.md"),
    ("检察官法_2019_04_23",
     REPO / "chapter3" / "agentic-rag" / "laws" / "2-宪法相关法" / "检察官法（2019-04-23）.md"),
]


def make_chunks():
    chunker = DocumentChunker()
    out = []
    for doc_title, path in SOURCES:
        text = path.read_text(encoding="utf-8")
        for c in chunker.chunk_text(text, doc_title):
            cid = c.get("chunk_id")
            # 官方 chunk_id 形如 宪法_chunk_0；统一为 <doc>_chunk_<i>
            out.append({
                "chunk_id": cid,
                "doc_title": doc_title,
                "plain": c["text"],
                "chunk_index": int(str(cid).rsplit("_", 1)[1]),
            })
    return out


def gen_prefix(client, model, source_text, chunk_text):
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": (
                "为目标文本块生成简短的中文检索前缀。前缀必须说明该块来自哪份文档、所属章节/条款、"
                "主体与主题，使孤立文本能被准确检索。不得添加源文没有的事实。只输出前缀，不要解释。")},
            {"role": "user", "content": (
                f"完整源文档：\n<document>\n{source_text}\n</document>\n\n"
                f"目标文本块：\n<chunk>\n{chunk_text}\n</chunk>")},
        ],
        temperature=0,
        max_tokens=220,
    )
    return (resp.choices[0].message.content or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="Qwen/Qwen3.5-35B-A3B")
    args = ap.parse_args()

    load_dotenv(REPO / ".env")
    chunks = make_chunks()
    print(f"切块总数：{len(chunks)}")
    for doc_title, _ in SOURCES:
        print(f"  {doc_title}: {sum(1 for c in chunks if c['doc_title'] == doc_title)} 块")

    if args.dry_run:
        return

    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        sys.exit("缺少 SILICONFLOW_API_KEY")
    client = OpenAI(api_key=key, base_url="https://api.siliconflow.cn/v1", timeout=90)
    source_texts = {t: p.read_text(encoding="utf-8") for t, p in SOURCES}

    def work(c):
        prefix = gen_prefix(client, args.model, source_texts[c["doc_title"]], c["plain"])
        return c, prefix

    store = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(work, c) for c in chunks]
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            c, prefix = fut.result()
            store[c["chunk_id"]] = {
                "doc_id": c["chunk_id"],
                "content": f"{prefix}\n\n{c['plain']}",
                "metadata": {
                    "doc_title": c["doc_title"],
                    "original_text": c["plain"],
                    "context": prefix,
                    "chunk_index": c["chunk_index"],
                    "contextual": True,
                },
            }
            print(f"[{i}/{len(chunks)}] {c['chunk_id']} -> {prefix[:60]}", flush=True)

    STORE_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入 {STORE_PATH}")


if __name__ == "__main__":
    main()
