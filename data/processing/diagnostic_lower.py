#!/usr/bin/env python3
"""
Diagnostic: compare last week vs this week lower detector area spectra
to determine root cause of ~54% efficiency drop.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

FILES = {
    (0, 'last'):  '/home/guiyu/workspace/CAEN/data/5181.root',
    (10, 'last'): '/home/guiyu/workspace/CAEN/data/5182.root',
    (20, 'last'): '/home/guiyu/workspace/CAEN/data/5183.root',
    (30, 'last'): '/home/guiyu/workspace/CAEN/data/5184.root',
    (40, 'this'): '/home/guiyu/workspace/CAEN/data/5185.root',
    (50, 'this'): '/home/guiyu/workspace/CAEN/data/5186.root',
}


def load_areas(filepath):
    with uproot.open(filepath) as f:
        t = f['t1;1']
        return t['area'].array(library='np'), t['area2'].array(library='np')


def main():
    # Load all data
    data = {}
    for (n, wk), fp in FILES.items():
        a1, a2 = load_areas(fp)
        data[(n, wk)] = (a1, a2)

    # Separate by week (aggregate area distributions)
    last_up = np.concatenate([data[(n, 'last')][0] for n in [0, 10, 20, 30]])
    last_down = np.concatenate([data[(n, 'last')][1] for n in [0, 10, 20, 30]])
    this_up = np.concatenate([data[(n, 'this')][0] for n in [40, 50]])
    this_down = np.concatenate([data[(n, 'this')][1] for n in [40, 50]])

    # Remove extreme outliers for cleaner histograms
    def clip_areas(arr, low=-50, high=400):
        return arr[(arr > low) & (arr < high)]

    lu = clip_areas(last_up)
    ld = clip_areas(last_down)
    tu = clip_areas(this_up)
    td = clip_areas(this_down)

    # ====== PRINT DIAGNOSTICS ======
    print("=" * 80)
    print("Diagnostic: Area Spectrum Comparison (Last Week vs This Week)")
    print("=" * 80)

    print(f"\nSample sizes (clipped to [-50, 400]):")
    print(f"  Upper detector: last={len(lu)}, this={len(tu)}")
    print(f"  Lower detector: last={len(ld)}, this={len(td)}")

    # Key statistics
    for label, arr in [("Upper last", lu), ("Upper this", tu),
                       ("Lower last", ld), ("Lower this", td)]:
        print(f"  {label:15s}: median={np.median(arr):.2f}, mean={np.mean(arr):.2f}, "
              f"std={np.std(arr):.2f}, >30={np.sum(arr>30)/len(arr)*100:.1f}%")

    # Fraction surviving threshold
    thresholds = [5, 10, 15, 20, 25, 30, 40, 50, 80, 100]
    print(f"\n{'Thr':>5}  {'Last-Up%':>10} {'This-Up%':>10} {'Last-Down%':>10} {'This-Down%':>10} {'Down-ratio':>10}")
    print("-" * 58)
    for thr in thresholds:
        lp_u = np.sum(lu > thr) / len(lu) * 100
        tp_u = np.sum(tu > thr) / len(tu) * 100
        lp_d = np.sum(ld > thr) / len(ld) * 100
        tp_d = np.sum(td > thr) / len(td) * 100
        print(f"{thr:>5}  {lp_u:>10.2f} {tp_u:>10.2f} {lp_d:>10.2f} {tp_d:>10.2f} {tp_d/lp_d:>10.3f}")

    # ====== FINDINGS ======
    # Ratio of this/last for different thresholds
    print("\n--- Diagnosis ---")
    last_gt30 = np.sum(ld > 30) / len(ld)
    this_gt30 = np.sum(td > 30) / len(td)
    ratio30 = this_gt30 / last_gt30

    # If gain shifted left, median of this week should be lower
    median_shift = np.median(td) - np.median(ld)
    print(f"Lower detector median shift: {median_shift:+.2f} (this - last)")
    print(f"Lower detector mean shift:   {np.mean(td) - np.mean(ld):+.2f}")

    if median_shift < -2:
        print(f"\n>>> CONCLUSION: Gain/HV drift detected!")
        print(f"    Lower detector area spectrum shifted LEFT by {median_shift:.1f} units.")
        print(f"    This causes signals to fall below the >30 threshold.")
        print(f"    Root cause: PMT/SiPM HV drift or gain change on lower channel.")
        print(f"    Fix: increase lower detector HV, or lower software threshold.")
    elif abs(median_shift) < 2:
        print(f"\n>>> CONCLUSION: No significant gain shift detected.")
        print(f"    Median area unchanged ({median_shift:.1f}), but >30 survival rate dropped.")
        print(f"    Root cause more likely: geometry misalignment or dead-time/noise.")
    else:
        print(f"\n>>> Gain shift: median moved RIGHT by {median_shift:.1f} units. Unexpected.")

    # ====== PLOTS ======
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Diagnostic: Lower Detector Area Spectrum — Last Week vs This Week',
                 fontsize=14, fontweight='bold')

    bins = np.linspace(-50, 400, 181)

    # Row 1: Upper detector (control group)
    ax = axes[0, 0]
    ax.hist(lu, bins=bins, alpha=0.6, color='royalblue', label=f'Last week (n={len(lu)})', density=True)
    ax.hist(tu, bins=bins, alpha=0.6, color='crimson', label=f'This week (n={len(tu)})', density=True)
    ax.axvline(30, color='black', linestyle='--', alpha=0.5, linewidth=1, label='threshold=30')
    ax.set_title('Upper Detector Area Spectrum\n(should be identical — control)', fontsize=11)
    ax.set_xlabel('Area')
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    # Overlay: zoom on upper detector
    for arr, color, label in [(lu, 'royalblue', 'Last week'), (tu, 'crimson', 'This week')]:
        h, edges = np.histogram(arr[(arr > 0) & (arr < 200)], bins=bins[bins <= 200])
        ax.stairs(h / max(h), edges, fill=False, color=color, linewidth=1.5, label=label)
    ax.axvline(30, color='black', linestyle='--', alpha=0.5)
    ax.set_title('Upper Detector (0-200 zoom, normalized)', fontsize=11)
    ax.set_xlabel('Area')
    ax.legend(fontsize=8)

    ax = axes[0, 2]
    # Upper detector CDF
    for arr, color, label in [(lu, 'royalblue', 'Last week'), (tu, 'crimson', 'This week')]:
        sorted_arr = np.sort(arr[arr > -200])
        cdf = np.arange(1, len(sorted_arr) + 1) / len(sorted_arr)
        ax.plot(sorted_arr, cdf, color=color, linewidth=2, label=label)
    ax.axvline(30, color='black', linestyle='--', alpha=0.5)
    ax.set_title('Upper Detector CDF', fontsize=11)
    ax.set_xlabel('Area')
    ax.set_ylabel('Cumulative probability')
    ax.set_xlim(-10, 200)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Row 2: Lower detector (problem channel)
    ax = axes[1, 0]
    ax.hist(ld, bins=bins, alpha=0.6, color='royalblue', label=f'Last week (n={len(ld)})', density=True)
    ax.hist(td, bins=bins, alpha=0.6, color='crimson', label=f'This week (n={len(td)})', density=True)
    ax.axvline(30, color='black', linestyle='--', alpha=0.5, linewidth=1)
    ax.set_title('Lower Detector Area Spectrum\n(efficiency dropped 54%)', fontsize=11)
    ax.set_xlabel('Area')
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    # Zoom on lower detector
    for arr, color, label in [(ld, 'royalblue', 'Last week'), (td, 'crimson', 'This week')]:
        h, edges = np.histogram(arr[(arr > 0) & (arr < 200)], bins=bins[bins <= 200])
        ax.stairs(h / max(h), edges, fill=False, color=color, linewidth=1.5, label=label)
    ax.axvline(30, color='black', linestyle='--', alpha=0.5)
    ax.set_title('Lower Detector (0-200 zoom, normalized)', fontsize=11)
    ax.set_xlabel('Area')
    ax.legend(fontsize=8)

    ax = axes[1, 2]
    # Lower detector CDF
    for arr, color, label in [(ld, 'royalblue', 'Last week'), (td, 'crimson', 'This week')]:
        sorted_arr = np.sort(arr[arr > -200])
        cdf = np.arange(1, len(sorted_arr) + 1) / len(sorted_arr)
        ax.plot(sorted_arr, cdf, color=color, linewidth=2, label=label)
    ax.axvline(30, color='black', linestyle='--', alpha=0.5)
    ax.set_title('Lower Detector CDF', fontsize=11)
    ax.set_xlabel('Area')
    ax.set_ylabel('Cumulative probability')
    ax.set_xlim(-10, 200)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    plt.savefig('/home/guiyu/workspace/CAEN/data/diagnostic_lower_detector.png', dpi=150, bbox_inches='tight')
    print(f"\nDiagnostic plot saved: /home/guiyu/workspace/CAEN/data/diagnostic_lower_detector.png")
    plt.show()


if __name__ == '__main__':
    main()
