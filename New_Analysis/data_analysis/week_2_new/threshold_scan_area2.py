#!/usr/bin/env python3
"""扫描第二周 area2 阈值 30、25、20 对事件筛选的影响。

目标：
1. 保持上探测器阈值 area > 30 不变；
2. 将下探测器阈值 area2 分别设为 30、25、20；
3. 检查降低 area2 阈值后，有多少下探测器事件和符合事件被恢复；
4. 将输出保存到独立目录 results_threshold_scan，避免覆盖原有 area2 左移分析。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "Processed_data" / "npz"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results_threshold_scan"

WEEK2_RUNS = ["51811", "5185", "5186", "5187"]
AREA_THRESHOLD = 30.0
AREA2_THRESHOLDS = [30.0, 25.0, 20.0]


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="Scan area2 thresholds for week-2 data.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing processed npz files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for threshold scan results.",
    )
    return parser.parse_args()


def ensure_dirs(output_dir: Path) -> dict[str, Path]:
    """创建输出目录。"""

    paths = {
        "tables": output_dir / "tables",
        "figures": output_dir / "figures",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def load_run(input_dir: Path, run: str) -> dict[str, np.ndarray]:
    """读取一个 run 的 npz 数据。"""

    path = input_dir / f"{run}.npz"
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def scalar(data: dict[str, np.ndarray], key: str):
    """读取 npz 中的标量字段。"""

    return np.asarray(data[key]).item()


def summarize_thresholds(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """计算不同 area2 阈值下的下探测器通过数和符合数。"""

    rows = []
    recovered_rows = []

    for run in WEEK2_RUNS:
        data = load_run(input_dir, run)
        area = np.asarray(data["area"], dtype=float)
        area2 = np.asarray(data["area2"], dtype=float)
        up_mask = area > AREA_THRESHOLD
        n_total = len(area)
        n_up = int(np.count_nonzero(up_mask))

        run_rows = []
        for area2_threshold in AREA2_THRESHOLDS:
            down_mask = area2 > area2_threshold
            coin_mask = up_mask & down_mask
            n_down = int(np.count_nonzero(down_mask))
            n_coin = int(np.count_nonzero(coin_mask))
            row = {
                "run": run,
                "lead_plates": int(scalar(data, "lead_plates")),
                "lead_thickness_mm": float(scalar(data, "lead_thickness_mm")),
                "area_threshold": AREA_THRESHOLD,
                "area2_threshold": area2_threshold,
                "n_total": n_total,
                "n_up_area_gt30": n_up,
                "n_down_area2_gt_threshold": n_down,
                "n_coin": n_coin,
                "down_fraction": n_down / n_total,
                "coin_fraction": n_coin / n_total,
                "coin_over_up": n_coin / n_up if n_up else np.nan,
            }
            rows.append(row)
            run_rows.append(row)

        by_threshold = {row["area2_threshold"]: row for row in run_rows}
        baseline = by_threshold[30.0]
        for threshold in [25.0, 20.0]:
            current = by_threshold[threshold]
            recovered_rows.append(
                {
                    "run": run,
                    "lead_plates": int(scalar(data, "lead_plates")),
                    "lead_thickness_mm": float(scalar(data, "lead_thickness_mm")),
                    "baseline_area2_threshold": 30.0,
                    "new_area2_threshold": threshold,
                    "recovered_down_events": (
                        current["n_down_area2_gt_threshold"]
                        - baseline["n_down_area2_gt_threshold"]
                    ),
                    "recovered_coin_events": current["n_coin"] - baseline["n_coin"],
                    "relative_down_increase_vs_30": (
                        current["n_down_area2_gt_threshold"]
                        / baseline["n_down_area2_gt_threshold"]
                        - 1.0
                    ),
                    "relative_coin_increase_vs_30": current["n_coin"] / baseline["n_coin"] - 1.0,
                    "coin_over_up_increase_vs_30": (
                        current["coin_over_up"] - baseline["coin_over_up"]
                    ),
                }
            )

    return pd.DataFrame(rows), pd.DataFrame(recovered_rows)


def plot_threshold_counts(summary: pd.DataFrame, figure_dir: Path) -> None:
    """绘制不同阈值下的符合数和 Coin/Up。"""

    runs = WEEK2_RUNS
    x = np.arange(len(runs))
    width = 0.24
    colors = {30.0: "tab:red", 25.0: "tab:orange", 20.0: "tab:green"}

    fig, ax = plt.subplots(figsize=(8, 5.2))
    for i, threshold in enumerate(AREA2_THRESHOLDS):
        subset = summary[summary["area2_threshold"] == threshold].set_index("run").loc[runs]
        ax.bar(
            x + (i - 1) * width,
            subset["n_coin"],
            width=width,
            label=f"area2 > {threshold:g}",
            color=colors[threshold],
        )
    ax.set_xticks(x)
    ax.set_xticklabels(runs)
    ax.set_ylabel("Coincidence events")
    ax.set_title("Week 2 coincidence counts under different area2 thresholds")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week2_coin_counts_area2_threshold_scan.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.2))
    for i, threshold in enumerate(AREA2_THRESHOLDS):
        subset = summary[summary["area2_threshold"] == threshold].set_index("run").loc[runs]
        ax.bar(
            x + (i - 1) * width,
            subset["coin_over_up"],
            width=width,
            label=f"area2 > {threshold:g}",
            color=colors[threshold],
        )
    ax.set_xticks(x)
    ax.set_xticklabels(runs)
    ax.set_ylabel("Coin / Up")
    ax.set_title("Week 2 conditional coincidence ratio under area2 threshold scan")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week2_coin_over_up_area2_threshold_scan.png", dpi=220)
    plt.close(fig)


def plot_recovered_events(recovered: pd.DataFrame, figure_dir: Path) -> None:
    """绘制相对 area2>30 被恢复的符合事件数。"""

    runs = WEEK2_RUNS
    x = np.arange(len(runs))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5.2))
    for i, threshold in enumerate([25.0, 20.0]):
        subset = recovered[recovered["new_area2_threshold"] == threshold].set_index("run").loc[runs]
        values = subset["recovered_coin_events"].to_numpy()
        positions = x + (i - 0.5) * width
        bars = ax.bar(
            positions,
            values,
            width=width,
            label=f"30 -> {threshold:g}",
            edgecolor="black",
            linewidth=0.8,
        )
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                max(value, 0) + 0.04,
                f"{int(value)}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(runs)
    ax.set_ylim(0, max(2.5, recovered["recovered_coin_events"].max() * 1.35))
    ax.set_ylabel("Recovered coincidence events")
    ax.set_title("Coincidence events recovered by lowering area2 threshold")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(title="area2 threshold")
    fig.tight_layout()
    fig.savefig(figure_dir / "week2_recovered_coin_events.png", dpi=220)
    plt.close(fig)


def write_readme(summary: pd.DataFrame, recovered: pd.DataFrame, output_dir: Path) -> None:
    """写入中文说明文档。"""

    total_recovered_25 = int(recovered[recovered["new_area2_threshold"] == 25.0]["recovered_coin_events"].sum())
    total_recovered_20 = int(recovered[recovered["new_area2_threshold"] == 20.0]["recovered_coin_events"].sum())
    base_coin_total = int(summary[summary["area2_threshold"] == 30.0]["n_coin"].sum())
    coin_25_total = int(summary[summary["area2_threshold"] == 25.0]["n_coin"].sum())
    coin_20_total = int(summary[summary["area2_threshold"] == 20.0]["n_coin"].sum())

    text = f"""# Week 2 area2 阈值扫描

本目录检验第二周数据中，固定使用 `area2 > 30` 是否会筛掉一部分本来可能进入符合样本的事件。

## 阈值设置

- 上探测器阈值固定：`area > 30`
- 下探测器阈值扫描：`area2 > 30`、`area2 > 25`、`area2 > 20`
- 分析 run：`51811`、`5185`、`5186`、`5187`

## 主要结论

降低第二周 `area2` 阈值会恢复一部分符合事件，说明确实有事件处在 `20 < area2 <= 30` 或 `25 < area2 <= 30` 区间，在原来的 `area2 > 30` 标准下被筛掉。

- 使用 `area2 > 30` 时，第二周总符合数：{base_coin_total}
- 改为 `area2 > 25` 时，第二周总符合数：{coin_25_total}，恢复 {total_recovered_25} 个符合事件
- 改为 `area2 > 20` 时，第二周总符合数：{coin_20_total}，恢复 {total_recovered_20} 个符合事件

物理含义：第二周 `area2` 分布左移后，固定阈值 `area2 > 30` 会更强地压低下探测器通过率和符合率。把阈值降到 25 或 20 可以证明存在一批“被阈值筛掉”的事件，但这只是诊断探测器响应变化，不代表正式分析应随意改变阈值。

## 输出文件

### 表格

- `tables/week2_area2_threshold_scan_summary.csv`：每个 run 在三个阈值下的通过数、符合数和 Coin/Up。
- `tables/week2_area2_threshold_recovered_events.csv`：相对 `area2 > 30`，降到 25 或 20 后恢复的下探测器事件和符合事件数。

### 图像

- `figures/week2_coin_counts_area2_threshold_scan.png`：不同阈值下的符合事件数。
- `figures/week2_coin_over_up_area2_threshold_scan.png`：不同阈值下的 Coin/Up 条件符合比。
- `figures/week2_recovered_coin_events.png`：降低阈值后恢复的符合事件数。
"""

    (output_dir / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    """主函数。"""

    args = parse_args()
    paths = ensure_dirs(args.output_dir)
    summary, recovered = summarize_thresholds(args.input_dir)

    summary.to_csv(paths["tables"] / "week2_area2_threshold_scan_summary.csv", index=False)
    recovered.to_csv(paths["tables"] / "week2_area2_threshold_recovered_events.csv", index=False)

    plot_threshold_counts(summary, paths["figures"])
    plot_recovered_events(recovered, paths["figures"])
    write_readme(summary, recovered, args.output_dir)

    print("Threshold scan complete.")
    print(f"Output: {args.output_dir}")


if __name__ == "__main__":
    main()
