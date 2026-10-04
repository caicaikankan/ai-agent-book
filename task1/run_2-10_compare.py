# 实验 2-10 截图用脚本：无压缩 vs 上下文感知压缩（mock 网页，DeepSeek 驱动 Agent）
# 用法（在仓库根目录执行）：
#   $env:LLM_PROVIDER="deepseek"; $env:MODEL_NAME="deepseek-v4-flash"; $env:MAX_ITERATIONS="6"
#   uv run python d:\ai-agent-book\task1\run_2-10_compare.py
import sys, io, json
from datetime import datetime

sys.path.insert(0, r"D:\ai-agent-book-main\chapter2\context-compression")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from config import Config
from experiment import ExperimentRunner
from compression_strategies import CompressionStrategy

Config.LLM_PROVIDER = "deepseek"
Config.MODEL_NAME = "deepseek-v4-flash"
Config.MAX_ITERATIONS = 6  # mock 数据只覆盖 4 个创始人，6 轮足够对比 token 经济性

api_key, base_url, model = Config.resolve_llm()
print("=" * 70)
print(f"实验 2-10：上下文压缩对比 | provider={Config.LLM_PROVIDER} model={model}")
print(f"任务：追踪 OpenAI 联合创始人现状（无 SERPER key，自动使用 mock 网页）")
print("=" * 70)

runner = ExperimentRunner(api_key=api_key, results_file=None)
results = []
for strat in (CompressionStrategy.NO_COMPRESSION, CompressionStrategy.CONTEXT_AWARE):
    results.append(runner.run_single_strategy(strat))

print("\n" + "=" * 70)
print("对比汇总")
print("=" * 70)
print(f"{'策略':<24}{'轮数':>4}{'工具调用':>8}{'累计tokens':>12}{'压缩比':>8}{'溢出':>4}")
for r in results:
    m = r["metrics"]
    ratio = m.get("compression_ratio", 1.0)
    print(f"{m['strategy']:<24}{m['iterations']:>4}{m['tool_calls']:>8}"
          f"{m.get('total_tokens', 0):>12,}{ratio:>7.1%}{m.get('context_overflows', 0):>4}")
    if m.get("total_original_size"):
        print(f"  原始 {m['total_original_size']:,} 字符 -> 进上下文 {m['total_compressed_size']:,} 字符")

out = r"d:\ai-agent-book\task1\2-10_mock_compare_rerun.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n原始数据已保存：{out}")
