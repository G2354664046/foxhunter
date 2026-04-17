import os
import sys
import time
from statistics import mean

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.services.cxn_cnn.inference import binary_file_to_gray_image


# 改成你的真实样本路径（支持 .exe/.dll/.bin）
FILE_PATH = "uploads/FileZilla_3.68.1_win64-setup.exe"
OUT_DIR = "out_data_benchmark"
ROUNDS = 30


def main() -> None:
    if not os.path.isfile(FILE_PATH):
        raise FileNotFoundError(
            f"样本文件不存在: {FILE_PATH}。\n"
            "请先准备一个可用样本，或修改 FILE_PATH 为实际路径。"
        )

    os.makedirs(OUT_DIR, exist_ok=True)
    times_ms: list[float] = []

    # 预热一次，减少首次调用抖动影响
    _ = binary_file_to_gray_image(FILE_PATH, OUT_DIR, "warmup.png")

    for i in range(ROUNDS):
        t0 = time.perf_counter()
        _ = binary_file_to_gray_image(FILE_PATH, OUT_DIR, f"bench_{i}.png")
        t1 = time.perf_counter()
        times_ms.append((t1 - t0) * 1000)

    times_ms.sort()
    p95_idx = max(0, int(len(times_ms) * 0.95) - 1)
    p95 = times_ms[p95_idx]

    print(f"样本文件: {FILE_PATH}")
    print(f"轮次: {ROUNDS}")
    print(f"平均耗时: {mean(times_ms):.2f} ms")
    print(f"最小耗时: {min(times_ms):.2f} ms")
    print(f"最大耗时: {max(times_ms):.2f} ms")
    print(f"P95耗时: {p95:.2f} ms")
    print(f"输出目录: {OUT_DIR}")


if __name__ == "__main__":
    main()
