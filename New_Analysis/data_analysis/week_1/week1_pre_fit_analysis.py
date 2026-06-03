#!/usr/bin/env python3
"""第一周衰减拟合前的数据分析脚本。

本脚本只完成指数衰减拟合之前的工作：
1. 读取第一周 5181-5184 的预处理 npz 数据；
2. 计算固定阈值下的基础计数、符合率、归一化符合比；
3. 计算相对透过率和有效阻挡能力；
4. 生成基础统计表和诊断图。

注意：本脚本不进行指数衰减拟合。拟合应在确认基础统计和图像合理后，
由后续脚本单独完成。
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_NPZ_DIR = PROJECT_ROOT / "Processed_data" / "npz"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results"

# 第一周只包含 0、10、20、30 片铅板数据。
WEEK1_RUNS = ["5181", "5182", "5183", "5184"]

# 本实验报告统一使用固定阈值，不做其他阈值扫描。
AREA_THRESHOLD = 30.0
AREA2_THRESHOLD = 30.0

# 每个 run 测量时间取 1 小时，时间不确定度取 1 分钟。
MEASUREMENT_TIME_S = 3600.0
MEASUREMENT_TIME_UNCERTAINTY_S = 60.0


@dataclass
class RunStats:
    """单个 run 的统计结果，最终会写入 CSV。"""

    run: str
    lead_plates: int
    lead_thickness_mm: float
    radiation_lengths: float
    mass_thickness_g_cm2: float
    n_total: int
    n_up: int
    n_down: int
    n_coin: int
    r_coin_per_hour: float
    r_coin_hz: float
    sigma_r_coin_per_hour: float
    sigma_r_coin_hz: float
    up_fraction: float
    down_fraction: float
    coin_fraction: float
    coin_over_up: float
    sigma_coin_over_up: float
    coin_over_down: float
    sigma_coin_over_down: float
    transmission: float
    sigma_transmission: float
    blocking: float
    sigma_blocking: float
    area_mean: float
    area2_mean: float
    area_median: float
    area2_median: float


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Run pre-fit analysis for week-1 cosmic-ray lead data."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROCESSED_NPZ_DIR,
        help="Directory containing processed npz files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for CSV tables and figures.",
    )
    return parser.parse_args()


def ensure_output_dirs(output_dir: Path) -> dict[str, Path]:
    """创建输出目录，并返回各类输出路径。"""

    paths = {
        "tables": output_dir / "tables",
        "figures": output_dir / "figures",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def load_run(input_dir: Path, run: str) -> dict[str, np.ndarray]:
    """读取单个第一周 npz 文件。"""

    path = input_dir / f"{run}.npz"
    if not path.exists():
        raise FileNotFoundError(f"Missing processed file: {path}")

    with np.load(path) as data:
        return {name: data[name] for name in data.files}


def scalar_value(data: dict[str, np.ndarray], key: str, cast_type=float):
    """从 npz 的 run 级标量数组中取出 Python 标量。"""

    return cast_type(np.asarray(data[key]).item())


def rate_relative_error(n_coin: int) -> float:
    """符合率相对误差，包含泊松计数误差和 1 min 时间误差。"""

    if n_coin <= 0:
        return float("nan")
    time_term = MEASUREMENT_TIME_UNCERTAINTY_S / MEASUREMENT_TIME_S
    return float(np.sqrt(1.0 / n_coin + time_term**2))


def binomial_sigma(successes: int, trials: int) -> float:
    """二项比例误差，用于 Coin/Up 和 Coin/Down。"""

    if trials <= 0:
        return float("nan")
    p = successes / trials
    return float(np.sqrt(p * (1.0 - p) / trials))


def compute_basic_counts(data: dict[str, np.ndarray]) -> dict[str, int | np.ndarray]:
    """在固定阈值下计算上下探测器和符合事件。"""

    area = np.asarray(data["area"])
    area2 = np.asarray(data["area2"])
    up_mask = area > AREA_THRESHOLD
    down_mask = area2 > AREA2_THRESHOLD
    coin_mask = up_mask & down_mask

    return {
        "area": area,
        "area2": area2,
        "up_mask": up_mask,
        "down_mask": down_mask,
        "coin_mask": coin_mask,
        "n_total": int(len(area)),
        "n_up": int(np.count_nonzero(up_mask)),
        "n_down": int(np.count_nonzero(down_mask)),
        "n_coin": int(np.count_nonzero(coin_mask)),
    }


def compute_stats(
    run: str,
    data: dict[str, np.ndarray],
    baseline_n_coin: int,
) -> RunStats:
    """计算单个 run 的所有衰减拟合前统计量。"""

    counts = compute_basic_counts(data)
    area = counts["area"]
    area2 = counts["area2"]
    n_total = counts["n_total"]
    n_up = counts["n_up"]
    n_down = counts["n_down"]
    n_coin = counts["n_coin"]

    r_coin_hz = n_coin / MEASUREMENT_TIME_S
    r_coin_per_hour = n_coin
    rel_err_rate = rate_relative_error(n_coin)

    coin_over_up = n_coin / n_up if n_up else float("nan")
    coin_over_down = n_coin / n_down if n_down else float("nan")

    transmission = n_coin / baseline_n_coin if baseline_n_coin else float("nan")
    rel_err_transmission = float(
        np.sqrt(
            1.0 / n_coin
            + 1.0 / baseline_n_coin
            + 2.0 * (MEASUREMENT_TIME_UNCERTAINTY_S / MEASUREMENT_TIME_S) ** 2
        )
    )
    sigma_transmission = transmission * rel_err_transmission

    return RunStats(
        run=run,
        lead_plates=scalar_value(data, "lead_plates", int),
        lead_thickness_mm=scalar_value(data, "lead_thickness_mm", float),
        radiation_lengths=scalar_value(data, "radiation_lengths", float),
        mass_thickness_g_cm2=scalar_value(data, "mass_thickness_g_cm2", float),
        n_total=n_total,
        n_up=n_up,
        n_down=n_down,
        n_coin=n_coin,
        r_coin_per_hour=r_coin_per_hour,
        r_coin_hz=r_coin_hz,
        sigma_r_coin_per_hour=n_coin * rel_err_rate,
        sigma_r_coin_hz=r_coin_hz * rel_err_rate,
        up_fraction=n_up / n_total if n_total else float("nan"),
        down_fraction=n_down / n_total if n_total else float("nan"),
        coin_fraction=n_coin / n_total if n_total else float("nan"),
        coin_over_up=coin_over_up,
        sigma_coin_over_up=binomial_sigma(n_coin, n_up),
        coin_over_down=coin_over_down,
        sigma_coin_over_down=binomial_sigma(n_coin, n_down),
        transmission=transmission,
        sigma_transmission=sigma_transmission,
        blocking=1.0 - transmission,
        sigma_blocking=sigma_transmission,
        area_mean=float(np.mean(area)),
        area2_mean=float(np.mean(area2)),
        area_median=float(np.median(area)),
        area2_median=float(np.median(area2)),
    )


def write_stats_table(stats: list[RunStats], table_dir: Path) -> pd.DataFrame:
    """保存第一周基础统计表。"""

    df = pd.DataFrame([asdict(item) for item in stats])
    df = df.sort_values("lead_plates")
    output_path = table_dir / "week1_pre_fit_summary.csv"
    df.to_csv(output_path, index=False)
    print(f"wrote table: {output_path}")
    return df


def plot_rate_curves(df: pd.DataFrame, figure_dir: Path) -> None:
    """绘制符合率、透过率和阻挡能力曲线。"""

    x = df["lead_thickness_mm"]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(
        x,
        df["r_coin_per_hour"],
        yerr=df["sigma_r_coin_per_hour"],
        marker="o",
        linestyle="-",
        capsize=4,
    )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Coincidence rate (counts/hour)")
    ax.set_title("Week 1 coincidence rate before attenuation fit")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(figure_dir / "week1_coin_rate.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(
        x,
        df["transmission"],
        yerr=df["sigma_transmission"],
        marker="o",
        linestyle="-",
        capsize=4,
        label="Transmission",
    )
    ax.errorbar(
        x,
        df["blocking"],
        yerr=df["sigma_blocking"],
        marker="s",
        linestyle="--",
        capsize=4,
        label="Blocking",
    )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Relative value")
    ax.set_title("Week 1 effective transmission and blocking")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week1_transmission_blocking.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(
        x,
        df["coin_over_up"],
        yerr=df["sigma_coin_over_up"],
        marker="o",
        linestyle="-",
        capsize=4,
        label="Coin/Up",
    )
    ax.errorbar(
        x,
        df["coin_over_down"],
        yerr=df["sigma_coin_over_down"],
        marker="s",
        linestyle="--",
        capsize=4,
        label="Coin/Down",
    )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("Normalized coincidence ratio")
    ax.set_title("Week 1 normalized coincidence ratios")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week1_normalized_coin_ratios.png", dpi=200)
    plt.close(fig)


def plot_area_distributions(
    run_data: dict[str, dict[str, np.ndarray]], df: pd.DataFrame, figure_dir: Path
) -> None:
    """绘制 area、area2 的一维分布以及二维诊断图。"""

    bins = np.linspace(0, 120, 121)

    fig, ax = plt.subplots(figsize=(7, 5))
    for _, row in df.iterrows():
        run = row["run"]
        area = np.asarray(run_data[run]["area"])
        ax.hist(
            area,
            bins=bins,
            histtype="step",
            density=True,
            label=f"{int(row['lead_plates'])} plates",
        )
    ax.axvline(AREA_THRESHOLD, color="black", linestyle=":", label="area=30")
    ax.set_xlabel("area")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Week 1 area distributions")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week1_area_distribution.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for _, row in df.iterrows():
        run = row["run"]
        area2 = np.asarray(run_data[run]["area2"])
        ax.hist(
            area2,
            bins=bins,
            histtype="step",
            density=True,
            label=f"{int(row['lead_plates'])} plates",
        )
    ax.axvline(AREA2_THRESHOLD, color="black", linestyle=":", label="area2=30")
    ax.set_xlabel("area2")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Week 1 area2 distributions")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "week1_area2_distribution.png", dpi=200)
    plt.close(fig)

    for _, row in df.iterrows():
        run = row["run"]
        area = np.asarray(run_data[run]["area"])
        area2 = np.asarray(run_data[run]["area2"])

        fig, ax = plt.subplots(figsize=(6, 5))
        hist = ax.hist2d(area, area2, bins=100, range=[[0, 120], [0, 120]], cmap="viridis")
        ax.axvline(AREA_THRESHOLD, color="white", linestyle=":")
        ax.axhline(AREA2_THRESHOLD, color="white", linestyle=":")
        ax.set_xlabel("area")
        ax.set_ylabel("area2")
        ax.set_title(f"Week 1 area vs area2: run {run}")
        fig.colorbar(hist[3], ax=ax, label="Counts")
        fig.tight_layout()
        fig.savefig(figure_dir / f"week1_area_vs_area2_{run}.png", dpi=200)
        plt.close(fig)


def main() -> None:
    """脚本入口。"""

    args = parse_args()
    output_paths = ensure_output_dirs(args.output_dir)

    run_data = {run: load_run(args.input_dir, run) for run in WEEK1_RUNS}
    baseline_counts = compute_basic_counts(run_data["5181"])
    baseline_n_coin = int(baseline_counts["n_coin"])

    stats = [
        compute_stats(run, run_data[run], baseline_n_coin)
        for run in WEEK1_RUNS
    ]
    df = write_stats_table(stats, output_paths["tables"])

    plot_rate_curves(df, output_paths["figures"])
    plot_area_distributions(run_data, df, output_paths["figures"])

    print("week 1 pre-fit analysis completed")
    print(f"figures: {output_paths['figures']}")
    print(f"tables: {output_paths['tables']}")


if __name__ == "__main__":
    main()
