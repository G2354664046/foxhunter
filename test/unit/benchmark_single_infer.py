import os
import sys
import time
from statistics import mean

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.services.cxn_cnn.inference import predict_cnn

# 这里填你已经生成好的灰度图路径（256x256 png）
IMAGE_PATH = "out_data/sample_1.png"
ROUNDS = 30

times_ms = []

# 先预热一次，避免首次加载模型影响
_ = predict_cnn(IMAGE_PATH)

for _ in range(ROUNDS):
    t0 = time.perf_counter()
    _ = predict_cnn(IMAGE_PATH)
    t1 = time.perf_counter()
    times_ms.append((t1 - t0) * 1000)

times_ms.sort()
p95 = times_ms[int(len(times_ms) * 0.95) - 1]

print(f"轮次: {ROUNDS}")
print(f"平均耗时: {mean(times_ms):.2f} ms")
print(f"最小耗时: {min(times_ms):.2f} ms")
print(f"最大耗时: {max(times_ms):.2f} ms")
print(f"P95耗时: {p95:.2f} ms")