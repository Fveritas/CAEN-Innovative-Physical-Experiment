#!/usr/bin/env python3
"""Fit the Coin/Up-normalized and zero-lead-scaled combined curve.

The fitted quantity is produced by combined_week_analysis.py:

    R_scaled_norm = (N_coin / N_up) * N_up(5181) * k_week

where k_week is 1 for Week 1 and 3357/1831 for Week 2.  The Week 2
zero-lead point is excluded from the fit because it is the diagnostic point
used to define the inter-week scale factor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.interpolate import make_interp_spline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_DIR = Path(__file__).resolve().parent / "results"
DEFAULT_INPUT_TABLE = (
    DEFAULT_RESULTS_DIR / "tables" / "combined_coin_up_normalized_summary.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fit normalized-then-scaled combined attenuation curve."
    )
    parser.add_argument(
        "--input-table",
        type=Path,
        default=DEFAULT_INPUT_TABLE,
        help="Combined summary CSV from combined_week_analysis.py.",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Combined-analysis results directory.",
    )
    return parser.parse_args()


def ensure_output_dirs(results_dir: Path) -> dict[str, Path]:
    paths = {
        "fit": results_dir / "fit_normalized_scaled",
        "figures": results_dir / "figures",
        "tables": results_dir / "tables",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def attenuation_model(x: np.ndarray, lambda_eff: float) -> np.ndarray:
    return np.exp(-x / lambda_eff)


def rate_model(x: np.ndarray, r0: float, lambda_eff: float) -> np.ndarray:
    return r0 * np.exp(-x / lambda_eff)


def offset_exp_model(x: np.ndarray, offset: float, amplitude: float, lambda_eff: float) -> np.ndarray:
    return offset + amplitude * np.exp(-x / lambda_eff)


def r_squared(y: np.ndarray, y_fit: np.ndarray) -> float:
    """Unweighted R^2, used as a visual goodness-of-fit summary."""

    ss_res = float(np.sum((y - y_fit) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def smooth_xy(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return a smooth guide curve through the data points."""

    order = np.argsort(x)
    x_sorted = x[order]
    y_sorted = y[order]
    x_grid = np.linspace(float(np.min(x_sorted)), float(np.max(x_sorted)), 300)
    try:
        spline_degree = min(3, len(x_sorted) - 1)
        spline = make_interp_spline(x_sorted, y_sorted, k=spline_degree)
        return x_grid, spline(x_grid)
    except ValueError:
        return x_grid, np.interp(x_grid, x_sorted, y_sorted)


def add_fit_text(ax: plt.Axes, lines: list[str]) -> None:
    ax.text(
        0.03,
        0.05,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": "0.7", "alpha": 0.85},
    )


def prepare_fit_data(summary: pd.DataFrame) -> pd.DataFrame:
    """Select the 0-60 plate trend points and define fit uncertainties."""

    fit_df = summary.copy()
    fit_df["include_in_fit"] = ~(
        (fit_df["week"] == 2) & (fit_df["lead_plates"] == 0)
    )
    fit_df["fit_note"] = np.where(
        fit_df["include_in_fit"],
        "used in 0-60 plate trend fit",
        "excluded: Week 2 zero-lead diagnostic scale point",
    )

    rate = fit_df["r_coin_up_normalized_then_scaled"].astype(float)
    sigma_rate = fit_df["sigma_r_coin_up_normalized_then_scaled"].astype(float)
    reference_rate = float(
        fit_df.loc[(fit_df["week"] == 1) & (fit_df["lead_plates"] == 0), "n_coin"].iloc[0]
    )
    fit_df["transmission_normalized_then_scaled"] = rate / reference_rate
    fit_df["sigma_transmission_normalized_then_scaled"] = sigma_rate / reference_rate
    return fit_df


def chi2_result(y: np.ndarray, y_fit: np.ndarray, sigma: np.ndarray, npar: int) -> tuple[float, int, float]:
    residual = y - y_fit
    chi2 = float(np.sum((residual / sigma) ** 2))
    ndf = int(len(y) - npar)
    chi2_ndf = chi2 / ndf if ndf > 0 else float("nan")
    return chi2, ndf, chi2_ndf


def information_criteria(chi2: float, npoints: int, npar: int) -> tuple[float, float]:
    """AIC/BIC using chi2 as the weighted least-squares deviance proxy."""

    aic = chi2 + 2 * npar
    bic = chi2 + npar * np.log(npoints)
    return float(aic), float(bic)


def fit_transmission(fit_df: pd.DataFrame) -> dict[str, float | str]:
    data = fit_df.loc[fit_df["include_in_fit"]].copy()
    x = data["lead_thickness_mm"].to_numpy(dtype=float)
    y = data["transmission_normalized_then_scaled"].to_numpy(dtype=float)
    sigma = data["sigma_transmission_normalized_then_scaled"].to_numpy(dtype=float)

    popt, pcov = curve_fit(
        attenuation_model,
        x,
        y,
        sigma=sigma,
        absolute_sigma=True,
        p0=[120.0],
        bounds=([1e-6], [np.inf]),
        maxfev=10000,
    )
    lambda_eff = float(popt[0])
    sigma_lambda = float(np.sqrt(pcov[0, 0])) if pcov.size else float("nan")
    y_fit = attenuation_model(x, lambda_eff)
    chi2, ndf, chi2_ndf = chi2_result(y, y_fit, sigma, npar=1)
    r2 = r_squared(y, y_fit)
    aic, bic = information_criteria(chi2, len(y), 1)

    return {
        "fit_name": "normalized_scaled_transmission",
        "model": "T(x) = exp(-x / lambda_eff)",
        "fit_sample": "Week 1 0-30 plates plus Week 2 40-60 plates; Week 2 zero-lead excluded",
        "x_unit": "mm",
        "lambda_eff_mm": lambda_eff,
        "sigma_lambda_eff_mm": sigma_lambda,
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "r_squared": r2,
        "aic": aic,
        "bic": bic,
    }


def fit_rate(fit_df: pd.DataFrame) -> dict[str, float | str]:
    data = fit_df.loc[fit_df["include_in_fit"]].copy()
    x = data["lead_thickness_mm"].to_numpy(dtype=float)
    y = data["r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)
    sigma = data["sigma_r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)

    popt, pcov = curve_fit(
        rate_model,
        x,
        y,
        sigma=sigma,
        absolute_sigma=True,
        p0=[float(y[0]), 120.0],
        bounds=([0.0, 1e-6], [np.inf, np.inf]),
        maxfev=10000,
    )
    r0, lambda_eff = [float(value) for value in popt]
    errors = np.sqrt(np.diag(pcov)) if pcov.size else [float("nan"), float("nan")]
    y_fit = rate_model(x, r0, lambda_eff)
    chi2, ndf, chi2_ndf = chi2_result(y, y_fit, sigma, npar=2)
    r2 = r_squared(y, y_fit)
    aic, bic = information_criteria(chi2, len(y), 2)

    return {
        "fit_name": "normalized_scaled_rate",
        "model": "R(x) = R0 * exp(-x / lambda_eff)",
        "fit_sample": "Week 1 0-30 plates plus Week 2 40-60 plates; Week 2 zero-lead excluded",
        "x_unit": "mm",
        "rate_unit": "counts/hour",
        "r0_counts_per_hour": r0,
        "sigma_r0_counts_per_hour": float(errors[0]),
        "lambda_eff_mm": lambda_eff,
        "sigma_lambda_eff_mm": float(errors[1]),
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "r_squared": r2,
        "aic": aic,
        "bic": bic,
    }


def fit_offset_transmission(fit_df: pd.DataFrame) -> dict[str, float | str]:
    data = fit_df.loc[fit_df["include_in_fit"]].copy()
    x = data["lead_thickness_mm"].to_numpy(dtype=float)
    y = data["transmission_normalized_then_scaled"].to_numpy(dtype=float)
    sigma = data["sigma_transmission_normalized_then_scaled"].to_numpy(dtype=float)

    offset0 = float(np.min(y) * 0.95)
    amp0 = float(max(y[0] - offset0, 1e-3))
    upper_offset = float(np.min(y) * 0.999)
    popt, pcov = curve_fit(
        offset_exp_model,
        x,
        y,
        sigma=sigma,
        absolute_sigma=True,
        p0=[offset0, amp0, 40.0],
        bounds=([0.0, 0.0, 1e-6], [upper_offset, np.inf, np.inf]),
        maxfev=50000,
    )
    offset, amplitude, lambda_eff = [float(value) for value in popt]
    errors = np.sqrt(np.diag(pcov)) if pcov.size else [float("nan")] * 3
    y_fit = offset_exp_model(x, offset, amplitude, lambda_eff)
    chi2, ndf, chi2_ndf = chi2_result(y, y_fit, sigma, npar=3)
    r2 = r_squared(y, y_fit)
    aic, bic = information_criteria(chi2, len(y), 3)

    return {
        "fit_name": "normalized_scaled_transmission_offset_exp",
        "model": "T(x) = T_inf + A * exp(-x / lambda_eff)",
        "fit_sample": "Week 1 0-30 plates plus Week 2 40-60 plates; Week 2 zero-lead excluded",
        "x_unit": "mm",
        "offset": offset,
        "sigma_offset": float(errors[0]),
        "amplitude": amplitude,
        "sigma_amplitude": float(errors[1]),
        "lambda_eff_mm": lambda_eff,
        "sigma_lambda_eff_mm": float(errors[2]),
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "r_squared": r2,
        "aic": aic,
        "bic": bic,
    }


def fit_offset_rate(fit_df: pd.DataFrame) -> dict[str, float | str]:
    data = fit_df.loc[fit_df["include_in_fit"]].copy()
    x = data["lead_thickness_mm"].to_numpy(dtype=float)
    y = data["r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)
    sigma = data["sigma_r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)

    offset0 = float(np.min(y) * 0.95)
    amp0 = float(max(y[0] - offset0, 1.0))
    upper_offset = float(np.min(y) * 0.999)
    popt, pcov = curve_fit(
        offset_exp_model,
        x,
        y,
        sigma=sigma,
        absolute_sigma=True,
        p0=[offset0, amp0, 40.0],
        bounds=([0.0, 0.0, 1e-6], [upper_offset, np.inf, np.inf]),
        maxfev=50000,
    )
    offset, amplitude, lambda_eff = [float(value) for value in popt]
    errors = np.sqrt(np.diag(pcov)) if pcov.size else [float("nan")] * 3
    y_fit = offset_exp_model(x, offset, amplitude, lambda_eff)
    chi2, ndf, chi2_ndf = chi2_result(y, y_fit, sigma, npar=3)
    r2 = r_squared(y, y_fit)
    aic, bic = information_criteria(chi2, len(y), 3)

    return {
        "fit_name": "normalized_scaled_rate_offset_exp",
        "model": "R(x) = R_inf + A * exp(-x / lambda_eff)",
        "fit_sample": "Week 1 0-30 plates plus Week 2 40-60 plates; Week 2 zero-lead excluded",
        "x_unit": "mm",
        "rate_unit": "counts/hour",
        "offset": offset,
        "sigma_offset": float(errors[0]),
        "amplitude": amplitude,
        "sigma_amplitude": float(errors[1]),
        "lambda_eff_mm": lambda_eff,
        "sigma_lambda_eff_mm": float(errors[2]),
        "chi2": chi2,
        "ndf": ndf,
        "chi2_ndf": chi2_ndf,
        "r_squared": r2,
        "aic": aic,
        "bic": bic,
    }


def plot_transmission_fit(
    fit_df: pd.DataFrame, result: dict[str, float | str], out_dir: Path
) -> None:
    used = fit_df.loc[fit_df["include_in_fit"]]
    excluded = fit_df.loc[~fit_df["include_in_fit"]]
    x = used["lead_thickness_mm"].to_numpy(dtype=float)
    y = used["transmission_normalized_then_scaled"].to_numpy(dtype=float)
    sigma = used["sigma_transmission_normalized_then_scaled"].to_numpy(dtype=float)
    lambda_eff = float(result["lambda_eff_mm"])

    x_grid = np.linspace(0, max(x) * 1.05, 300)
    y_grid = attenuation_model(x_grid, lambda_eff)
    y_fit = attenuation_model(x, lambda_eff)
    smooth_x, smooth_y = smooth_xy(x, y)
    r2 = float(result["r_squared"])

    fig, (ax, ax_res) = plt.subplots(
        2,
        1,
        figsize=(7, 6),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    ax.errorbar(x, y, yerr=sigma, marker="o", linestyle="none", capsize=4, label="Fit data")
    if not excluded.empty:
        ax.scatter(
            excluded["lead_thickness_mm"],
            excluded["transmission_normalized_then_scaled"],
            marker="x",
            color="tab:gray",
            label="Excluded Week 2 zero lead",
        )
    ax.plot(
        smooth_x,
        smooth_y,
        "--",
        color="tab:orange",
        linewidth=1.6,
        label="Smooth data guide",
    )
    ax.plot(x_grid, y_grid, "-", label=f"Fit lambda={lambda_eff:.2f} mm")
    add_fit_text(
        ax,
        [
            f"R^2 = {r2:.3f}",
            f"chi2/ndf = {float(result['chi2_ndf']):.3f}",
        ],
    )
    ax.set_ylabel("Transmission")
    ax.set_title("Normalized-then-scaled transmission fit")
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax_res.axhline(0, color="black", linewidth=1)
    ax_res.errorbar(x, y - y_fit, yerr=sigma, marker="o", linestyle="none", capsize=4)
    ax_res.set_xlabel("Lead thickness (mm)")
    ax_res.set_ylabel("Residual")
    ax_res.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "normalized_scaled_transmission_fit.png", dpi=200)
    plt.close(fig)


def plot_rate_fit(fit_df: pd.DataFrame, result: dict[str, float | str], out_dir: Path) -> None:
    used = fit_df.loc[fit_df["include_in_fit"]]
    excluded = fit_df.loc[~fit_df["include_in_fit"]]
    x = used["lead_thickness_mm"].to_numpy(dtype=float)
    y = used["r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)
    sigma = used["sigma_r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)
    r0 = float(result["r0_counts_per_hour"])
    lambda_eff = float(result["lambda_eff_mm"])

    x_grid = np.linspace(0, max(x) * 1.05, 300)
    y_grid = rate_model(x_grid, r0, lambda_eff)
    y_fit = rate_model(x, r0, lambda_eff)
    smooth_x, smooth_y = smooth_xy(x, y)
    r2 = float(result["r_squared"])

    fig, (ax, ax_res) = plt.subplots(
        2,
        1,
        figsize=(7, 6),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    ax.errorbar(x, y, yerr=sigma, marker="o", linestyle="none", capsize=4, label="Fit data")
    if not excluded.empty:
        ax.scatter(
            excluded["lead_thickness_mm"],
            excluded["r_coin_up_normalized_then_scaled"],
            marker="x",
            color="tab:gray",
            label="Excluded Week 2 zero lead",
        )
    ax.plot(
        smooth_x,
        smooth_y,
        "--",
        color="tab:orange",
        linewidth=1.6,
        label="Smooth data guide",
    )
    ax.plot(x_grid, y_grid, "-", label=f"Fit R0={r0:.1f}/h, lambda={lambda_eff:.2f} mm")
    add_fit_text(
        ax,
        [
            f"R^2 = {r2:.3f}",
            f"chi2/ndf = {float(result['chi2_ndf']):.3f}",
        ],
    )
    ax.set_ylabel("Rate (counts/hour)")
    ax.set_title("Normalized-then-scaled rate fit")
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax_res.axhline(0, color="black", linewidth=1)
    ax_res.errorbar(x, y - y_fit, yerr=sigma, marker="o", linestyle="none", capsize=4)
    ax_res.set_xlabel("Lead thickness (mm)")
    ax_res.set_ylabel("Residual")
    ax_res.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "normalized_scaled_rate_fit.png", dpi=200)
    plt.close(fig)


def plot_log_fit_views(
    fit_df: pd.DataFrame,
    transmission_result: dict[str, float | str],
    rate_result: dict[str, float | str],
    out_dir: Path,
) -> None:
    used = fit_df.loc[fit_df["include_in_fit"]].copy()
    excluded = fit_df.loc[~fit_df["include_in_fit"]].copy()
    x = used["lead_thickness_mm"].to_numpy(dtype=float)
    x_grid = np.linspace(0, max(x) * 1.05, 300)

    t = used["transmission_normalized_then_scaled"].to_numpy(dtype=float)
    sigma_t = used["sigma_transmission_normalized_then_scaled"].to_numpy(dtype=float)
    sigma_log_t = sigma_t / t
    lambda_t = float(transmission_result["lambda_eff_mm"])
    log_t_fit = -x / lambda_t
    log_t_r2 = r_squared(np.log(t), log_t_fit)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(x, np.log(t), yerr=sigma_log_t, marker="o", linestyle="none", capsize=4, label="Fit data")
    if not excluded.empty:
        ax.scatter(
            excluded["lead_thickness_mm"],
            np.log(excluded["transmission_normalized_then_scaled"]),
            marker="x",
            color="tab:gray",
            label="Excluded Week 2 zero lead",
        )
    ax.plot(x_grid, -x_grid / lambda_t, "-", label=f"ln T = -x/{lambda_t:.2f}")
    add_fit_text(
        ax,
        [
            f"R^2(log) = {log_t_r2:.3f}",
            f"chi2/ndf = {float(transmission_result['chi2_ndf']):.3f}",
        ],
    )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("ln(Transmission)")
    ax.set_title("Log-linear view of normalized-then-scaled transmission")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "normalized_scaled_transmission_log_fit.png", dpi=200)
    plt.close(fig)

    r = used["r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)
    sigma_r = used["sigma_r_coin_up_normalized_then_scaled"].to_numpy(dtype=float)
    sigma_log_r = sigma_r / r
    r0 = float(rate_result["r0_counts_per_hour"])
    lambda_r = float(rate_result["lambda_eff_mm"])
    log_r_fit = np.log(r0) - x / lambda_r
    log_r_r2 = r_squared(np.log(r), log_r_fit)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(x, np.log(r), yerr=sigma_log_r, marker="o", linestyle="none", capsize=4, label="Fit data")
    if not excluded.empty:
        ax.scatter(
            excluded["lead_thickness_mm"],
            np.log(excluded["r_coin_up_normalized_then_scaled"]),
            marker="x",
            color="tab:gray",
            label="Excluded Week 2 zero lead",
        )
    ax.plot(x_grid, np.log(r0) - x_grid / lambda_r, "-", label=f"ln R = ln R0 - x/{lambda_r:.2f}")
    add_fit_text(
        ax,
        [
            f"R^2(log) = {log_r_r2:.3f}",
            f"chi2/ndf = {float(rate_result['chi2_ndf']):.3f}",
        ],
    )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel("ln(Rate)")
    ax.set_title("Log-linear view of normalized-then-scaled rate")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "normalized_scaled_rate_log_fit.png", dpi=200)
    plt.close(fig)


def plot_offset_exp_fit(
    fit_df: pd.DataFrame,
    result: dict[str, float | str],
    out_dir: Path,
    *,
    quantity: str,
) -> None:
    used = fit_df.loc[fit_df["include_in_fit"]]
    excluded = fit_df.loc[~fit_df["include_in_fit"]]
    x = used["lead_thickness_mm"].to_numpy(dtype=float)
    if quantity == "transmission":
        y_col = "transmission_normalized_then_scaled"
        sigma_col = "sigma_transmission_normalized_then_scaled"
        y_label = "Transmission"
        filename = "normalized_scaled_transmission_offset_exp_fit.png"
        title = "Transmission fit with constant offset"
    else:
        y_col = "r_coin_up_normalized_then_scaled"
        sigma_col = "sigma_r_coin_up_normalized_then_scaled"
        y_label = "Rate (counts/hour)"
        filename = "normalized_scaled_rate_offset_exp_fit.png"
        title = "Rate fit with constant offset"

    y = used[y_col].to_numpy(dtype=float)
    sigma = used[sigma_col].to_numpy(dtype=float)
    offset = float(result["offset"])
    amplitude = float(result["amplitude"])
    lambda_eff = float(result["lambda_eff_mm"])
    x_grid = np.linspace(0, max(x) * 1.05, 300)
    y_grid = offset_exp_model(x_grid, offset, amplitude, lambda_eff)
    y_fit = offset_exp_model(x, offset, amplitude, lambda_eff)
    smooth_x, smooth_y = smooth_xy(x, y)

    fig, (ax, ax_res) = plt.subplots(
        2,
        1,
        figsize=(7, 6),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    ax.errorbar(x, y, yerr=sigma, marker="o", linestyle="none", capsize=4, label="Fit data")
    if not excluded.empty:
        ax.scatter(
            excluded["lead_thickness_mm"],
            excluded[y_col],
            marker="x",
            color="tab:gray",
            label="Excluded Week 2 zero lead",
        )
    ax.plot(
        smooth_x,
        smooth_y,
        "--",
        color="tab:orange",
        linewidth=1.6,
        label="Smooth data guide",
    )
    ax.plot(
        x_grid,
        y_grid,
        "-",
        label=f"Fit C={offset:.3g}, lambda={lambda_eff:.2f} mm",
    )
    add_fit_text(
        ax,
        [
            f"R^2 = {float(result['r_squared']):.3f}",
            f"chi2/ndf = {float(result['chi2_ndf']):.3f}",
            f"AIC = {float(result['aic']):.2f}",
        ],
    )
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax_res.axhline(0, color="black", linewidth=1)
    ax_res.errorbar(x, y - y_fit, yerr=sigma, marker="o", linestyle="none", capsize=4)
    ax_res.set_xlabel("Lead thickness (mm)")
    ax_res.set_ylabel("Residual")
    ax_res.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / filename, dpi=200)
    plt.close(fig)


def plot_offset_exp_log_view(
    fit_df: pd.DataFrame,
    result: dict[str, float | str],
    out_dir: Path,
    *,
    quantity: str,
) -> None:
    used = fit_df.loc[fit_df["include_in_fit"]]
    excluded = fit_df.loc[~fit_df["include_in_fit"]]
    x = used["lead_thickness_mm"].to_numpy(dtype=float)
    if quantity == "transmission":
        y_col = "transmission_normalized_then_scaled"
        sigma_col = "sigma_transmission_normalized_then_scaled"
        y_label = "ln(Transmission - T_inf)"
        filename = "normalized_scaled_transmission_offset_exp_log_fit.png"
        title = "Log-linear view after subtracting transmission offset"
    else:
        y_col = "r_coin_up_normalized_then_scaled"
        sigma_col = "sigma_r_coin_up_normalized_then_scaled"
        y_label = "ln(Rate - R_inf)"
        filename = "normalized_scaled_rate_offset_exp_log_fit.png"
        title = "Log-linear view after subtracting rate offset"

    y = used[y_col].to_numpy(dtype=float)
    sigma = used[sigma_col].to_numpy(dtype=float)
    offset = float(result["offset"])
    amplitude = float(result["amplitude"])
    lambda_eff = float(result["lambda_eff_mm"])
    y_minus_offset = y - offset
    valid = y_minus_offset > 0
    x_valid = x[valid]
    log_y = np.log(y_minus_offset[valid])
    sigma_log_y = sigma[valid] / y_minus_offset[valid]
    log_y_fit = np.log(amplitude) - x_valid / lambda_eff
    log_r2 = r_squared(log_y, log_y_fit)

    x_grid = np.linspace(0, max(x) * 1.05, 300)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(
        x_valid,
        log_y,
        yerr=sigma_log_y,
        marker="o",
        linestyle="none",
        capsize=4,
        label="Fit data",
    )
    if not excluded.empty:
        excluded_y = excluded[y_col].to_numpy(dtype=float) - offset
        valid_excluded = excluded_y > 0
        if np.any(valid_excluded):
            ax.scatter(
                excluded["lead_thickness_mm"].to_numpy(dtype=float)[valid_excluded],
                np.log(excluded_y[valid_excluded]),
                marker="x",
                color="tab:gray",
                label="Excluded Week 2 zero lead",
            )
    ax.plot(
        x_grid,
        np.log(amplitude) - x_grid / lambda_eff,
        "-",
        label=f"ln(y-C) = ln A - x/{lambda_eff:.2f}",
    )
    add_fit_text(
        ax,
        [
            f"R^2(log) = {log_r2:.3f}",
            f"chi2/ndf = {float(result['chi2_ndf']):.3f}",
        ],
    )
    ax.set_xlabel("Lead thickness (mm)")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / filename, dpi=200)
    plt.close(fig)


def write_outputs(
    fit_df: pd.DataFrame,
    fit_results: list[dict[str, float | str]],
    paths: dict[str, Path],
) -> None:
    fit_df.to_csv(paths["fit"] / "normalized_scaled_fit_input.csv", index=False)
    fit_table = pd.DataFrame(fit_results)
    fit_table.to_csv(paths["fit"] / "normalized_scaled_exponential_fits.csv", index=False)
    with (paths["fit"] / "normalized_scaled_exponential_fits.json").open("w", encoding="utf-8") as f:
        json.dump(fit_results, f, indent=2, ensure_ascii=False)


def main() -> None:
    args = parse_args()
    paths = ensure_output_dirs(args.results_dir)
    summary = pd.read_csv(args.input_table, dtype={"run": str})
    fit_df = prepare_fit_data(summary)
    transmission_result = fit_transmission(fit_df)
    rate_result = fit_rate(fit_df)
    offset_transmission_result = fit_offset_transmission(fit_df)
    offset_rate_result = fit_offset_rate(fit_df)
    fit_results = [
        transmission_result,
        rate_result,
        offset_transmission_result,
        offset_rate_result,
    ]

    write_outputs(fit_df, fit_results, paths)
    plot_transmission_fit(fit_df, transmission_result, paths["fit"])
    plot_rate_fit(fit_df, rate_result, paths["fit"])
    plot_log_fit_views(fit_df, transmission_result, rate_result, paths["fit"])
    plot_offset_exp_fit(
        fit_df, offset_transmission_result, paths["fit"], quantity="transmission"
    )
    plot_offset_exp_fit(fit_df, offset_rate_result, paths["fit"], quantity="rate")
    plot_offset_exp_log_view(
        fit_df, offset_transmission_result, paths["fit"], quantity="transmission"
    )
    plot_offset_exp_log_view(
        fit_df, offset_rate_result, paths["fit"], quantity="rate"
    )

    print("normalized-then-scaled exponential fits completed")
    print(f"fit outputs: {paths['fit']}")
    for result in fit_results:
        print(
            f"{result['fit_name']}: lambda={float(result['lambda_eff_mm']):.3f} "
            f"+/- {float(result['sigma_lambda_eff_mm']):.3f} mm, "
            f"chi2/ndf={float(result['chi2_ndf']):.3f}"
        )


if __name__ == "__main__":
    main()
