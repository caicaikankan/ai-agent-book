# -*- coding: utf-8 -*-
"""实验 3-4 离线可运行版：稠密向量 + ANN 索引基准。

与官方 benchmark.py 的对应关系：
- 语料/查询/评测口径完全沿用官方（同 TOPICS、300 docs、20 queries、top-k=10、
  exact ground truth 用 queries @ matrix.T）。
- 向量：官方用本地 Qwen3-Embedding-0.6B（torch+transformers，本机不装）；
  本版用 SiliconFlow 托管的 BAAI/bge-m3（真实稠密 embedding，1024 维）。
- 后端：annoy / hnswlib 在 Windows 无预编译 wheel（需 MSVC），故用
  ① RPForest——纯 numpy 复刻 ANNOY 的随机投影森林（建树/搜索/需全量重建）；
  ② usearch.Index——工业级 HNSW 实现（增量插入、无需重建）。
评测 recall@k、构建时间、查询延迟、序列化大小、增量更新行为，与官方一致。
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np
from openai import OpenAI
from usearch.index import Index as USearchIndex

TOPICS = [
    ("vector search", "Approximate nearest-neighbor indexes accelerate semantic vector retrieval."),
    ("database transactions", "Database transactions use atomicity, consistency, isolation and durability."),
    ("photosynthesis", "Green plants turn sunlight and carbon dioxide into chemical energy."),
    ("quantum entanglement", "Entangled particles exhibit correlated quantum measurement outcomes."),
    ("contract law", "A valid contract generally requires offer acceptance and consideration."),
    ("neural networks", "Deep neural networks learn layered nonlinear representations from data."),
    ("cybersecurity", "Zero trust security continuously verifies identity and device posture."),
    ("volcanoes", "Volcanoes form when magma rises through fractures in the planetary crust."),
    ("water cycle", "Evaporation condensation precipitation and runoff form the water cycle."),
    ("operating systems", "An operating system schedules processes and manages memory and devices."),
    ("HTTP errors", "HTTP status 403 means a server understood but refused a request."),
    ("machine translation", "Multilingual models translate meaning between natural languages."),
    ("financial risk", "Portfolio diversification reduces exposure to idiosyncratic financial risk."),
    ("medical imaging", "Radiology systems analyze X-rays CT scans and magnetic resonance images."),
    ("supply chains", "Supply chain planning coordinates inventory logistics demand and suppliers."),
    ("climate science", "Climate models simulate long-term interactions among atmosphere ocean and land."),
    ("CPU instructions", "SIMD instructions apply one operation to several packed numeric values."),
    ("compiler design", "A compiler parses source code optimizes intermediate form and emits machine code."),
    ("graph theory", "Graph algorithms traverse vertices and edges to discover paths and communities."),
    ("astronomy", "Astronomers infer stellar properties from spectra luminosity and orbital motion."),
]


# ----------------------------- 语料（同官方） -----------------------------

def build_corpus(n_docs: int):
    docs, ids = [], []
    variants = (
        "A concise technical overview.",
        "This passage explains the central mechanism and its practical use.",
        "An engineering handbook entry with definitions and examples.",
        "A research summary intended for a multilingual knowledge base.",
        "Operational notes emphasizing trade-offs, reliability, and performance.",
    )
    for i in range(n_docs):
        topic, sentence = TOPICS[i % len(TOPICS)]
        variant = variants[(i // len(TOPICS)) % len(variants)]
        docs.append(f"Topic: {topic}. {sentence} {variant} Document revision {i:04d}.")
        ids.append(f"doc_{i:04d}")
    return ids, docs


# ----------------------------- bge-m3 向量 -----------------------------

def encode(texts: Sequence[str], batch_size: int = 32) -> np.ndarray:
    key = os.environ.get("SILICONFLOW_API_KEY")
    if not key:
        sys.exit("缺少 SILICONFLOW_API_KEY")
    client = OpenAI(api_key=key, base_url="https://api.siliconflow.cn/v1", timeout=90)
    out = []
    for s in range(0, len(texts), batch_size):
        for attempt in range(3):
            try:
                r = client.embeddings.create(
                    model="BAAI/bge-m3", input=list(texts[s:s + batch_size])
                )
                out.extend(d.embedding for d in sorted(r.data, key=lambda x: x.index))
                break
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"  batch {s} 重试({e})", flush=True)
                time.sleep(3)
    v = np.asarray(out, dtype="float32")
    return v / np.linalg.norm(v, axis=1, keepdims=True)


# ------------------- RPForest：numpy 复刻 ANNOY 森林 -------------------

class _Node:
    __slots__ = ("normal", "offset", "left", "right", "items")

    def __init__(self):
        self.normal = None   # 分割超平面法向量
        self.offset = None   # 超平面偏移
        self.left = None
        self.right = None
        self.items = None    # 叶子：position 数组


class RPForest:
    """随机投影树森林，思想与 ANNOY 一致：
    每棵树在每个内部节点随机取两点，以其等距超平面递归二分；
    查询时多棵树落到叶子、汇总候选后精确重排。插入新数据需整体重建。
    """

    def __init__(self, n_trees: int = 50, leaf_size: int = 10, seed: int = 37):
        self.n_trees = n_trees
        self.leaf_size = leaf_size
        self.seed = seed
        self.trees: List[_Node] = []
        self.ids: List[str] = []
        self.matrix: np.ndarray | None = None

    def add_items(self, ids: Sequence[str], vectors: np.ndarray) -> None:
        self.ids = list(ids)
        self.matrix = np.asarray(vectors, dtype="float32")
        self.rebuild()

    def _build_tree(self, items: np.ndarray, rng: np.random.Generator) -> _Node:
        node = _Node()
        if len(items) <= self.leaf_size:
            node.items = items
            return node
        a_idx, b_idx = rng.choice(items, 2, replace=False)
        a, b = self.matrix[a_idx], self.matrix[b_idx]
        normal = a - b
        n = np.linalg.norm(normal)
        if n < 1e-8:
            node.items = items
            return node
        normal /= n
        offset = (a + b) / 2
        sides = (self.matrix[items] - offset) @ normal
        left_items = items[sides >= 0]
        right_items = items[sides < 0]
        if len(left_items) == 0 or len(right_items) == 0:
            node.items = items
            return node
        node.normal, node.offset = normal, offset
        node.left = self._build_tree(left_items, rng)
        node.right = self._build_tree(right_items, rng)
        return node

    def rebuild(self) -> None:
        rng = np.random.default_rng(self.seed)
        all_items = np.arange(len(self.ids))
        self.trees = [self._build_tree(all_items, rng) for _ in range(self.n_trees)]

    @staticmethod
    def _leaf(node: _Node, q: np.ndarray) -> _Node:
        while node.items is None:
            node = node.left if (q - node.offset) @ node.normal >= 0 else node.right
        return node

    def search(self, q: np.ndarray, k: int):
        cand = set()
        for tree in self.trees:
            cand.update(self._leaf(tree, q).items.tolist())
        cand = np.fromiter(cand, dtype="int64")
        scores = self.matrix[cand] @ q
        order = cand[np.argsort(-scores)[:k]]
        return [self.ids[i] for i in order], scores[np.argsort(-scores)[:k]].tolist()


# ----------------------------- 评测工具 -----------------------------

def exact_neighbors(matrix: np.ndarray, queries: np.ndarray, k: int):
    scores = queries @ matrix.T
    return [np.argsort(-row)[:k].tolist() for row in scores]


def percentiles(values):
    return {
        "mean": statistics.mean(values),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
    }


def measure_rpforest(ids, vectors, queries, truth, k, repeats):
    forest = RPForest(n_trees=50, leaf_size=10)
    t0 = time.perf_counter()
    forest.add_items(ids, vectors)
    build_ms = (time.perf_counter() - t0) * 1000

    id_to_pos = {d: i for i, d in enumerate(ids)}
    recalls, latencies, rankings = [], [], []
    for qi, q in enumerate(queries):
        first = None
        for _ in range(repeats):
            t0 = time.perf_counter()
            found, _ = forest.search(q, k)
            latencies.append((time.perf_counter() - t0) * 1000)
            if first is None:
                first = found
        found_pos = {id_to_pos[x] for x in first}
        recalls.append(len(found_pos & set(truth[qi])) / k)
        rankings.append({"query_index": qi, "doc_ids": first})

    # 序列化大小：50 棵树的全部超平面参数（向量化近似：vectors + id 表，
    # 与 ANNOY 的落盘内容性质相同——存的是分割面而非原始向量）
    import io
    buf = io.BytesIO()
    for tree in forest.trees:
        def walk(n):
            if n.items is not None:
                buf.write(n.items.tobytes())
            else:
                buf.write(n.normal.tobytes()); buf.write(n.offset.tobytes())
                walk(n.left); walk(n.right)
        walk(tree)
    return {
        "build_ms": round(build_ms, 3),
        "recall_at_k": statistics.mean(recalls),
        "query_latency_ms": percentiles(latencies),
        "serialized_bytes": buf.tell(),
        "rankings": rankings,
    }, forest


def measure_hnsw(ids, vectors, queries, truth, k, repeats, max_elements):
    index = USearchIndex(ndim=vectors.shape[1], metric="cos", dtype="f32",
                         connectivity=16, expansion_add=128, expansion_search=64)
    t0 = time.perf_counter()
    labels = np.arange(len(ids), dtype=np.int64)
    index.add(labels, vectors)
    build_ms = (time.perf_counter() - t0) * 1000

    id_to_pos = {d: i for i, d in enumerate(ids)}
    recalls, latencies, rankings = [], [], []
    for qi, q in enumerate(queries):
        first = None
        for _ in range(repeats):
            t0 = time.perf_counter()
            matches = index.search(q, k)
            latencies.append((time.perf_counter() - t0) * 1000)
            if first is None:
                first = matches.keys.tolist()
        found_ids = [ids[p] for p in first]
        found_pos = {id_to_pos[x] for x in found_ids}
        recalls.append(len(found_pos & set(truth[qi])) / k)
        rankings.append({"query_index": qi, "doc_ids": found_ids})

    with tempfile.NamedTemporaryFile(suffix=".usearch", delete=False) as f:
        path = f.name
    index.save(path)
    size = os.path.getsize(path)
    os.unlink(path)
    return {
        "build_ms": round(build_ms, 3),
        "recall_at_k": statistics.mean(recalls),
        "query_latency_ms": percentiles(latencies),
        "serialized_bytes": size,
        "rankings": rankings,
    }, index


def main():
    n_docs, k, repeats, seed = 300, 10, 5, 37
    np.random.seed(seed)

    ids, docs = build_corpus(n_docs)
    queries = [f"Find technical information about {topic}." for topic, _ in TOPICS]

    print("生成 bge-m3 向量 …", flush=True)
    t0 = time.perf_counter()
    vectors = encode(docs)
    query_vectors = encode(queries)
    embedding_ms = (time.perf_counter() - t0) * 1000
    print(f"  doc {vectors.shape}, query {query_vectors.shape}, {embedding_ms/1000:.1f}s", flush=True)

    dim = vectors.shape[1]
    initial_n = int(n_docs * 0.8)
    initial_truth = exact_neighbors(vectors[:initial_n], query_vectors, k)
    truth = exact_neighbors(vectors, query_vectors, k)

    # ---- 初始 80% ----
    print("RP-forest (ANNOY 类) …", flush=True)
    rp, forest = measure_rpforest(ids[:initial_n], vectors[:initial_n],
                                  query_vectors, initial_truth, k, repeats)
    print(f"  recall@10={rp['recall_at_k']:.3f} build={rp['build_ms']:.1f}ms", flush=True)

    print("HNSW (usearch) …", flush=True)
    hn, hnsw = measure_hnsw(ids[:initial_n], vectors[:initial_n],
                            query_vectors, initial_truth, k, repeats,
                            max_elements=n_docs + 10)
    print(f"  recall@10={hn['recall_at_k']:.3f} build={hn['build_ms']:.1f}ms", flush=True)

    # ---- 增量 20% ----
    t0 = time.perf_counter()
    forest.add_items(ids, vectors)          # ANNOY 类：必须整体重建
    rp_update_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    new_labels = np.arange(initial_n, n_docs, dtype=np.int64)
    hnsw.add(new_labels, vectors[initial_n:])   # HNSW：原地增量
    hn_update_ms = (time.perf_counter() - t0) * 1000

    id_to_pos = {d: i for i, d in enumerate(ids)}
    rp_after, hn_after = [], []
    for qi, q in enumerate(query_vectors):
        found, _ = forest.search(q, k)
        rp_after.append(len({id_to_pos[x] for x in found} & set(truth[qi])) / k)
        m = hnsw.search(q, k).keys.tolist()
        hn_after.append(len({id_to_pos[ids[p]] for p in m} & set(truth[qi])) / k)

    rp["incremental_update"] = {
        "items_added": n_docs - initial_n,
        "latency_ms": round(rp_update_ms, 3),
        "requires_full_rebuild": True,
        "recall_at_k_after_update": statistics.mean(rp_after),
    }
    hn["incremental_update"] = {
        "items_added": n_docs - initial_n,
        "latency_ms": round(hn_update_ms, 3),
        "requires_full_rebuild": False,
        "recall_at_k_after_update": statistics.mean(hn_after),
    }

    passed = rp["recall_at_k"] >= 0.8 and hn["recall_at_k"] >= 0.8
    evidence = {
        "status": "passed" if passed else "partial",
        "configuration": {
            "embedding_model": "BAAI/bge-m3 (SiliconFlow hosted, official used local Qwen3-Embedding-0.6B)",
            "device": "api",
            "seed": seed,
            "dimension": dim,
            "documents": n_docs,
            "queries": len(queries),
            "top_k": k,
            "backends": "RPForest(numpy, ANNOY-like, 50 trees) vs usearch(HNSW, cos)",
            "why_not_official": "annoy/hnswlib 无 Windows 预编译 wheel（需 MSVC C++ Build Tools）；torch/transformers 本地模型未安装",
        },
        "acceptance": {
            "real_embedding_model": True,
            "same_vectors_and_queries": True,
            "exact_search_ground_truth": True,
            "recall_latency_build_size_measured": True,
            "incremental_behavior_measured": True,
            "both_backends_recall_at_least_0_8": passed,
        },
        "summary": {
            "embedding_ms": round(embedding_ms, 3),
            "rpforest": {x: v for x, v in rp.items() if x != "rankings"},
            "hnsw": {x: v for x, v in hn.items() if x != "rankings"},
        },
        "results": {"rpforest": rp, "hnsw": hn},
    }
    out = Path(__file__).parent / "3-4_benchmark.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(evidence["summary"], ensure_ascii=False, indent=2))
    print(f"\n已写入 {out}")


if __name__ == "__main__":
    main()
