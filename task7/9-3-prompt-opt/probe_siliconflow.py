"""最小连通性测试：验证 SiliconFlow Qwen3-8B + 工具调用是否正常。"""
import os
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)
started = time.time()
resp = client.chat.completions.create(
    model=os.getenv("LLM_MODEL", "Qwen/Qwen3-8B"),
    messages=[{"role": "user", "content": "回复'连通正常'四个字即可。"}],
    temperature=0,
    max_tokens=50,
)
print(f"耗时 {time.time() - started:.1f}s")
print("回复：", resp.choices[0].message.content)
print("usage:", resp.usage)
