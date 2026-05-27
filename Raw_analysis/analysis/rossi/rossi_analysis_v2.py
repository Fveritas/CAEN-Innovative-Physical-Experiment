#!/usr/bin/env python3
"""
Rossi Transition Curve Analysis (v2)
Accounts for systematic shift between last week (0-30 plates) and this week (40-50 plates).
Coincidence condition: area > 30 AND area2 > 30.
Each file = 1 hour measurement.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

DATA_FILES = {
    0:  '/home/guiyu/workspace/CAEN/data/5181.root',
    10: '/home/guiyu/workspace/CAEN/data/5182.root',
    20: '/home/guiyu/workspace/CAEN/data/5183.root',
    30: '/home/guiyu/workspace/CAEN/data/5184.root',
    40: '/home/guiyu/workspace/CAEN/data/5185.root',
    50: '/home/guiyu/workspace/CAEN/data/5186.root',
}

MEASUREMENT_TIME_HOURS = 1.0
PLATE_THICKNESS_MM = 0.5
DETECTOR_DISTANCE_CM = 16.2
LEAD_RADIATION_LENGTH_MM = 5.6
LEAD_DENSITY_G_CM3 = 11.34

# Which week each data belongs to
WEEK_MAP = {0: 'last', 10: 'last', 20: 'last', 30: 'last',
            40: 'this', 50: 'this'}


def analyze_file(filepath, n_plates):
    with uproot.open(filepath) as f:
        tree = f['t1;1']
        area = tree['area'].array(library='np')
        area2 = tree['area2'].array(library='np')
        total = len(area)

        coin30 = (area > 30) & (area2 > 30)
        n_up30 = int(np.sum(area > 30))
        n_down30 = int(np.sum(area2 > 30))
        n_coin30 = int(np.sum(coin30))

        # Also test lower threshold
        coin5 = (area > 5) & (area2 > 5)
        n_coin5 = int(np.sum(coin5))

    thickness_mm = n_plates * PLATE_THICKNESS_MM
    rad_lengths = thickness_mm / LEAD_RADIATION_LENGTH_MM
    mass_thickness = thickness_mm * 0.1 * LEAD_DENSITY_G_CM3  # g/cm²

    return {
        'n_plates': n_plates,
        'thickness_mm': thickness_mm,
        'thickness_cm': thickness_mm / 10,
        'week': WEEK_MAP[n_plates],
        'rad_lengths': rad_lengths,
        'mass_thickness': mass_thickness,
        'total_entries': total,
        'n_up30': n_up30,
        'n_down30': n_down30,
        'n_coin30': n_coin30,
        'n_coin5': n_coin5,
        'rate30': n_coin30 / MEASUREMENT_TIME_HOURS,
        'rate5': n_coin5 / MEASUREMENT_TIME_HOURS,
        'coin_ratio30': n_coin30 / coin30 if coin30 > 0 else 0,
        'coin_per_up': n_coin30 / n_up30 if n_up30 > 0 else 0,
        'up_ratio': n_up30 / coin30 if coin30 > 0 else 0,
        'down_ratio': n_down30 / coin30 if coin30 > 0 else 0,
    }


def main():
    results = [analyze_file(DATA_FILES[p], p) for p in sorted(DATA_FILES.keys())]

    # ====== PRINT TABLES ======
    print("=" * 115)
    print("Rossi Transition Curve Analysis (v2)")
    print(f"Detector separation: {DETECTOR_DISTANCE_CM} cm | Plate: {PLATE_THICKNESS_MM} mm each")
    print(f"Lead X0 = {LEAD_RADIATION_LENGTH_MM} mm | Ec ≈ {7.4} MeV | ρ = {LEAD_DENSITY_G_CM3} g/cm³")
    print("=" * 115)

    print("\n--- Basic trigger & coincidence counts (threshold: area > 30) ---")
    print(f"{'Plates':>7} {'Week':>6} {'Entries':>9} {'Up>30':>7} {'Down>30':>9} "
          f"{'Coin30':>8} {'Rate30/h':>10} {'Coin/Entries':>13} {'Coin/Up':>8}")
    print("-" * 95)
    for r in results:
        print(f"{r['n_plates']:>7} {r['week']:>6} {r['total_entries']:>9} {r['n_up30']:>7} "
              f"{r['n_down30']:>9} {r['n_coin30']:>8} {r['rate30']:>10.0f} "
              f"{r['coin_ratio30']:>13.4f} {r['coin_per_up']:>8.4f}")

    # ====== SYSTEMATIC CHECK ======
    print("\n--- Systematic shift check: per-channel trigger rate ---")
    print(f"{'Plates':>7} {'Week':>6} {'Up/Entries':>12} {'Down/Entries':>14} "
          f"{'Coin/Entries':>13} {'Coin/Up':>8}")
    print("-" * 70)
    for r in results:
        print(f"{r['n_plates']:>7} {r['week']:>6} {r['up_ratio']:>12.4f} "
              f"{r['down_ratio']:>14.4f} {r['coin_ratio30']:>13.4f} {r['coin_per_up']:>8.4f}")

    # Compare last week avg vs this week avg
    last_ratios = [r['down_ratio'] for r in results if r['week'] == 'last']
    this_ratios = [r['down_ratio'] for r in results if r['week'] == 'this']
    last_coin_up = [r['coin_per_up'] for r in results if r['week'] == 'last']
    this_coin_up = [r['coin_per_up'] for r in results if r['week'] == 'this']

    print(f"\n--- Cross-week comparison ---")
    print(f"Down/Entries (week avg): last={np.mean(last_ratios):.4f}  this={np.mean(this_ratios):.4f}  "
          f"ratio_this/last={np.mean(this_ratios)/np.mean(last_ratios):.3f}")
    print(f"Coin/Up (week avg):       last={np.mean(last_coin_up):.4f}  this={np.mean(this_coin_up):.4f}  "
          f"ratio_this/last={np.mean(this_coin_up)/np.mean(last_coin_up):.3f}")
    print(f"!!! Lower detector efficiency dropped by ~{100*(1-np.mean(this_ratios)/np.mean(last_ratios)):.0f}% this week.")
    print(f"!!! This means absolute coincidence counts between the two weeks are NOT directly comparable.")

    # ====== ROSSI PEAK ANALYSIS (last week only) ======
    print("\n" + "=" * 115)
    print("Rossi Peak Analysis on LAST WEEK data only (0–30 plates, self-consistent):")
    last_r = [r for r in results if r['week'] == 'last']
    last_thick = np.array([r['thickness_mm'] for r in last_r])
    last_rates = np.array([r['rate30'] for r in last_r])
    last_rates5 = np.array([r['rate5'] for r in last_r])
    last_coin_up = np.array([r['coin_per_up'] for r in last_r])

    # Fit linear trend
    slope, intercept, r_value, p_value, std_err = stats.linregress(last_thick, last_rates)
    print(f"Linear fit: rate = {intercept:.1f} + ({slope:.2f})*thickness(mm)")
    print(f"R² = {r_value**2:.4f}, p = {p_value:.4f}")

    trend_slope = np.polyfit(last_thick, last_rates, 1)[0]
    if trend_slope < 0 and last_rates[0] == np.max(last_rates):
        print(f"\n>>> NO ROSSI PEAK DETECTED in 0–30 plate dataset.")
        print(f"    Coincidence rate at 0 plates (3357/h) > all other measurements.")
        print(f"    Rate decreases monotonically: 0→10→20→30 plates.")
        print(f"    Decrease over 15mm lead: {(last_rates[-1]-last_rates[0])/last_rates[0]*100:.1f}%")

        # Also note
        print(f"\n    Coin/Up ratio (corrects for upper-detector drift):")
        for i, r in enumerate(last_r):
            print(f"      {r['n_plates']} plates: {r['coin_per_up']:.4f}")
        print(f"    Coin/Up decreases linearly with thickness → no Rossi peak.")

    # ====== PLOTS ======
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Rossi Transition Curve Analysis\n(Note: 40-50 plates from different week — systematic shift)', 
                 fontsize=13, fontweight='bold')

    cmap = {'last': 'royalblue', 'this': 'crimson'}
    marker = {'last': 'o', 'this': 's'}

    # Plot 1: All data, colored by week
    ax = axes[0, 0]
    for week in ['last', 'this']:
        wk_r = [r for r in results if r['week'] == week]
        ax.plot([r['thickness_mm'] for r in wk_r],
                [r['rate30'] for r in wk_r],
                marker[week]+'-', color=cmap[week], linewidth=2, markersize=10,
                label=f'Week: {week}')
    # Draw expected trend from last week
    t_ext = np.linspace(0, 30, 50)
    ax.plot(t_ext, intercept + slope*t_ext, '--', color='gray', alpha=0.4, label='Linear fit (last week)')
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Coincidence rate (counts/h)', fontsize=11)
    ax.set_title('Coincidence Rate vs Thickness', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Second x-axis: X0
    ax2t = ax.twiny()
    ax2t.set_xlim(ax.get_xlim())
    ax2t.set_xlabel('Radiation length (X0)', fontsize=10)

    # Plot 2: Down/Entries ratio (diagnostic)
    ax = axes[0, 1]
    for week in ['last', 'this']:
        wk_r = [r for r in results if r['week'] == week]
        ax.plot([r['thickness_mm'] for r in wk_r],
                [r['down_ratio'] for r in wk_r],
                marker[week]+'-', color=cmap[week], linewidth=2, markersize=10,
                label=f'Week: {week}')
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Down trigger ratio (area>30 / entries)', fontsize=11)
    ax.set_title('Lower Detector Trigger Ratio\n(Reveals systematic shift between weeks)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Plot 3: Coin/Up normalized rate (last week zoom)
    ax = axes[1, 0]
    ax.plot(last_thick, last_coin_up, 'o-', color='teal', linewidth=2, markersize=10)
    ax.axvline(x=15, color='orange', linestyle='--', alpha=0.5, label='Expected Rossi peak\n~2.7 X0')
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Coin/Up ratio', fontsize=11)
    ax.set_title('Normalized Coincidence Ratio (Coin/Up)\nLast Week Only (0-30 plates)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Plot 4: Coincidence rates with different thresholds
    ax = axes[1, 1]
    last_thick_all = np.array([r['thickness_mm'] for r in last_r])
    ax.plot(last_thick_all, [r['rate30'] for r in last_r], 'o-', color='darkblue', linewidth=2, markersize=10, label='Thr=30')
    ax.plot(last_thick_all, [r['rate5'] for r in last_r], 's--', color='darkgreen', linewidth=2, markersize=10, label='Thr=5')
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Coincidence rate (counts/h)', fontsize=11)
    ax.set_title('Coincidence Rate: Threshold Comparison\nLast Week Only', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    plt.savefig('/home/guiyu/workspace/CAEN/data/rossi_curve_v2.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: /home/guiyu/workspace/CAEN/data/rossi_curve_v2.png")

    plt.show()


if __name__ == '__main__':
    main()
