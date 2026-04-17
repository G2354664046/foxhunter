from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

REPORT_DIR = Path(__file__).resolve().parent
INPUT_FILES = {
    "test1": REPORT_DIR / "test1_stats_history.csv",
    "test2": REPORT_DIR / "test2_stats_history.csv",
}
DISPLAY_LABELS = {
    "test1": "加压测试",
    "test2": "基准测试",
}
SLA_MS = 200  # 可按需修改，设置为 None 则不画 SLA 线

# 中文显示配置（按顺序回退，尽量兼容 Windows/macOS/Linux）
plt.rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei"
]
plt.rcParams["axes.unicode_minus"] = False


def load_locust_history(csv_path: Path) -> pd.DataFrame:
    """
    读取 locust stats_history.csv，并做基础清洗：
    - 只保留 Aggregated 行
    - 去掉空行和 N/A
    - 将时间戳转换为可读时间
    """
    df = pd.read_csv(csv_path, skip_blank_lines=True)
    df = df[df["Name"] == "Aggregated"].copy()
    df = df.dropna(subset=["Timestamp"])

    # 时间轴：将 unix 时间戳转 datetime
    df["Timestamp"] = pd.to_numeric(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"])
    df["dt"] = pd.to_datetime(df["Timestamp"], unit="s")

    numeric_cols = [
        "User Count",
        "Requests/s",
        "Failures/s",
        "50%",
        "90%",
        "95%",
        "99%",
    ]
    # 数值化，N/A 转为 NaN
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _ordered_keys(data: dict[str, pd.DataFrame]) -> list[str]:
    return [k for k in ("test1", "test2") if k in data]


def _apply_common_style(ax: plt.Axes, title: str, y_label: str) -> None:
    ax.set_title(title)
    ax.set_xlabel("时间")
    ax.set_ylabel(y_label)
    ax.grid(True, linestyle="--", alpha=0.4)


def plot_experience_stability_combined(
    data: dict[str, pd.DataFrame],
    labels: dict[str, str],
    out_file: Path,
) -> None:
    """
    组合一：体验与稳定性图
    - X: 时间
    - Y: 响应时间(ms)
    - 线条: P50、P90、P95(主)、P99(辅助)、SLA水平线(可选)
    """
    keys = _ordered_keys(data)
    fig, axes = plt.subplots(len(keys), 1, figsize=(14, 10), sharex=False)
    if len(keys) == 1:
        axes = [axes]

    for idx, key in enumerate(keys):
        df = data[key]
        label = labels.get(key, key)
        ax = axes[idx]
        ax.plot(df["dt"], df["50%"], label="P50", color="#2ca02c", linewidth=1.6)
        ax.plot(df["dt"], df["90%"], label="P90", color="#9467bd", linewidth=1.6)
        ax.plot(df["dt"], df["95%"], label="P95", color="#1f77b4", linewidth=2.6)
        ax.plot(df["dt"], df["99%"], label="P99", color="#ff7f0e", linewidth=1.8)

        if SLA_MS is not None:
            ax.axhline(SLA_MS, color="red", linestyle="--", linewidth=1.8, label=f"SLA={SLA_MS}ms")
        _apply_common_style(ax, f"{label} - 百分位响应时间折线图", "响应时间 (ms)")
        ax.legend(loc="upper left")

    fig.suptitle("百分位响应时间折线图", fontsize=14)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def plot_pressure_throughput_combined(
    data: dict[str, pd.DataFrame],
    labels: dict[str, str],
    out_file: Path,
) -> None:
    """
    组合二：压力与吞吐量图
    - X: 时间
    - 左Y: 并发用户数(User Count)
    - 右Y: 吞吐量(Requests/s)
    """
    keys = _ordered_keys(data)
    fig, axes = plt.subplots(len(keys), 1, figsize=(14, 10), sharex=False)
    if len(keys) == 1:
        axes = [axes]

    for idx, key in enumerate(keys):
        df = data[key]
        label = labels.get(key, key)
        ax1 = axes[idx]
        ax2 = ax1.twinx()

        ax1.fill_between(
            df["dt"],
            df["User Count"],
            color="#9ecae1",
            alpha=0.45,
            label="并发用户数(User Count)",
        )
        ax1.plot(df["dt"], df["User Count"], color="#1f77b4", linewidth=2.2)
        ax2.plot(df["dt"], df["Requests/s"], color="#2ca02c", linewidth=2.6, label="吞吐量(Requests/s)")

        _apply_common_style(ax1, f"{label} - 压力与吞吐量折线图", "并发用户数")
        ax2.set_ylabel("吞吐量 (Requests/s)")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.suptitle("压力与吞吐量折线图", fontsize=14)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def plot_health_monitor_combined(
    data: dict[str, pd.DataFrame],
    labels: dict[str, str],
    out_file: Path,
) -> None:
    """
    组合三：健康度监控图
    - X: 时间
    - 左Y: RPS(Requests/s)
    - 右Y: Failures/s
    """
    keys = _ordered_keys(data)
    fig, axes = plt.subplots(len(keys), 1, figsize=(14, 10), sharex=False)
    if len(keys) == 1:
        axes = [axes]

    for idx, key in enumerate(keys):
        df = data[key]
        label = labels.get(key, key)
        ax1 = axes[idx]
        ax2 = ax1.twinx()

        ax1.plot(df["dt"], df["Requests/s"], color="#1f77b4", linewidth=2.6, label="总RPS(Requests/s)")
        ax2.fill_between(df["dt"], df["Failures/s"], color="#ff9896", alpha=0.4, label="Failures/s")
        ax2.plot(df["dt"], df["Failures/s"], color="#d62728", linewidth=2.1)

        _apply_common_style(ax1, f"{label} - RPS与失败速率折线图", "RPS (Requests/s)")
        ax2.set_ylabel("失败速率 (Failures/s)")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.suptitle("RPS与失败速率折线图", fontsize=14)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def plot_all() -> None:
    data = {key: load_locust_history(path) for key, path in INPUT_FILES.items()}
    labels = {key: DISPLAY_LABELS.get(key, key) for key in INPUT_FILES}

    plot_experience_stability_combined(
        data,
        labels,
        REPORT_DIR / "chart1_experience_stability_combined.png",
    )
    plot_pressure_throughput_combined(
        data,
        labels,
        REPORT_DIR / "chart2_pressure_throughput_combined.png",
    )
    plot_health_monitor_combined(
        data,
        labels,
        REPORT_DIR / "chart3_health_monitor_combined.png",
    )
    print("三张组合图已生成完毕。")


if __name__ == "__main__":
    plot_all()
