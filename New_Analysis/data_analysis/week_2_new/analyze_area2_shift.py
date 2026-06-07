#!/usr/bin/env python3
"""分析第二周 area2 分布是否相对第一周发生明显左移。

本脚本专门回答一个问题：
第二周下探测器脉冲积分 area2 是否相对第一周 0 片基准明显变小？

输出内容：
1. 每个 run 的 area2 均值、中位数、分位数、阈值通过率；
2. 第二周各 run 与第一周 0 片基准的差值和比例；
3. Kolmogorov-Smirnov 检验结果；
4. area2 直方图、ECDF、箱线图和阈值通过率图。
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = PROJECT_ROOT / "Processed_data" / "npz"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results"

# 第一周 0 片数据作为“正常响应”参考；第二周 51811 是第二周 0 片基准。
REFERENCE_RUN = "5181"
WEEK2_RUNS = ["51811", "5185", "5186", "5187"]
ALL_RUNS = [REFERENCE_RUN, *WEEK2_RUNS]

# 报告中统一使用的下探测器阈值。
AREA2_THRESHOLD = 30.0


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="Analyze week-2 area2 left shift.")
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
        help="Directory for output tables and figures.",
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


def load_npz(input_dir: Path, run: str) -> dict[str, np.ndarray]:
    """读取单个 run 的 npz 数据。"""

    path = input_dir / f"{run}.npz"
    if not path.exists():
        raise FileNotFoundError(f"Missing processed data: {path}")
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def scalar(data: dict[str, np.ndarray], key: str, default=np.nan):
    """从 npz 的标量字段中提取 Python 标量。"""

    if key not in data:
        return default
    value = np.asarray(data[key])
    if value.shape == ():
        return value.item()
    return default


def trimmed_mean(values: np.ndarray, fraction: float = 0.05) -> float:
    """计算截尾均值，降低极端大脉冲对均值的影响。"""

    values = np.sort(values[np.isfinite(values)])
    if values.size == 0:
        return float("nan")
    cut = int(values.size * fraction)
    if cut == 0 or 2 * cut >= values.size:
        return float(np.mean(values))
    return float(np.mean(values[cut:-cut]))


def ks_2sample(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """两样本 Kolmogorov-Smirnov 检验。

    优先使用 scipy；如果当前环境没有 scipy，则使用渐近公式近似 p 值。
    """

    try:
        from scipy.stats import ks_2samp

        result = ks_2samp(x, y, alternative="two-sided", method="auto")
        return float(result.statistic), float(result.pvalue)
    except Exception:
        x = np.sort(x[np.isfinite(x)])
        y = np.sort(y[np.isfinite(y)])
        if x.size == 0 or y.size == 0:
            return float("nan"), float("nan")
        values = np.sort(np.concatenate([x, y]))
        cdf_x = np.searchsorted(x, values, side="right") / x.size
        cdf_y = np.searchsorted(y, values, side="right") / y.size
        d_stat = float(np.max(np.abs(cdf_x - cdf_y)))
        n_eff = x.size * y.size / (x.size + y.size)
        # 常用渐近近似：p ~= 2 exp(-2 lambda^2)，只作为无 scipy 时的备选。
        lam = (math.sqrt(n_eff) + 0.12 + 0.11 / math.sqrt(n_eff)) * d_stat
        p_value = min(1.0, 2.0 * math.exp(-2.0 * lam * lam))
        return d_stat, float(p_value)


def summarize_run(data: dict[str, np.ndarray]) -> dict[str, float | int | str]:
    """计算单个 run 的 area2 分布统计量。"""

    area2 = np.asarray(data["area2"], dtype=float)
    finite = area2[np.isfinite(area2)]
    passed = finite > AREA2_THRESHOLD

    return {
        "run": str(scalar(data, "run")),
        "week": int(scalar(data, "week")),
        "lead_plates": int(scalar(data, "lead_plates")),
        "lead_thickness_mm": float(scalar(data, "lead_thickness_mm")),
        "n_events": int(finite.size),
        "area2_mean": float(np.mean(finite)),
        "area2_std": float(np.std(finite, ddof=1)),
        "area2_sem": float(np.std(finite, ddof=1) / math.sqrt(finite.size)),
        "area2_trimmed_mean_5pct": trimmed_mean(finite, 0.05),
        "area2_median": float(np.median(finite)),
        "area2_q05": float(np.quantile(finite, 0.05)),
        "area2_q25": float(np.quantile(finite, 0.25)),
        "area2_q75": float(np.quantile(finite, 0.75)),
        "area2_q95": float(np.quantile(finite, 0.95)),
        "area2_pass_count_gt30": int(np.count_nonzero(passed)),
        "area2_pass_fraction_gt30": float(np.mean(passed)),
    }


def build_tables(input_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    """生成统计表和相对第一周基准的差异表。"""

    datasets = {run: load_npz(input_dir, run) for run in ALL_RUNS}
    summary = pd.DataFrame([summarize_run(datasets[run]) for run in ALL_RUNS])

    reference = datasets[REFERENCE_RUN]["area2"].astype(float)
    ref_stats = summary.loc[summary["run"] == REFERENCE_RUN].iloc[0]

    comparisons = []
    for run in WEEK2_RUNS:
        row = summary.loc[summary["run"] == run].iloc[0]
        d_stat, p_value = ks_2sample(reference, datasets[run]["area2"].astype(float))
        comparisons.append(
            {
                "reference_run": REFERENCE_RUN,
                "run": run,
                "lead_plates": int(row["lead_plates"]),
                "lead_thickness_mm": float(row["lead_thickness_mm"]),
                "delta_mean_vs_5181": row["area2_mean"] - ref_stats["area2_mean"],
                "mean_ratio_vs_5181": row["area2_mean"] / ref_stats["area2_mean"],
                "delta_median_vs_5181": row["area2_median"] - ref_stats["area2_median"],
                "median_ratio_vs_5181": row["area2_median"] / ref_stats["area2_median"],
                "delta_q25_vs_5181": row["area2_q25"] - ref_stats["area2_q25"],
                "delta_q75_vs_5181": row["area2_q75"] - ref_stats["area2_q75"],
                "delta_pass_fraction_gt30_vs_5181": (
                    row["area2_pass_fraction_gt30"] - ref_stats["area2_pass_fraction_gt30"]
                ),
                "pass_fraction_ratio_vs_5181": (
                    row["area2_pass_fraction_gt30"] / ref_stats["area2_pass_fraction_gt30"]
                ),
                "ks_statistic_vs_5181": d_stat,
                "ks_pvalue_vs_5181": p_value,
            }
        )

    return summary, pd.DataFrame(comparisons), datasets


def ecdf(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """计算经验分布函数。"""

    x = np.sort(values[np.isfinite(values)])
    y = np.arange(1, x.size + 1) / x.size
    return x, y


def plot_histograms(datasets: dict[str, dict[str, np.ndarray]], figure_dir: Path) -> None:
    """绘制 area2 归一化直方图。"""

    bins = np.linspace(-10, 120, 131)
    labels = {
        "5181": "Week 1 0 plates: 5181",
        "51811": "Week 2 0 plates: 51811",
        "5185": "Week 2 40 plates: 5185",
        "5186": "Week 2 50 plates: 5186",
        "5187": "Week 2 60 plates: 5187",
    }

    fig, ax = plt.subplots(figsize=(8, 5.4))
    for run in ALL_RUNS:
        ax.hist(
            datasets[run]["area2"],
            bins=bins,
            histtype="step",
            density=True,
            linewidth=1.7,
            label=labels[run],
        )
    ax.axvline(AREA2_THRESHOLD, color="black", linestyle=":", linewidth=1.5, label="area2 = 30")
    ax.set_xlabel("area2")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Area2 distribution: Week 2 vs Week 1 reference")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(figure_dir / "area2_distribution_week2_vs_week1.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.4))
    for run in [REFERENCE_RUN, "51811"]:
        ax.hist(
            datasets[run]["area2"],
            bins=bins,
            histtype="step",
            density=True,
            linewidth=2.0,
            label=labels[run],
        )
    ax.axvline(AREA2_THRESHOLD, color="black", linestyle=":", linewidth=1.5, label="area2 = 30")
    ax.set_xlabel("area2")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Zero-lead area2 baseline comparison")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "area2_zero_lead_left_shift.png", dpi=220)
    plt.close(fig)


def plot_ecdf_and_box(summary: pd.DataFrame, datasets: dict[str, dict[str, np.ndarray]], figure_dir: Path) -> None:
    """绘制 ECDF、箱线图和通过率图。"""

    labels = [f"{run}\n{int(summary.loc[summary['run'] == run, 'lead_plates'].iloc[0])} plates" for run in ALL_RUNS]

    fig, ax = plt.subplots(figsize=(8, 5.4))
    for run in ALL_RUNS:
        x, y = ecdf(datasets[run]["area2"].astype(float))
        ax.plot(x, y, linewidth=1.8, label=run)
    ax.axvline(AREA2_THRESHOLD, color="black", linestyle=":", linewidth=1.5, label="area2 = 30")
    ax.set_xlim(-10, 120)
    ax.set_xlabel("area2")
    ax.set_ylabel("ECDF")
    ax.set_title("Area2 empirical cumulative distributions")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "area2_ecdf_week2_vs_week1.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.4))
    values = [datasets[run]["area2"].astype(float) for run in ALL_RUNS]
    ax.boxplot(values, tick_labels=labels, showfliers=False)
    ax.axhline(AREA2_THRESHOLD, color="black", linestyle=":", linewidth=1.5, label="area2 = 30")
    ax.set_ylabel("area2")
    ax.set_title("Area2 distribution boxplot without outliers")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "area2_boxplot_week2_vs_week1.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5.2))
    x = np.arange(len(summary))
    ax.bar(x, summary["area2_pass_fraction_gt30"], color=["tab:blue", *["tab:orange"] * 4])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, max(0.05, summary["area2_pass_fraction_gt30"].max() * 1.2))
    ax.set_ylabel("Fraction with area2 > 30")
    ax.set_title("Area2 threshold pass fraction")
    ax.grid(True, axis="y", alpha=0.3)
    for i, value in enumerate(summary["area2_pass_fraction_gt30"]):
        ax.text(i, value, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(figure_dir / "area2_pass_fraction_gt30.png", dpi=220)
    plt.close(fig)


def write_readme(summary: pd.DataFrame, comparison: pd.DataFrame, output_dir: Path) -> None:
    """写入中文 README，总结本轮分析结论。"""

    ref = summary.loc[summary["run"] == REFERENCE_RUN].iloc[0]
    w2_zero = summary.loc[summary["run"] == "51811"].iloc[0]
    comp_zero = comparison.loc[comparison["run"] == "51811"].iloc[0]

    readme = f"""# Week 2 New: area2 左移分析

本目录专门分析第二周下探测器脉冲积分 `area2` 是否相对第一周发生明显左移。

## 分析对象

- 第一周参考基准：`5181`，0 片铅板。
- 第二周数据：`51811`、`5185`、`5186`、`5187`，分别对应 0、40、50、60 片铅板。
- 固定阈值：`area2 > 30`。

## 主要结论

第二周 `area2` 相对第一周 0 片基准存在明显左移。最直接的 0 片对比为：

- `5181` 的 `area2` 均值：{ref['area2_mean']:.3f}
- `51811` 的 `area2` 均值：{w2_zero['area2_mean']:.3f}
- 均值差：{comp_zero['delta_mean_vs_5181']:.3f}
- 均值比例：{comp_zero['mean_ratio_vs_5181']:.3f}
- `5181` 的 `area2` 中位数：{ref['area2_median']:.3f}
- `51811` 的 `area2` 中位数：{w2_zero['area2_median']:.3f}
- 中位数差：{comp_zero['delta_median_vs_5181']:.3f}
- `area2 > 30` 通过率从 {ref['area2_pass_fraction_gt30']:.3f} 下降到 {w2_zero['area2_pass_fraction_gt30']:.3f}
- KS 检验统计量：{comp_zero['ks_statistic_vs_5181']:.3f}
- KS 检验 p 值：{comp_zero['ks_pvalue_vs_5181']:.3e}

这些量共同说明：第二周下探测器的脉冲积分分布不仅均值降低，而且整体分布相对第一周向低 `area2` 区域移动。因此，第二周固定阈值 `area2 > 30` 对下探测器更严格，会显著降低第二周的有效符合效率。

## 输出文件

### 表格

- `results/tables/area2_shift_summary.csv`：每个 run 的 `area2` 分布统计量。
- `results/tables/area2_shift_comparison_vs_5181.csv`：第二周各 run 相对第一周 0 片基准的差值、比例和 KS 检验。

### 图像

- `results/figures/area2_zero_lead_left_shift.png`：第一周 0 片和第二周 0 片的 `area2` 分布直接对比。
- `results/figures/area2_distribution_week2_vs_week1.png`：第一周参考和第二周全部 run 的 `area2` 分布对比。
- `results/figures/area2_ecdf_week2_vs_week1.png`：经验累积分布函数，用于观察整体分布左移。
- `results/figures/area2_boxplot_week2_vs_week1.png`：箱线图，展示中位数和四分位范围变化。
- `results/figures/area2_pass_fraction_gt30.png`：`area2 > 30` 阈值通过率对比。
"""

    (output_dir.parent / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    """主函数。"""

    args = parse_args()
    paths = ensure_dirs(args.output_dir)
    summary, comparison, datasets = build_tables(args.input_dir)

    summary.to_csv(paths["tables"] / "area2_shift_summary.csv", index=False)
    comparison.to_csv(paths["tables"] / "area2_shift_comparison_vs_5181.csv", index=False)

    plot_histograms(datasets, paths["figures"])
    plot_ecdf_and_box(summary, datasets, paths["figures"])
    write_readme(summary, comparison, args.output_dir)

    print("Area2 shift analysis complete.")
    print(f"Summary table: {paths['tables'] / 'area2_shift_summary.csv'}")
    print(f"Comparison table: {paths['tables'] / 'area2_shift_comparison_vs_5181.csv'}")
    print(f"Figures: {paths['figures']}")


if __name__ == "__main__":
    main()
