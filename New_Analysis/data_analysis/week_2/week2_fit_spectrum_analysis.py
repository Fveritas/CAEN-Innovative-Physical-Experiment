#!/usr/bin/env python3
"""第二周衰减拟合与脉冲积分分布分析。

本脚本实现 WEEK_2_ANALYSIS_PLAN.md 中第二周系统诊断、建议图表和后续拟合：
1. 使用拟合前统计表中的 transmission 和 coin/hour 做经验指数拟合；
2. 对 area、area2 的全事件和符合事件分布进行统计；
3. 输出拟合参数表、脉冲积分统计表和补充图像。

注意：第二周数据存在明显系统效应可能，拟合结果只能作为经验趋势参考。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEEK_DIR = Path(__file__).resolve().parent
PROCESSED_NPZ_DIR = PROJECT_ROOT / "Processed_data" / "npz"
DEFAULT_RESULTS_DIR = WEEK_DIR / "results"

WEEK_RUNS = ["51811", "5185", "5186", "5187"]
AREA_THRESHOLD = 30.0
AREA2_THRESHOLD = 30.0


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(
        description="Fit week-2 attenuation and analyze pulse-integral spectra."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROCESSED_NPZ_DIR,
        help="Directory containing processed npz files.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory containing pre-fit table and receiving outputs.",
    )
    return parser.parse_args()


def ensure_output_dirs(results_dir: Path) -> dict[str, Path]:
    """创建拟合和能谱输出目录。"""

    paths = {
        "tables": results_dir / "tables",
        "figures": results_dir / "figures",
        "fit": results_dir / "fit",
        "spectrum": results_dir / "spectrum",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def attenuation_model(x: np.ndarray, lambda_eff: float) -> np.ndarray:
    """相对透过率指数衰减模型，0 片点固定为 1。"""

    return np.exp(-x / lambda_eff)


def rate_model(x: np.ndarray, r0: float, lambda_eff: float) -> np.ndarray:
    """绝对符合率指数衰减模型，单位为 counts/hour。"""

    return r0 * np.exp(-x / lambda_eff)


def fit_transmission(summary: pd.DataFrame) -> dict[str, float | str]:
    """使用 transmission 做带误差经验拟合。"""

    x = summary["lead_thickness_mm"].to_numpy(dtype=float)
    y = summary["transmission"].to_numpy(dtype=float)
    sigma = summary["sigma_transmission"].to_numpy(dtype=float)

    popt, pcov = curve_fit(
        attenuation_model,
        x,
        y,
        sigma=sigma,
        absolute_sigma=True,
        p0=[80.0],
        bounds=([1e-6], [np.inf]),
        maxfev=10000,
    )
    lambda_eff = float(popt[0])
    sigma_lambda = float(np.sqrt(pcov[0, 0])) if pcov.size else float("nan")

    y_fit = attenuation_model(x, lambda_eff)
    residual = y - y_fit
    chi2 = float(np.sum((residual / sigma) ** 2))
    ndf = int(len(x) - 1)
    chi2_ndf = chi2 / ndf if ndf > 0 else float("nan")

    return {
        "model": "Transmission(x) = exp(-x / lambda_eff)",
        "x_unit": "mm",
        "lambda_eff_mm": lambda_eff,
        "sigma_lambda_eff_mm": sigma_lambda,
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "note": "Week 2 fit is empirical because week-2 data show possible systematic effects.",
    }


def fit_coin_rate(summary: pd.DataFrame) -> dict[str, float | str]:
    """使用 R_coin(counts/hour) 做带误差经验拟合。"""

    x = summary["lead_thickness_mm"].to_numpy(dtype=float)
    y = summary["r_coin_per_hour"].to_numpy(dtype=float)
    sigma = summary["sigma_r_coin_per_hour"].to_numpy(dtype=float)

    popt, pcov = curve_fit(
        rate_model,
        x,
        y,
        sigma=sigma,
        absolute_sigma=True,
        p0=[float(y[0]), 80.0],
        bounds=([0.0, 1e-6], [np.inf, np.inf]),
        maxfev=10000,
    )
    r0, lambda_eff = [float(value) for value in popt]
    errors = np.sqrt(np.diag(pcov)) if pcov.size else [float("nan"), float("nan")]
    sigma_r0 = float(errors[0])
    sigma_lambda = float(errors[1])

    y_fit = rate_model(x, r0, lambda_eff)
    residual = y - y_fit
    chi2 = float(np.sum((residual / sigma) ** 2))
    ndf = int(len(x) - 2)
    chi2_ndf = chi2 / ndf if ndf > 0 else float("nan")

    return {
        "model": "R_coin(x) = R0 * exp(-x / lambda_eff)",
        "x_unit": "mm",
        "rate_unit": "counts/hour",
        "r0_counts_per_hour": r0,
        "sigma_r0_counts_per_hour": sigma_r0,
        "lambda_eff_mm": lambda_eff,
        "sigma_lambda_eff_mm": sigma_lambda,
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "note": "Week 2 coin/hour fit is empirical because week-2 data show possible systematic effects.",
    }


def plot_fit(summary: pd.DataFrame, fit_result: dict[str, float | str], out_dir: Path) -> None:
    """绘制 transmission 拟合图和残差图。"""

    x = summary["lead_thickness_mm"].to_numpy(dtype=float)
    y = summary["transmission"].to_numpy(dtype=float)
    sigma = summary["sigma_transmission"].to_numpy(dtype=float)
    lambda_eff = float(fit_result["lambda_eff_mm"])

    x_grid = np.linspace(0, max(x) * 1.05 if max(x) > 0 else 1, 300)
    y_grid = attenuation_model(x_grid, lambda_eff)
    y_fit = attenuation_model(x, lambda_eff)

    fig, (ax, ax_res) = plt.subplots(
        2,
        1,
        figsize=(7, 6),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    ax.errorbar(x, y, yerr=sigma, marker="o", linestyle="none", capsize=4, label="Data")
    ax.plot(x_grid, y_grid, "-", label=f"Fit lambda={lambda_eff:.2f} mm")
    ax.set_ylabel("Transmission")
    ax.set_title("Week 2 empirical attenuation fit")
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax_res.axhline(0, color="black", linewidth=1)
    ax_res.errorbar(x, y - y_fit, yerr=sigma, marker="o", linestyle="none", capsize=4)
    ax_res.set_xlabel("Lead thickness (mm)")
    ax_res.set_ylabel("Residual")
    ax_res.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "week2_attenuation_fit.png", dpi=200)
    plt.close(fig)


def plot_coin_rate_fit(
    summary: pd.DataFrame, fit_result: dict[str, float | str], out_dir: Path
) -> None:
    """绘制 coin/hour 拟合图和残差图。"""

    x = summary["lead_thickness_mm"].to_numpy(dtype=float)
    y = summary["r_coin_per_hour"].to_numpy(dtype=float)
    sigma = summary["sigma_r_coin_per_hour"].to_numpy(dtype=float)
    r0 = float(fit_result["r0_counts_per_hour"])
    lambda_eff = float(fit_result["lambda_eff_mm"])

    x_grid = np.linspace(0, max(x) * 1.05 if max(x) > 0 else 1, 300)
    y_grid = rate_model(x_grid, r0, lambda_eff)
    y_fit = rate_model(x, r0, lambda_eff)

    fig, (ax, ax_res) = plt.subplots(
        2,
        1,
        figsize=(7, 6),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    ax.errorbar(x, y, yerr=sigma, marker="o", linestyle="none", capsize=4, label="Data")
    ax.plot(
        x_grid,
        y_grid,
        "-",
        label=f"Fit R0={r0:.1f}/h, lambda={lambda_eff:.2f} mm",
    )
    ax.set_ylabel("Coincidence rate (counts/hour)")
    ax.set_title("Week 2 empirical coin/hour attenuation fit")
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax_res.axhline(0, color="black", linewidth=1)
    ax_res.errorbar(x, y - y_fit, yerr=sigma, marker="o", linestyle="none", capsize=4)
    ax_res.set_xlabel("Lead thickness (mm)")
    ax_res.set_ylabel("Residual")
    ax_res.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "week2_coin_rate_fit.png", dpi=200)
    plt.close(fig)


def load_npz(input_dir: Path, run: str) -> dict[str, np.ndarray]:
    """读取一个 npz 数据文件。"""

    path = input_dir / f"{run}.npz"
    if not path.exists():
        raise FileNotFoundError(path)
    with np.load(path) as data:
        return {key: data[key] for key in data.files}


def describe(values: np.ndarray) -> dict[str, float]:
    """给出一组脉冲积分的常用统计量。"""

    if len(values) == 0:
        return {
            "count": 0,
            "mean": float("nan"),
            "median": float("nan"),
            "std": float("nan"),
            "p10": float("nan"),
            "p90": float("nan"),
        }
    return {
        "count": int(len(values)),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "p10": float(np.percentile(values, 10)),
        "p90": float(np.percentile(values, 90)),
    }


def spectrum_table(input_dir: Path, summary: pd.DataFrame) -> pd.DataFrame:
    """统计每个 run 的全事件和符合事件 area/area2 分布。"""

    rows: list[dict[str, float | int | str]] = []
    for _, info in summary.sort_values("lead_plates").iterrows():
        run = str(info["run"])
        data = load_npz(input_dir, run)
        area = np.asarray(data["area"])
        area2 = np.asarray(data["area2"])
        coin = (area > AREA_THRESHOLD) & (area2 > AREA2_THRESHOLD)

        for detector, values in [
            ("area", area),
            ("area2", area2),
            ("area_coin", area[coin]),
            ("area2_coin", area2[coin]),
        ]:
            stats = describe(values)
            rows.append(
                {
                    "run": run,
                    "lead_plates": int(info["lead_plates"]),
                    "lead_thickness_mm": float(info["lead_thickness_mm"]),
                    "quantity": detector,
                    **stats,
                }
            )
    return pd.DataFrame(rows)


def plot_coin_spectra(input_dir: Path, summary: pd.DataFrame, out_dir: Path) -> None:
    """绘制符合事件中的 area 和 area2 叠加分布。"""

    bins = np.linspace(0, 120, 121)

    fig, ax = plt.subplots(figsize=(7, 5))
    for _, info in summary.sort_values("lead_plates").iterrows():
        run = str(info["run"])
        data = load_npz(input_dir, run)
        area = np.asarray(data["area"])
        area2 = np.asarray(data["area2"])
        coin = (area > AREA_THRESHOLD) & (area2 > AREA2_THRESHOLD)
        ax.hist(
            area[coin],
            bins=bins,
            histtype="step",
            density=True,
            label=f"{int(info['lead_plates'])} plates",
        )
    ax.axvline(AREA_THRESHOLD, color="black", linestyle=":", label="area=30")
    ax.set_xlabel("area for coincidence events")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Week 2 coincidence-event area spectra")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "week2_area_coin_spectrum.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    for _, info in summary.sort_values("lead_plates").iterrows():
        run = str(info["run"])
        data = load_npz(input_dir, run)
        area = np.asarray(data["area"])
        area2 = np.asarray(data["area2"])
        coin = (area > AREA_THRESHOLD) & (area2 > AREA2_THRESHOLD)
        ax.hist(
            area2[coin],
            bins=bins,
            histtype="step",
            density=True,
            label=f"{int(info['lead_plates'])} plates",
        )
    ax.axvline(AREA2_THRESHOLD, color="black", linestyle=":", label="area2=30")
    ax.set_xlabel("area2 for coincidence events")
    ax.set_ylabel("Normalized counts")
    ax.set_title("Week 2 coincidence-event area2 spectra")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "week2_area2_coin_spectrum.png", dpi=200)
    plt.close(fig)


def main() -> None:
    """脚本入口。"""

    args = parse_args()
    paths = ensure_output_dirs(args.results_dir)
    summary_path = paths["tables"] / "week2_pre_fit_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(f"Run week2_pre_fit_analysis.py first: {summary_path}")

    summary = pd.read_csv(summary_path, dtype={"run": str})
    transmission_fit = fit_transmission(summary)
    coin_rate_fit = fit_coin_rate(summary)
    fit_results = [transmission_fit, coin_rate_fit]
    pd.DataFrame(fit_results).to_csv(paths["fit"] / "week2_attenuation_fit.csv", index=False)
    (paths["fit"] / "week2_attenuation_fit.json").write_text(
        json.dumps(fit_results, indent=2),
        encoding="utf-8",
    )
    plot_fit(summary, transmission_fit, paths["fit"])
    plot_coin_rate_fit(summary, coin_rate_fit, paths["fit"])

    spec_df = spectrum_table(args.input_dir, summary)
    spec_df.to_csv(paths["spectrum"] / "week2_spectrum_summary.csv", index=False)
    plot_coin_spectra(args.input_dir, summary, paths["spectrum"])

    print("week 2 fit and spectrum analysis completed")
    print(f"fit result: {paths['fit'] / 'week2_attenuation_fit.csv'}")
    print(f"spectrum summary: {paths['spectrum'] / 'week2_spectrum_summary.csv'}")


if __name__ == "__main__":
    main()
