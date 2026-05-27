#!/usr/bin/env python3
"""
Analyze what can be measured with current data setup.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import sys

def analyze_capabilities(file_path, area_threshold=30, area2_threshold=30):
    """
    Analyze what measurements are possible with current setup.
    """

    print("=" * 80)
    print("Analysis of Current Data Capabilities")
    print("=" * 80)

    with uproot.open(file_path) as root_file:
        tree = root_file["t1"]

        # Read all relevant data
        area = tree["area"].array(library="np")
        area2 = tree["area2"].array(library="np")
        amp = tree["amp"].array(library="np")
        base = tree["base"].array(library="np")
        rms = tree["rms"].array(library="np")

        total_events = len(area)

        # Apply cuts
        area_cut = area > area_threshold
      area2_cut = area2 > area2_threshold
      coincidence_cut = area_cut & area2_cut

        n_area = np.sum(area_cut)
        n_area2 = np.sum(area2_cut)
        n_coincidence = np.sum(coincidence_cut)

     print(f"\n{'='*80}")
        print("1. COSMIC RAY COUNTING (✓ EXCELLENT)")
        print(f"{'='*80}")
        print(f"Total events recorded: {total_events}")
        print(f"Upper detector triggers (area > {area_threshold}): {n_area} ({n_area/total_events*100:.2f}%)")
        print(f"Lower detector triggers (area2 > {area_threshold}): {n_area2} ({n_area2/total_events*100:.2f}%)")
        print(f"Coincidence events (cosmic rays): {n_coincidence} ({n_coincidence/total_events*100:.2f}%)")
        print(f"\nCoincidence rate: {n_coincidence/n_area*100:.1f}% of upper detector triggers")
        print("\n✓ This is RELIABLE for:")
        print("  - Measuring cosmic ray flux (count rate)")
      print("  - Studying lead shielding attenuation")
        print("  - Comparing different configurations")

     print(f"\n{'='*80}")
     print("2. ENERGY/CHARGE MEASUREMENT (✓ GOOD)")
        print(f"{'='*80}")

        # Analyze energy distribution for coincidence events
        area_coin = area[coincidence_cut]
        area2_coin = area2[coincidence_cut]

        print(f"\nCharge distribution (coincidence events):")
        print(f"  Upper detector (area):")
        print(f"    Mean:   {np.mean(area_coin):.2f} pC")
        print(f"  Median: {np.median(area_coin):.2f} pC")
        print(f"    Std:    {np.std(area_coin):.2f} pC")
        print(f"    Range:  {np.min(area_coin):.2f} - {np.max(area_coin):.2f} pC")

        print(f"  Lower detector (area2):")
        print(f"    Mean:   {np.mean(area2_coin):.2f} pC")
      print(f"    Median: {np.median(area2_coin):.2f} pC")
        print(f"    Std:    {np.std(area2_coin):.2f} pC")
        print(f"    Range:  {np.min(area2_coin):.2f} - {np.max(area2_coin):.2f} pC")

        print("\n✓ This is RELIABLE for:")
        print("  - Energy deposition spectrum")
        print("  - Identifying different particle types (if sufficient statistics)")
        print("  - Quality cuts on events")

      print(f"\n{'='*80}")
        print("3. DETECTOR PERFORMANCE (✓ GOOD)")
        print(f"{'='*80}")

        print(f"\nNoise characteristics:")
        print(f"  Baseline RMS: {np.mean(rms):.2f} ± {np.std(rms):.2f} ADC counts")
        print(f"  Baseline level: {np.mean(base):.2f} ± {np.std(base):.2f} ADC counts")

        # Signal-to-noise ratio
        amp_coin = amp[coincidence_cut]
        snr = np.mean(amp_coin) / np.mean(rms)
     print(f"  Signal-to-noise ratio: {snr:.1f}")

     print("\n✓ This is RELIABLE for:")
        print("  - Monitoring detector health")
        print("  - Optimizing trigger thresholds")
        print("  - Identifying noisy channels")

        print(f"\n{'='*80}")
        print("4. ANGULAR DISTRIBUTION (△ POSSIBLE with caveats)")
        print(f"{'='*80}")

      print("\nWith multiple measurements at different angles:")
        print("  △ Can estimate angular dependence (cos²θ distribution)")
        print("  △ Requires careful geometry calibration")
        print("  △ Limited by detector acceptance")

      print(f"\n{'='*80}")
        print("5. VELOCITY MEASUREMENT (✗ NOT POSSIBLE)")
        print(f"{'='*80}")

        print("\nCurrent setup:")
        print(f"  Distance: 16 cm")
        print(f"  Expected time difference: 0.54 ns")
        print(f"  Sampling interval: 4 ns")
        print(f"  Time resolution: 0.13 samples")

        print("\n✗ NOT RELIABLE because:")
        print("  - Time difference << sampling interval")
        print("  - Dominated by timing jitter and noise")
        print("  - Would need ≥2.4 m distance or ≥1 GHz sampling")

        print(f"\n{'='*80}")
        print("RECOMMENDED ANALYSES FOR YOUR DATA")
        print(f"{'='*80}")

        print("\n1. Lead Shielding Attenuation Study:")
        print("   - Compare coincidence rates for different lead thicknesses")
        print("   - Fit exponential attenuation: N = N₀ × exp(-μx)")
    print("   - Extract attenuation coefficient μ")

        print("\n2. Energy Spectrum Analysis:")
        print("   - Plot charge distribution (area histogram)")
        print("   - Identify Landau distribution peak")
        print("   - Compare spectra with/without shielding")

        print("\n3. Detector Efficiency:")
        print("   - Calculate coincidence efficiency")
        print("   - Study efficiency vs threshold")
      print("   - Optimize trigger settings")

        print("\n4. Time Stability:")
        print("   - Monitor count rate vs time")
        print("   - Check for environmental effects")
        print("   - Verify detector stability")

        # Create summary plots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        # Plot 1: Event counts
        ax = axes[0, 0]
   categories = ['Total', 'Upper\n(area>30)', 'Lower\n(area2>30)', 'Coincidence']
        counts = [total_events, n_area, n_area2, n_coincidence]
      colors = ['gray', 'blue', 'green', 'red']
        ax.bar(categories, counts, color=colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel('Event Count')
     ax.set_title('Event Statistics')
        ax.grid(True, alpha=0.3, axis='y')

        # Plot 2: Charge distribution (upper)
    ax = axes[0, 1]
        ax.hist(area_coin, bins=50, range=(30, 200), edgecolor='black', alpha=0.7, color='blue')
        ax.set_xlabel('Charge (pC)')
        ax.set_ylabel('Counts')
        ax.set_title('Upper Detector Charge Distribution')
        ax.grid(True, alpha=0.3)

      # Plot 3: Charge distribution (lower)
        ax = axes[0, 2]
      ax.hist(area2_coin, bins=50, range=(30, 200), edgecolor='black', alpha=0.7, color='green')
        ax.set_xlabel('Charge (pC)')
        ax.set_ylabel('Counts')
        ax.set_title('Lower Detector Charge Distribution')
        ax.grid(True, alpha=0.3)

        # Plot 4: Correlation
        ax = axes[1, 0]
        ax.scatter(area_coin, area2_coin, alpha=0.3, s=10)
        ax.set_xlabel('Upper Detector Charge (pC)')
        ax.set_ylabel('Lower Detector Charge (pC)')
      ax.set_title('Charge Correlation')
        ax.grid(True, alpha=0.3)
        ax.plot([30, 200], [30, 200], 'r--', label='1:1 line')
        ax.legend()

        # Plot 5: Amplitude distribution
        ax = axes[1, 1]
        ax.hist(amp_coin, bins=50, edgecolor='black', alpha=0.7, color='orange')
        ax.set_xlabel('Amplitude (mV)')
        ax.set_ylabel('Counts')
        ax.set_title('Signal Amplitude Distribution')
        ax.grid(True, alpha=0.3)

        # Plot 6: Efficiency vs threshold
        ax = axes[1, 2]
        thresholds = np.linspace(10, 100, 20)
        efficiencies = []
        for thresh in thresholds:
            n_coin_thresh = np.sum((area > thresh) & (area2 > thresh))
            n_upper_thresh = np.sum(area > thresh)
            eff = n_coin_thresh / n_upper_thresh * 100 if n_upper_thresh > 0 else 0
          efficiencies.append(eff)
        ax.plot(thresholds, efficiencies, 'o-', color='purple')
        ax.axvline(area_threshold, color='r', linestyle='--', label=f'Current: {area_threshold}')
        ax.set_xlabel('Threshold (pC)')
        ax.set_ylabel('Coincidence Efficiency (%)')
     ax.set_title('Efficiency vs Threshold')
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        output_file = file_path.replace('.root', '_capabilities.png')
        plt.savefig(output_file, dpi=150)
        print(f"\n{'='*80}")
        print(f"Summary plots saved to: {output_file}")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_capabilities.py <root_file> [area_threshold] [area2_threshold]")
        sys.exit(1)

    file_path = sys.argv[1]
    area_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    area2_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0

    analyze_capabilities(file_path, area_threshold, area2_threshold)
