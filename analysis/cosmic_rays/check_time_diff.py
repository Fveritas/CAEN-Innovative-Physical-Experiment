#!/usr/bin/env python3
"""
Check the time difference distribution in detail.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt

file_path = "/home/guiyu/workspace/CAEN/5181b.root"

with uproot.open(file_path) as root_file:
    tree = root_file["t1"]

    area = tree["area"].array(library="np")
    area2 = tree["area2"].array(library="np")
    index_minamp1 = tree["Index_minamp1"].array(library="np")
    index_minamp2 = tree["Index_minamp2"].array(library="np")

    # Apply coincidence cut
    coincidence_cut = (area > 30) & (area2 > 30)

    index1_coin = index_minamp1[coincidence_cut]
    index2_coin = index_minamp2[coincidence_cut]

    # Time difference in samples
    time_diff_samples = index2_coin - index1_coin

    # Time difference in ns (4 ns per sample)
    time_diff_ns = time_diff_samples * 4.0

    print(f"Coincidence events: {np.sum(coincidence_cut)}")
    print(f"\nTime difference statistics (samples):")
    print(f"  Min:    {np.min(time_diff_samples)}")
    print(f"  Max:    {np.max(time_diff_samples)}")
    print(f"  Mean:   {np.mean(time_diff_samples):.2f}")
    print(f"  Median: {np.median(time_diff_samples):.2f}")
    print(f"  Std:    {np.std(time_diff_samples):.2f}")

    print(f"\nTime difference statistics (ns):")
    print(f"  Min:    {np.min(time_diff_ns):.2f}")
    print(f"  Max:    {np.max(time_diff_ns):.2f}")
    print(f"  Mean:   {np.mean(time_diff_ns):.2f}")
    print(f"  Median: {np.median(time_diff_ns):.2f}")
    print(f"  Std:    {np.std(time_diff_ns):.2f}")

    # Count positive, negative, and zero
    n_positive = np.sum(time_diff_samples > 0)
    n_negative = np.sum(time_diff_samples < 0)
    n_zero = np.sum(time_diff_samples == 0)

    print(f"\nTime difference distribution:")
    print(f"  Positive (lower after upper): {n_positive} ({n_positive/len(time_diff_samples)*100:.1f}%)")
    print(f"  Negative (upper after lower): {n_negative} ({n_negative/len(time_diff_samples)*100:.1f}%)")
    print(f"  Zero (simultaneous):          {n_zero} ({n_zero/len(time_diff_samples)*100:.1f}%)")

    # Expected time for cosmic rays at ~c
    expected_time_ns = 16.0 / 29.9792458  # distance(cm) / c(cm/ns)
    print(f"\nExpected time difference for v≈c: {expected_time_ns:.2f} ns")
    print(f"This corresponds to: {expected_time_ns/4.0:.2f} samples")

    # Plot histogram
    plt.figure(figsize=(14, 5))

    plt.subplot(1, 3, 1)
    plt.hist(time_diff_samples, bins=100, edgecolor='black', alpha=0.7)
    plt.xlabel('Time difference (samples)')
    plt.ylabel('Counts')
    plt.title('Time difference distribution')
    plt.axvline(0, color='r', linestyle='--', label='Zero')
    plt.axvline(expected_time_ns/4.0, color='g', linestyle='--', label=f'Expected ~{expected_time_ns/4.0:.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 3, 2)
    plt.hist(time_diff_ns, bins=100, edgecolor='black', alpha=0.7)
    plt.xlabel('Time difference (ns)')
    plt.ylabel('Counts')
    plt.title('Time difference distribution')
    plt.axvline(0, color='r', linestyle='--', label='Zero')
    plt.axvline(expected_time_ns, color='g', linestyle='--', label=f'Expected ~{expected_time_ns:.2f} ns')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 3, 3)
    # Zoom in on reasonable range
    reasonable_range = (time_diff_ns > -20) & (time_diff_ns < 20)
    plt.hist(time_diff_ns[reasonable_range], bins=80, edgecolor='black', alpha=0.7)
    plt.xlabel('Time difference (ns)')
    plt.ylabel('Counts')
    plt.title('Time difference (zoomed: -20 to 20 ns)')
    plt.axvline(0, color='r', linestyle='--', label='Zero')
    plt.axvline(expected_time_ns, color='g', linestyle='--', label=f'Expected ~{expected_time_ns:.2f} ns')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/home/guiyu/workspace/CAEN/time_diff_analysis.png', dpi=150)
    print(f"\nPlot saved to: /home/guiyu/workspace/CAEN/time_diff_analysis.png")
