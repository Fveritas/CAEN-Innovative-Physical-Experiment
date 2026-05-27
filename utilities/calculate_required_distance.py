#!/usr/bin/env python3
"""
Calculate required detector distance for velocity measurement.
"""

import numpy as np

# Constants
c = 29.9792458  # speed of light in cm/ns
v_cosmic = 0.99 * c  # cosmic ray velocity ~0.99c in cm/ns
sampling_interval_ns = 4.0  # 250 MS/s = 4 ns per sample

print("=" * 80)
print("Detector Distance Requirements for Cosmic Ray Velocity Measurement")
print("=" * 80)
print(f"\nCurrent setup:")
print(f"  Sampling rate: 250 MS/s")
print(f"  Sampling interval: {sampling_interval_ns} ns")
print(f"  Cosmic ray velocity: ~0.99c = {v_cosmic:.2f} cm/ns")
print("\n" + "=" * 80)

print(f"\nDistance vs Time Difference:")
print(f"{'Distance (cm)':<15} {'Time (ns)':<15} {'Samples':<15} {'Measurable?'}")
print("-" * 60)

distances = [10, 16, 20, 30, 40, 50, 60, 80, 100, 120, 150, 200]

for distance in distances:
    time_diff_ns = distance / v_cosmic
    time_diff_samples = time_diff_ns / sampling_interval_ns

    # Consider measurable if time difference >= 2 samples (for reasonable resolution)
    # and >= 5 samples for good resolution
    if time_diff_samples >= 5:
        measurable = "✓ Good"
    elif time_diff_samples >= 2:
        measurable = "△ Marginal"
    else:
        measurable = "✗ Poor"

    print(f"{distance:<15} {time_diff_ns:<15.2f} {time_diff_samples:<15.2f} {measurable}")

print("\n" + "=" * 80)
print("Recommendations:")
print("=" * 80)

# Calculate minimum distance for different resolution requirements
min_samples_marginal = 2
min_samples_good = 5
min_samples_excellent = 10

dist_marginal = min_samples_marginal * sampling_interval_ns * v_cosmic
dist_good = min_samples_good * sampling_interval_ns * v_cosmic
dist_excellent = min_samples_excellent * sampling_interval_ns * v_cosmic

print(f"\nFor MARGINAL resolution (≥2 samples):")
print(f"  Minimum distance: {dist_marginal:.1f} cm = {dist_marginal/100:.2f} m")
print(f"  Time difference: {min_samples_marginal * sampling_interval_ns:.1f} ns")

print(f"\nFor GOOD resolution (≥5 samples):")
print(f"  Minimum distance: {dist_good:.1f} cm = {dist_good/100:.2f} m")
print(f"  Time difference: {min_samples_good * sampling_interval_ns:.1f} ns")

print(f"\nFor EXCELLENT resolution (≥10 samples):")
print(f"  Minimum distance: {dist_excellent:.1f} cm = {dist_excellent/100:.2f} m")
print(f"  Time difference: {min_samples_excellent * sampling_interval_ns:.1f} ns")

print("\n" + "=" * 80)
print("Current setup (16 cm):")
print("=" * 80)
current_time = 16 / v_cosmic
current_samples = current_time / sampling_interval_ns
print(f"  Distance: 16 cm")
print(f"  Expected time difference: {current_time:.2f} ns")
print(f"  Expected samples: {current_samples:.2f}")
print(f"  Status: ✗ INSUFFICIENT - time difference is much smaller than sampling interval")
print(f"\n  This explains why your measurement shows:")
print(f"    - Nearly symmetric distribution (48.9% positive, 46.5% negative)")
print(f"    - Median = 0 samples")
print(f"    - Large noise (std = 11 samples)")
print("\n" + "=" * 80)
