#!/usr/bin/env python3
"""
Rossi Transition Curve Analysis
Analyze coincidence rate vs lead plate thickness from ROOT data files.
Each file = 1 hour measurement.
Coincidence condition: area > 30 AND area2 > 30 (both upper and lower detectors).
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

# File mapping: number of lead plates → ROOT file
# Each plate = 0.5 mm thick
DATA_FILES = {
    0:  '/home/guiyu/workspace/CAEN/data/5181.root',
    10: '/home/guiyu/workspace/CAEN/data/5182.root',
    20: '/home/guiyu/workspace/CAEN/data/5183.root',
    30: '/home/guiyu/workspace/CAEN/data/5184.root',
    40: '/home/guiyu/workspace/CAEN/data/5185.root',
    50: '/home/guiyu/workspace/CAEN/data/5186.root',
}

MEASUREMENT_TIME_HOURS = 1.0  # each file = 1 hour
PLATE_THICKNESS_MM = 0.5     # mm per plate
DETECTOR_DISTANCE_CM = 16.2  # between upper and lower detectors

# Lead properties
LEAD_RADIATION_LENGTH_MM = 5.6  # X0 for lead ≈ 0.56 cm = 5.6 mm
LEAD_CRITICAL_ENERGY_MEV = 7.4  # Ec for lead

def analyze_file(filepath, n_plates):
    """Analyze a single ROOT file and return statistics."""
    with uproot.open(filepath) as f:
        tree = f['t1;1']
        area = tree['area'].array(library='np')
        area2 = tree['area2'].array(library='np')

        total_entries = len(area)

        # Coincidence: both area > 30
        coin_mask = (area > 30) & (area2 > 30)
        n_coincidence = int(np.sum(coin_mask))

        # Single-detector trigger counts
        n_up = int(np.sum(area > 30))
        n_down = int(np.sum(area2 > 30))

        # Statistics for area distributions
        coin_area = area[coin_mask]
        coin_area2 = area2[coin_mask]

    thickness_mm = n_plates * PLATE_THICKNESS_MM
    rad_lengths = thickness_mm / LEAD_RADIATION_LENGTH_MM

    return {
        'n_plates': n_plates,
        'thickness_mm': thickness_mm,
        'rad_lengths': rad_lengths,
        'total_entries': total_entries,
        'n_coincidence': n_coincidence,
        'n_up': n_up,
        'n_down': n_down,
        'coin_rate_per_hour': n_coincidence / MEASUREMENT_TIME_HOURS,
        'coin_ratio': n_coincidence / total_entries if total_entries > 0 else 0,
        'mean_coin_area': np.mean(coin_area) if len(coin_area) > 0 else 0,
        'mean_coin_area2': np.mean(coin_area2) if len(coin_area2) > 0 else 0,
    }


def main():
    results = []
    for n_plates in sorted(DATA_FILES.keys()):
        r = analyze_file(DATA_FILES[n_plates], n_plates)
        results.append(r)

    # Print results table
    print("=" * 100)
    print("Rossi Transition Curve Analysis")
    print(f"Coincidence condition: area(up) > 30 AND area(down) > 30")
    print(f"Detector distance: {DETECTOR_DISTANCE_CM} cm")
    print(f"Plate thickness: {PLATE_THICKNESS_MM} mm each")
    print(f"Lead radiation length X0: {LEAD_RADIATION_LENGTH_MM} mm")
    print(f"Measurement time: {MEASUREMENT_TIME_HOURS} hour per file")
    print("=" * 100)
    print(f"{'Plates':>8} {'Thick(mm)':>10} {'Thick(cm)':>10} {'RadLen(X0)':>10} "
          f"{'Entries':>10} {'Coin(up&down)':>14} {'CoinRate(/h)':>13} {'CoinRatio':>10} "
          f"{'Up(>30)':>10} {'Down(>30)':>10}")
    print("-" * 100)
    for r in results:
        print(f"{r['n_plates']:>8} {r['thickness_mm']:>10.1f} {r['thickness_mm']/10:>10.2f} "
              f"{r['rad_lengths']:>10.2f} "
              f"{r['total_entries']:>10} {r['n_coincidence']:>14} {r['coin_rate_per_hour']:>13.1f} "
              f"{r['coin_ratio']:>10.4f} "
              f"{r['n_up']:>10} {r['n_down']:>10}")

    print("=" * 100)

    # Detect Rossi peak
    thicknesses = np.array([r['thickness_mm'] for r in results])
    rates = np.array([r['coin_rate_per_hour'] for r in results])
    plates = np.array([r['n_plates'] for r in results])

    peak_idx = np.argmax(rates)
    print(f"\nPeak coincidence rate: {rates[peak_idx]:.1f} /hour")
    print(f"Peak at: {plates[peak_idx]} plates = {thicknesses[peak_idx]:.1f} mm = {thicknesses[peak_idx]/10:.2f} cm")
    print(f"  = {thicknesses[peak_idx]/LEAD_RADIATION_LENGTH_MM:.1f} radiation lengths (X0)")
    print(f"  Expected Rossi peak: ~1.5 cm ≈ 2.7 X0")

    has_peak = False
    if peak_idx > 0 and peak_idx < len(rates) - 1:
        if rates[peak_idx-1] < rates[peak_idx] > rates[peak_idx+1]:
            has_peak = True
            print(f"\n>>> Rossi peak DETECTED: rate rises then falls through the peak region. <<<")

    if not has_peak:
        # Check overall trend: rate declines with thickness
        trend_slope = np.polyfit(range(len(rates)), rates, 1)[0]
        if trend_slope < 0 and rates[0] == np.max(rates):
            print(f"\n>>> NOT DETECTED: Coincidence rate is highest at 0 plates and")
            print(f"    decreases with additional lead. No Rossi peak observed.")
            print(f"    The lead acts primarily as an absorber between the two detectors")
            print(f"    in this vertical coincidence geometry (16.2 cm separation).")

    # Alternative: check if any thickness between 0 and max shows significant increase
    peak_over_base = rates[peak_idx] / rates[0] if rates[0] > 0 else float('inf')
    min_rate = np.min(rates)
    max_rate = np.max(rates)
    print(f"\nRate range: {min_rate:.1f} – {max_rate:.1f} /hour")
    print(f"Max/Min ratio: {max_rate/min_rate:.2f}" if min_rate > 0 else "")

    # ====== Plots ======
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Rossi Transition Curve Analysis', fontsize=14, fontweight='bold')
    fig.tight_layout(pad=4.0)

    # Plot 1: Coincidence rate vs thickness (Rossi curve)
    ax = axes[0, 0]
    ax.plot(thicknesses, rates, 'o-', color='darkblue', linewidth=2, markersize=10, label='Coincidence rate')
    ax.axvline(x=thicknesses[peak_idx], color='red', linestyle='--', alpha=0.5,
               label=f'Peak at {thicknesses[peak_idx]:.1f} mm')
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Coincidence rate (counts / hour)', fontsize=11)
    ax.set_title('Coincidence Rate vs Lead Thickness\n(Rossi Transition Curve)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Add second x-axis: radiation lengths
    ax2_t = ax.twiny()
    ax2_t.set_xlim(ax.get_xlim())
    x0_ticks = np.arange(0, 30, 5)
    ax2_t.set_xticks(x0_ticks)
    ax2_t.set_xticklabels([f'{x/LEAD_RADIATION_LENGTH_MM:.1f} X0' for x in x0_ticks])
    ax2_t.set_xlabel('Radiation length (X0)', fontsize=10)

    # Plot 2: Coincidence rate vs radiation length with theoretical annotation
    ax = axes[0, 1]
    rad_lengths = np.array([r['rad_lengths'] for r in results])
    ax.plot(rad_lengths, rates, 's-', color='darkgreen', linewidth=2, markersize=10)
    ax.set_xlabel('Radiation length (X0)', fontsize=11)
    ax.set_ylabel('Coincidence rate (counts / hour)', fontsize=11)
    ax.set_title('Coincidence Rate vs Radiation Length', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Mark expected Rossi peak region (2-3 X0)
    ax.axvspan(2, 3, alpha=0.15, color='orange', label='Expected Rossi peak\n(~2-3 X0)')
    ax.legend()

    # Plot 3: Total triggers and coincidences vs thickness
    ax = axes[1, 0]
    n_coin = np.array([r['n_coincidence'] for r in results])
    n_up = np.array([r['n_up'] for r in results])
    n_down = np.array([r['n_down'] for r in results])
    n_total = np.array([r['total_entries'] for r in results])

    ax.plot(thicknesses, n_up, 's--', color='blue', alpha=0.7, label='Upper detector (area>30)')
    ax.plot(thicknesses, n_down, '^--', color='green', alpha=0.7, label='Lower detector (area>30)')
    ax.plot(thicknesses, n_coin, 'o-', color='red', linewidth=2, markersize=8, label='Coincidences')
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Event count', fontsize=11)
    ax.set_title('Trigger and Coincidence Counts', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Plot 4: Coincidence ratio (coin/entries) vs thickness
    ax = axes[1, 1]
    ratios = np.array([r['coin_ratio'] for r in results])
    ax.plot(thicknesses, ratios, 'o-', color='purple', linewidth=2, markersize=10)
    ax.set_xlabel('Lead thickness (mm)', fontsize=11)
    ax.set_ylabel('Coincidence ratio (coin / total entries)', fontsize=11)
    ax.set_title('Coincidence Ratio vs Thickness', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.savefig('/home/guiyu/workspace/CAEN/data/rossi_curve.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved to: /home/guiyu/workspace/CAEN/data/rossi_curve.png")
    plt.show()


if __name__ == '__main__':
    main()
