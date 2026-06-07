#!/usr/bin/env python3
"""跨周综合分析脚本。

本脚本实现 COMBINED_ANALYSIS_PLAN.md 中 1-6 节的分析：
1. 读取 Week 1 和 Week 2 的单周统计表；
2. 比较两周 0 片铅板基准；
3. 检查上下探测器通过率、Coin/Up、Coin/Down 和脉冲积分响应差异；
4. 分析可能的探测器响应漂移；
5. 使用 Coin/Up 乘以 Week 1 零铅板 N_up 构造上探测器归一化符合率；
6. 给出 0-60 片铅板的条件归一化综合趋势。
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEEK1_SUMMARY = PROJECT_ROOT / "data_analysis" / "week_1" / "results" / "tables" / "week1_pre_fit_summary.csv"
WEEK2_SUMMARY = PROJECT_ROOT / "data_analysis" / "week_2" / "results" / "tables" / "week2_pre_fit_summary.csv"
PROCESSED_NPZ_DIR = PROJECT_ROOT / "Processed_data" / "npz"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results"


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="Combined inter-week analysis.")
    parser.add_argument(
        "--week1-summary",
        type=Path,
        default=WEEK1_SUMMARY,
        help="Week 1 pre-fit summary CSV.",
    )
    parser.add_argument(
        "--week2-summary",
        type=Path,
        default=WEEK2_SUMMARY,
        help="Week 2 pre-fit summary CSV.",
    )
    parser.add_argument(
        "--npz-dir",
        type=Path,
        default=PROCESSED_NPZ_DIR,
        help="Directory containing processed npz files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for combined-analysis tables and figures.",
    )
    return parser.parse_args()


def ensure_output_dirs(output_dir: Path) -> dict[str, Path]:
    """创建综合分析输出目录。"""

    paths = {
        "tables": output_dir / "tables",
        "figures": output_dir / "figures",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def load_summaries(week1_path: Path, week2_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """读取两周单独分析得到的统计表。"""

    week1 = pd.read_csv(week1_path, dtype={"run": str})
    week2 = pd.read_csv(week2_path, dtype={"run": str})
    week1["week"] = 1
    week2["week"] = 2
    return week1, week2


def load_npz(npz_dir: Path, run: str) -> dict[str, np.ndarray]:
    """读取一个预处理 npz 文件，用于画 0 片基准分布。"""

    path = npz_dir / f"{run}.npz"
    if not path.exists():
        raise FileNotFoundError(path)
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def baseline_comparison(week1: pd.DataFrame, week2: pd.DataFrame) -> pd.DataFrame:
    """生成两周 0 片基准对比表。"""

    baseline1 = week1.loc[week1["lead_plates"] == 0].iloc[0]
    baseline2 = week2.loc[week2["lead_plates"] == 0].iloc[0]
    fields = [
        "run",
        "n_total",
        "n_up",
        "n_down",
        "n_coin",
        "r_coin_per_hour",
        "up_fraction",
        "down_fraction",
        "coin_fraction",
        "coin_over_up",
        "coin_over_down",
        "area_mean",
        "area2_mean",
        "area_median",
        "area2_median",
    ]
    rows = []
    for label, row in [("week1_baseline", baseline1), ("week2_baseline", baseline2)]:
        item = {"baseline": label}
        for field in fields:
            item[field] = row[field]
        rows.append(item)

    comparison = pd.DataFrame(rows)
    ratios = {"baseline": "week2_over_week1"}
    for field in fields:
        if field == "run":
            ratios[field] = f"{baseline2[field]}/{baseline1[field]}"
            continue
        denominator = baseline1[field]
        ratios[field] = baseline2[field] / denominator if denominator != 0 else np.nan
    return pd.concat([comparison, pd.DataFrame([ratios])], ignore_index=True)


def build_combined_table(week1: pd.DataFrame, week2: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """构建原始与 Coin/Up 归一化后的跨周综合表。"""

    baseline1 = week1.loc[week1["lead_plates"] == 0].iloc[0]
    baseline2 = week2.loc[week2["lead_plates"] == 0].iloc[0]
    reference_n_up = float(baseline1["n_up"])
    reference_n_coin = float(baseline1["n_coin"])
    zero_lead_coin_scale = (
        float(baseline1["r_coin_per_hour"]) / float(baseline2["r_coin_per_hour"])
    )

    combined = pd.concat([week1, week2], ignore_index=True).sort_values(
        ["lead_thickness_mm", "week", "run"]
    )
    combined["is_zero_lead_baseline"] = combined["lead_plates"] == 0
    combined["coin_up_reference_n_up"] = reference_n_up
    combined["r_coin_up_normalized_to_week1"] = (
        combined["coin_over_up"] * reference_n_up
    )
    combined["sigma_r_coin_up_normalized_to_week1"] = (
        combined["sigma_coin_over_up"] * reference_n_up
    )
    combined["coin_up_normalized_transmission_to_week1"] = (
        combined["r_coin_up_normalized_to_week1"] / reference_n_coin
    )
    combined["coin_up_normalized_blocking_to_week1"] = (
        1.0 - combined["coin_up_normalized_transmission_to_week1"]
    )
    combined["zero_lead_coin_scale_factor"] = np.where(
        combined["week"] == 2, zero_lead_coin_scale, 1.0
    )
    combined["r_coin_up_normalized_then_scaled"] = (
        combined["r_coin_up_normalized_to_week1"]
        * combined["zero_lead_coin_scale_factor"]
    )
    combined["sigma_r_coin_up_normalized_then_scaled"] = (
        combined["sigma_r_coin_up_normalized_to_week1"]
        * combined["zero_lead_coin_scale_factor"]
    )
    combined["coin_up_normalized_then_scaled_transmission"] = (
        combined["r_coin_up_normalized_then_scaled"] / reference_n_coin
    )
    combined["coin_up_normalized_then_scaled_blocking"] = (
        1.0 - combined["coin_up_normalized_then_scaled_transmission"]
    )
    combined["week_label"] = combined["week"].map({1: "Week 1", 2: "Week 2"})
    return combined, reference_n_up


def normalization_comparison(combined: pd.DataFrame) -> pd.DataFrame:
    """比较原始符合率和 Coin/Up 归一化结果。"""

    columns = [
        "week",
        "run",
        "lead_plates",
        "lead_thickness_mm",
        "r_coin_per_hour",
        "coin_over_up",
        "r_coin_up_normalized_to_week1",
        "coin_up_normalized_transmission_to_week1",
        "coin_up_normalized_blocking_to_week1",
        "zero_lead_coin_scale_factor",
        "r_coin_up_normalized_then_scaled",
        "coin_up_normalized_then_scaled_transmission",
        "coin_up_normalized_then_scaled_blocking",
        "coin_over_down",
        "area_mean",
        "area2_mean",
    ]
    return combined[columns].sort_values(["lead_thickness_mm", "week"])


def plot_baseline_spectra(npz_dir: Path, figure_dir: Path) -> None:
    """绘制两周 0 片基准的 area 和 area2 分布对比。"""

    week1 = load_npz(npz_dir, "5181")
    week2 = load_npz(npz_dir, "51811")
    bins = np.linspace(0, 120, 121)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(week1["area"], bins=bins, histtype="step", density=True, label="Week 1: 5181")
    ax.hist(week2["area"], bins=bins, histtype="step", density=True, label="Week 2: 51811")
    ax.axvline(30, color="black", linestyle=":", label="area=30")
    ax.set_xlabel("area")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Zero-lead area distribution comparison")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "zero_lead_area_comparison.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(week1["area2"], bins=bins, histtype="step", density=True, label="Week 1: 5181")
    ax.hist(week2["area2"], bins=bins, histtype="step", density=True, label="Week 2: 51811")
    ax.axvline(30, color="black", linestyle=":", label="area2=30")
    ax.set_xlabel("area2")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Zero-lead area2 distribution comparison")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "zero_lead_area2_comparison.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharex=True, sharey=True)
    for ax, data, title in [
        (axes[0], week1, "Week 1: 5181"),
        (axes[1], week2, "Week 2: 51811"),
    ]:
        hist = ax.hist2d(
            data["area"],
            data["area2"],
            bins=100,
            range=[[0, 120], [0, 120]],
            cmap="Reds",
            vmin=0,
        )
        ax.axvline(30, color="black", linestyle=":")
        ax.axhline(30, color="black", linestyle=":")
        ax.set_title(title)
        ax.set_xlabel("area")
        fig.colorbar(hist[3], ax=ax, label="Counts")
    axes[0].set_ylabel("area2")
    fig.suptitle("Zero-lead area vs area2 comparison")
    fig.tight_layout()
    fig.savefig(figure_dir / "zero_lead_area_vs_area2_comparison.png", dpi=200)
    plt.close(fig)


def plot_detector_diagnostics(combined: pd.DataFrame, figure_dir: Path) -> None:
    """绘制上下探测器通过率和归一化符合比的跨周诊断图。"""

    x = combined["lead_thickness_mm"]
    marker = {1: "o", 2: "s"}

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.plot(
            group["lead_thickness_mm"],
            group["up_fraction"],
            marker=marker[week],
            linestyle="-",
            label=f"Week {week} Up pass",
        )
        ax.plot(
            group["lead_thickness_mm"],
            group["down_fraction"],
            marker=marker[week],
            linestyle="--",
            label=f"Week {week} Down pass",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Pass fraction")
    ax.set_title("Detector threshold pass fractions")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "detector_pass_fraction_comparison.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.errorbar(
            group["lead_thickness_mm"],
            group["coin_over_up"],
            yerr=group["sigma_coin_over_up"],
            marker=marker[week],
            linestyle="-",
            capsize=4,
            label=f"Week {week} Coin/Up",
        )
        ax.errorbar(
            group["lead_thickness_mm"],
            group["coin_over_down"],
            yerr=group["sigma_coin_over_down"],
            marker=marker[week],
            linestyle="--",
            capsize=4,
            label=f"Week {week} Coin/Down",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Conditional coincidence ratio")
    ax.set_title("Conditional coincidence ratios")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "conditional_coin_ratio_comparison.png", dpi=200)
    plt.close(fig)


def plot_combined_rates(combined: pd.DataFrame, figure_dir: Path) -> None:
    """绘制原始和 Coin/Up 归一化后的跨周符合率。"""

    marker = {1: "o", 2: "s"}

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.errorbar(
            group["lead_thickness_mm"],
            group["r_coin_per_hour"],
            yerr=group["sigma_r_coin_per_hour"],
            marker=marker[week],
            linestyle="none",
            capsize=4,
            label=f"Week {week}",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Raw coincidence rate (counts/hour)")
    ax.set_title("Raw cross-week rates (diagnostic only)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "raw_coin_rate_combined.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.errorbar(
            group["lead_thickness_mm"],
            group["r_coin_up_normalized_to_week1"],
            yerr=group["sigma_r_coin_up_normalized_to_week1"],
            marker=marker[week],
            linestyle="none",
            capsize=4,
            label=f"Week {week}",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Coin/Up normalized rate (counts/hour)")
    ax.set_title("Coin/Up normalized cross-week rates")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "coin_up_normalized_rate_combined.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.plot(
            group["lead_thickness_mm"],
            group["coin_up_normalized_transmission_to_week1"],
            marker=marker[week],
            linestyle="none",
            label=f"Week {week}",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Coin/Up normalized transmission to Week 1 baseline")
    ax.set_title("Coin/Up normalized 0-60 plate effective transmission")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "coin_up_normalized_transmission_combined.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.errorbar(
            group["lead_thickness_mm"],
            group["r_coin_up_normalized_then_scaled"],
            yerr=group["sigma_r_coin_up_normalized_then_scaled"],
            marker=marker[week],
            linestyle="none",
            capsize=4,
            label=f"Week {week}",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Coin/Up normalized then scaled rate (counts/hour)")
    ax.set_title("Coin/Up normalized rates with zero-lead scale applied")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        figure_dir / "coin_up_normalized_then_scaled_rate_combined.png", dpi=200
    )
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.plot(
            group["lead_thickness_mm"],
            group["coin_up_normalized_then_scaled_transmission"],
            marker=marker[week],
            linestyle="none",
            label=f"Week {week}",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Normalized then scaled transmission")
    ax.set_title("Coin/Up normalized transmission with zero-lead scale applied")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(
        figure_dir / "coin_up_normalized_then_scaled_transmission_combined.png",
        dpi=200,
    )
    plt.close(fig)


def plot_week_transmission(combined: pd.DataFrame, figure_dir: Path) -> None:
    """绘制分周各自归一化的 Transmission 对比。"""

    marker = {1: "o", 2: "s"}
    fig, ax = plt.subplots(figsize=(7, 5))
    for week, group in combined.groupby("week"):
        ax.errorbar(
            group["lead_thickness_mm"],
            group["transmission"],
            yerr=group["sigma_transmission"],
            marker=marker[week],
            linestyle="none",
            capsize=4,
            label=f"Week {week}",
        )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Within-week transmission")
    ax.set_title("Separate within-week transmission curves")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week_transmission_comparison.png", dpi=200)
    plt.close(fig)


def main() -> None:
    """脚本入口。"""

    args = parse_args()
    paths = ensure_output_dirs(args.output_dir)
    week1, week2 = load_summaries(args.week1_summary, args.week2_summary)

    baseline = baseline_comparison(week1, week2)
    baseline.to_csv(paths["tables"] / "baseline_comparison.csv", index=False)

    combined, reference_n_up = build_combined_table(week1, week2)
    combined.to_csv(
        paths["tables"] / "combined_coin_up_normalized_summary.csv", index=False
    )

    norm = normalization_comparison(combined)
    norm.to_csv(paths["tables"] / "normalization_comparison.csv", index=False)

    plot_baseline_spectra(args.npz_dir, paths["figures"])
    plot_detector_diagnostics(combined, paths["figures"])
    plot_combined_rates(combined, paths["figures"])
    plot_week_transmission(combined, paths["figures"])

    print("combined inter-week analysis completed")
    print(f"Coin/Up reference N_up from Week 1 zero lead: {reference_n_up:.0f}")
    print(f"tables: {paths['tables']}")
    print(f"figures: {paths['figures']}")


if __name__ == "__main__":
    main()
