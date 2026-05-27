#!/usr/bin/env python3
"""
Diagnostic v2: Focus on pulse population (>10), not noise-dominated median.
Analyze per-file to check if area spectrum shape shifts or scales.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

FILES_LAST = {
    0:  '/home/guiyu/workspace/CAEN/data/5181.root',
    10: '/home/guiyu/workspace/CAEN/data/5182.root',
    20: '/home/guiyu/workspace/CAEN/data/5183.root',
    30: '/home/guiyu/workspace/CAEN/data/5184.root',
}
FILES_THIS = {
    40: '/home/guiyu/workspace/CAEN/data/5185.root',
    50: '/home/guiyu/workspace/CAEN/data/5186.root',
}


def load_areas(fp):
    with uproot.open(fp) as f:
        t = f['t1;1']
        return t['area'].array(library='np'), t['area2'].array(library='np')


def main():
    # ===== Per-file pulse statistics (area > 10) =====
    print("=" * 100)
    print("Pulse population analysis (area > 10 only):")
    print(f"{'Plates':>7} {'Week':>6} {'Up>10':>8} {'Up_med':>8} {'Up_mean':>8} "
          f"{'Down>10':>10} {'Down_med':>10} {'Down_mean':>10}")
    print("-" * 85)

    all_last_up_pulses = []
    all_this_up_pulses = []
    all_last_down_pulses = []
    all_this_down_pulses = []

    for n, fp in {**FILES_LAST, **FILES_THIS}.items():
        a1, a2 = load_areas(fp)
        wk = 'last' if n <= 30 else 'this'

        up_pulse = a1[a1 > 10]
        down_pulse = a2[a2 > 10]

        print(f"{n:>7} {wk:>6} {len(up_pulse):>8} {np.median(up_pulse):>8.1f} "
              f"{np.mean(up_pulse):>8.1f} {len(down_pulse):>10} "
              f"{np.median(down_pulse):>10.1f} {np.mean(down_pulse):>10.1f}")

        if wk == 'last':
            all_last_up_pulses.append(up_pulse)
            all_last_down_pulses.append(down_pulse)
        else:
            all_this_up_pulses.append(up_pulse)
            all_this_down_pulses.append(down_pulse)

    up_last = np.concatenate(all_last_up_pulses)
    up_this = np.concatenate(all_this_up_pulses)
    down_last = np.concatenate(all_last_down_pulses)
    down_this = np.concatenate(all_this_down_pulses)

    print(f"\n--- Aggregated pulse population ---")
    print(f"Upper last: n={len(up_last)}, median={np.median(up_last):.1f}, mean={np.mean(up_last):.1f}, std={np.std(up_last):.1f}")
    print(f"Upper this: n={len(up_this)}, median={np.median(up_this):.1f}, mean={np.mean(up_this):.1f}, std={np.std(up_this):.1f}")
    print(f"Upper median shift: {np.median(up_this) - np.median(up_last):+.1f}")
    print(f"Upper pulse count ratio this/last (per h): {(len(up_this)/2)/(len(up_last)/4):.3f}")
    print()
    print(f"Lower last: n={len(down_last)}, median={np.median(down_last):.1f}, mean={np.mean(down_last):.1f}, std={np.std(down_last):.1f}")
    print(f"Lower this: n={len(down_this)}, median={np.median(down_this):.1f}, mean={np.mean(down_this):.1f}, std={np.std(down_this):.1f}")
    print(f"Lower median shift: {np.median(down_this) - np.median(down_last):+.1f}")
    print(f"Lower pulse count ratio this/last (per h): {(len(down_this)/2)/(len(down_last)/4):.3f}")

    # ===== QUANTILE COMPARISON =====
    print(f"\n--- Quantile comparison for pulse population ---")
    qs = [0.1, 0.25, 0.5, 0.75, 0.9]
    print(f"{'Quantile':>10} {'Up_last':>10} {'Up_this':>10} {'ratio':>8} {'Down_last':>10} {'Down_this':>10} {'ratio':>8}")
    for q in qs:
        ul = np.quantile(down_last, q)
        ut = np.quantile(down_this, q)
        print(f"{q:>10.2f} {np.quantile(up_last, q):>10.1f} {np.quantile(up_this, q):>10.1f} "
              f"{np.quantile(up_this, q)/np.quantile(up_last, q):>8.3f} "
              f"{ul:>10.1f} {ut:>10.1f} "
              f"{ut/ul if ul > 0 else 0:>8.3f}")

    # ===== THRESHOLD RATIO (absolute counts, per hour normalized) =====
    print(f"\n--- Absolute pulse counts (per hour) vs threshold ---")
    print(f"{'Thr':>5} {'Up_last/h':>10} {'Up_this/h':>10} {'U_ratio':>8} "
          f"{'Down_last/h':>12} {'Down_this/h':>12} {'D_ratio':>8}")
    for thr in [5, 10, 15, 20, 25, 30, 40, 50, 80, 100]:
        ul_h = np.sum(up_last > thr) / 4   # 4 hours last week
        ut_h = np.sum(up_this > thr) / 2   # 2 hours this week
        dl_h = np.sum(down_last > thr) / 4
        dt_h = np.sum(down_this > thr) / 2
        ur = ut_h / ul_h if ul_h > 0 else 0
        dr = dt_h / dl_h if dl_h > 0 else 0
        print(f"{thr:>5} {ul_h:>10.0f} {ut_h:>10.0f} {ur:>8.3f} "
              f"{dl_h:>12.0f} {dt_h:>12.0f} {dr:>8.3f}")

    # ====== DIAGNOSIS ======
    print(f"\n{'='*60}")
    print("DIAGNOSIS")

    # Upper detector
    up_median_ratio = np.median(up_this) / np.median(up_last)
    down_median_ratio = np.median(down_this) / np.median(down_last)
    
    # Check if lower pulse median shifted
    down_med_shift = np.median(down_this) - np.median(down_last)
    down_med_ratio = np.median(down_this) / np.median(down_last)
    
    print(f"Upper: median ratio this/last = {up_median_ratio:.3f} — {'GAIN UP' if up_median_ratio > 1.05 else 'stable' if up_median_ratio > 0.95 else 'GAIN DOWN'}")
    print(f"Lower: median ratio this/last = {down_median_ratio:.3f} — {'GAIN UP' if down_median_ratio > 1.05 else 'stable' if down_median_ratio > 0.95 else 'GAIN DOWN'}")
    print(f"Lower median shift: {down_med_shift:+.1f}")

    # Check ratio constancy
    ratios = []
    for thr in [5, 10, 15, 20, 25, 30, 40, 50]:
        dl_h = np.sum(down_last > thr) / 4
        dt_h = np.sum(down_this > thr) / 2
        ratios.append(dt_h / dl_h if dl_h > 0 else 0)
    
    ratio_spread = np.std(ratios) / np.mean(ratios)
    print(f"Ratio constancy (std/mean across thr 5-50): {ratio_spread:.4f}")

    if ratio_spread < 0.1 and down_med_ratio > 0.9:
        print(f"\n>>> DIAGNOSIS: Gain stable. Ratio near-constant across thresholds.")
        print(f"    Pulse spectrum shape unchanged → NOT a gain/HV drift problem.")
        print(f"    Lower detector is genuinely seeing ~{(1-np.mean(ratios))*100:.0f}% fewer events.")
        if np.mean(up_this) / np.mean(up_last) > 0.9:
            print(f"    Upper detector rate ~stable — rules out cosmic ray flux change.")
            print(f"    >>> Most likely: GEOMETRY MISALIGNMENT of lower detector,")
            print(f"        or partial blockage/obstruction between detectors.")
        else:
            print(f"    Both detectors affected → could be flux change or trigger issue.")
    elif ratio_spread > 0.2 or down_med_ratio < 0.8:
        print(f"\n>>> DIAGNOSIS: Gain shift detected on lower detector.")
        print(f"    Ratio varies with threshold ({ratio_spread:.3f}), median shifted.")
        print(f"    >>> Most likely: HV drift on lower detector channel.")
    else:
        print(f"\n>>> DIAGNOSIS: Mixed signals — moderate ratio spread ({ratio_spread:.3f}).")
        print(f"    Could be combination of gain drift + flux change + geometry.")

    # ====== PLOTS ======
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    fig.suptitle('Lower Detector Diagnostic: Last Week vs This Week', fontsize=14, fontweight='bold')

    # Row 1: Full area histograms
    ax = axes[0, 0]
    bins = np.linspace(-20, 300, 129)
    ax.hist(down_last, bins=bins, alpha=0.5, color='royalblue', density=True, label=f'Last week (n={len(down_last)})')
    ax.hist(down_this, bins=bins, alpha=0.5, color='crimson', density=True, label=f'This week (n={len(down_this)})')
    ax.axvline(30, color='black', ls='--', alpha=0.4)
    ax.set_title('Lower Detector: Full Area Spectrum (density)', fontsize=11)
    ax.legend(fontsize=8)
    ax.set_xlabel('Area')

    # Row 1: Pulse-only (>10) histogram
    ax = axes[0, 1]
    bins2 = np.linspace(10, 300, 117)
    ax.hist(down_last[down_last > 10], bins=bins2, alpha=0.5, color='royalblue', density=True,
            label=f'Last week (n={len(down_last)})')
    ax.hist(down_this[down_this > 10], bins=bins2, alpha=0.5, color='crimson', density=True,
            label=f'This week (n={len(down_this)})')
    ax.set_title('Lower Detector: Pulse Region Only (area > 10, density)', fontsize=11)
    ax.legend(fontsize=8)
    ax.set_xlabel('Area')

    # Row 2: CDF comparison
    ax = axes[1, 0]
    for arr, c, lab in [(down_last, 'royalblue', 'Last week'), (down_this, 'crimson', 'This week')]:
        s = np.sort(arr[arr > -100])
        cdf = np.arange(1, len(s) + 1) / len(s)
        ax.plot(s, cdf, color=c, linewidth=2, label=lab)
    ax.axvline(30, color='black', ls='--', alpha=0.4)
    ax.set_title('Lower Detector CDF (full range)', fontsize=11)
    ax.set_xlim(-10, 200)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Row 2: Pulse CDF (zoom)
    ax = axes[1, 1]
    for arr, c, lab in [(down_last[down_last > 10], 'royalblue', 'Last week'),
                         (down_this[down_this > 10], 'crimson', 'This week')]:
        s = np.sort(arr)
        cdf = np.arange(1, len(s) + 1) / len(s)
        ax.plot(s, cdf, color=c, linewidth=2, label=lab)
    ax.axvline(30, color='black', ls='--', alpha=0.4)
    ax.set_title('Lower Detector: Pulse CDF (area > 10)', fontsize=11)
    ax.set_xlim(10, 200)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Row 3: Ratio vs threshold plot
    ax = axes[2, 0]
    thresholds = np.arange(5, 101, 5)
    up_ratios = []
    down_ratios = []
    for thr in thresholds:
        ul_h = np.sum(up_last > thr) / 4
        ut_h = np.sum(up_this > thr) / 2
        dl_h = np.sum(down_last > thr) / 4
        dt_h = np.sum(down_this > thr) / 2
        up_ratios.append(ut_h / ul_h if ul_h > 0 else 0)
        down_ratios.append(dt_h / dl_h if dl_h > 0 else 0)
    
    ax.plot(thresholds, up_ratios, 's-', color='royalblue', linewidth=2, label='Upper detector (this/last)')
    ax.plot(thresholds, down_ratios, 'o-', color='crimson', linewidth=2, label='Lower detector (this/last)')
    ax.axhline(1.0, color='gray', ls='--', alpha=0.5)
    ax.set_xlabel('Area threshold', fontsize=11)
    ax.set_ylabel('Count rate ratio (this week / last week)', fontsize=11)
    ax.set_title('Threshold-Dependent Count Ratio\n(constant = geometry loss, sloping = gain shift)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.2)

    # Row 3: Per-file lower detector pulse median
    ax = axes[2, 1]
    plates = [0, 10, 20, 30, 40, 50]
    weeks = ['last', 'last', 'last', 'last', 'this', 'this']
    colors = ['royalblue', 'royalblue', 'royalblue', 'royalblue', 'crimson', 'crimson']
    down_meds = []
    up_meds = []
    for n in plates:
        fp = {**FILES_LAST, **FILES_THIS}[n]
        a1, a2 = load_areas(fp)
        down_meds.append(np.median(a2[a2 > 10]))
        up_meds.append(np.median(a1[a1 > 10]))
    
    ax.plot(plates[:4], down_meds[:4], 'o-', color='royalblue', linewidth=2, markersize=8, label='Lower detector (last)')
    ax.plot(plates[4:], down_meds[4:], 's-', color='crimson', linewidth=2, markersize=8, label='Lower detector (this)')
    ax.set_xlabel('Plates', fontsize=11)
    ax.set_ylabel('Median area of pulses (area > 10)', fontsize=11)
    ax.set_title('Pulse Median vs Lead Thickness\n(Gain shift would show jump at week boundary)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)

    fig.tight_layout()
    plt.savefig('/home/guiyu/workspace/CAEN/data/diagnostic_lower_v2.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: /home/guiyu/workspace/CAEN/data/diagnostic_lower_v2.png")
    plt.show()


if __name__ == '__main__':
    main()
