#!/usr/bin/env python3
"""
Calculate cosmic ray velocity from timing information.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
import sys
import os


def calculate_velocity(file_path, distance_cm, sampling_rate_GHz=5.0,
                      area_threshold=30, area2_threshold=30):
    """
    Calculate cosmic ray velocity from detector timing.

    Parameters:
    -----------
    file_path : str
        Path to the ROOT file
    distance_cm : float
        Distance between upper and lower detectors (in cm)
    sampling_rate_GHz : float
        Sampling rate in GHz (default: 5.0 GHz for DT5742)
    area_threshold : float
        Threshold for area (upper detector)
    area2_threshold : float
        Threshold for area2 (lower detector)
    """

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    # Calculate sampling interval in nanoseconds
    sampling_interval_ns = 1.0 / sampling_rate_GHz

    # Convert distance to meters
    distance_m = distance_cm / 100.0

    print(f"Analyzing: {file_path}")
    print("=" * 80)
    print(f"Detector distance: {distance_cm} cm = {distance_m} m")
    print(f"Sampling rate: {sampling_rate_GHz} GHz")
    print(f"Sampling interval: {sampling_interval_ns} ns")
    print("=" * 80)

    try:
        with uproot.open(file_path) as root_file:
            tree = root_file["t1"]

            # Read data
            area = tree["area"].array(library="np")
            area2 = tree["area2"].array(library="np")
            index_minamp1 = tree["Index_minamp1"].array(library="np")
            index_minamp2 = tree["Index_minamp2"].array(library="np")

            # Apply coincidence cut
            coincidence_cut = (area > area_threshold) & (area2 > area2_threshold)

            # Get coincidence events
            index1_coin = index_minamp1[coincidence_cut]
            index2_coin = index_minamp2[coincidence_cut]

          # Calculate time difference (in ns)
            # Positive means signal arrives at detector 2 (lower) after detector 1 (upper)
            time_diff_ns = (index2_coin - index1_coin) * sampling_interval_ns

            # Calculate velocity (in m/s)
            # velocity = distance / time
            # Need to convert time from ns to s
            velocity_m_per_s = distance_m / (time_diff_ns * 1e-9)

         # Convert to c (speed of light = 299792458 m/s)
            c = 299792458  # m/s
            velocity_fraction_c = velocity_m_per_s / c

            # Statistics
            n_coincidence = np.sum(coincidence_cut)

            print(f"\nCoincidence events: {n_coincidence}")
            print(f"\nTiming statistics:")
            print(f"  Index_minamp1 (upper detector):")
            print(f"    Mean: {np.mean(index1_coin):.2f}")
            print(f"    Std:  {np.std(index1_coin):.2f}")
            print(f"  Index_minamp2 (lower detector):")
            print(f"    Mean: {np.mean(index2_coin):.2f}")
            print(f"    Std:  {np.std(index2_coin):.2f}")

            print(f"\nTime difference (index2 - index1):")
            print(f"  Mean: {np.mean(index2_coin - index1_coin):.2f} samples")
            print(f"  Std:  {np.std(index2_coin - index1_coin):.2f} samples")
            print(f"  Mean: {np.mean(time_diff_ns):.2f} ns")
            print(f"  Std:  {np.std(time_diff_ns):.2f} ns")

            # Filter out unrealistic velocities (e.g., negative or > c)
            valid_velocity = (time_diff_ns > 0) & (velocity_fraction_c < 1.5) & (velocity_fraction_c > 0)
            n_valid = np.sum(valid_velocity)

        print(f"\nValid velocity events: {n_valid} / {n_coincidence} ({n_valid/n_coincidence*100:.1f}%)")

        if n_valid > 0:
            velocity_valid = velocity_m_per_s[valid_velocity]
            velocity_c_valid = velocity_fraction_c[valid_velocity]

            print(f"\nVelocity statistics (valid events only):")
            print(f"  Mean: {np.mean(velocity_valid):.2e} m/s = {np.mean(velocity_c_valid):.4f} c")
            print(f"  Median: {np.median(velocity_valid):.2e} m/s = {np.median(velocity_c_valid):.4f} c")
            print(f"  Std:  {np.std(velocity_valid):.2e} m/s")
            print(f"\nExpected cosmic ray velocity: ~0.99 c = {0.99*c:.2e} m/s")

            # Create histogram
            plt.figure(figsize=(12, 5))

            plt.subplot(1, 2, 1)
            plt.hist(time_diff_ns[valid_velocity], bins=50, edgecolor='black', alpha=0.7)
            plt.xlabel('Time difference (ns)')
            plt.ylabel('Counts')
            plt.title('Time difference between detectors')
            plt.grid(True, alpha=0.3)

            plt.subplot(1, 2, 2)
            plt.hist(velocity_c_valid, bins=50, edgecolor='black', alpha=0.7)
            plt.xlabel('Velocity (fraction of c)')
            plt.ylabel('Counts')
            plt.title('Cosmic ray velocity distribution')
            plt.axvline(0.99, color='r', linestyle='--', label='Expected ~0.99c')
            plt.legend()
            plt.grid(True, alpha=0.3)

            plt.tight_layout()
            output_file = file_path.replace('.root', '_velocity.png')
            plt.savefig(output_file, dpi=150)
            print(f"\nPlot saved to: {output_file}")

            return {
                  'n_coincidence': n_coincidence,
          'n_valid': n_valid,
                    'mean_velocity_m_s': np.mean(velocity_valid),
            'mean_velocity_c': np.mean(velocity_c_valid),
               'median_velocity_c': np.median(velocity_c_valid)
             }
        else:
            print("\nWARNING: No valid velocity measurements!")
            print("Check if:")
            print("  1. Detector distance is correct")
            print("  2. Sampling rate is correct")
            print("  3. Index_minamp1 and Index_minamp2 are properly saved")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python calculate_velocity.py <root_file> <distance_cm> [sampling_rate_GHz] [area_threshold] [area2_threshold]")
        print("\nExample:")
        print("  python calculate_velocity.py 5181b.root 50.0")
        print("  python calculate_velocity.py 5181b.root 50.0 5.0 30 30")
        print("\nParameters:")
        print("  distance_cm: Distance between upper and lower detectors (in cm)")
        print("  sampling_rate_GHz: Sampling rate (default: 5.0 GHz)")
        print("  area_threshold: Threshold for upper detector (default: 30)")
        print("  area2_threshold: Threshold for lower detector (default: 30)")
        sys.exit(1)

    file_path = sys.argv[1]
    distance_cm = float(sys.argv[2])
    sampling_rate_GHz = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
    area_threshold = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0
    area2_threshold = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0

    calculate_velocity(file_path, distance_cm, sampling_rate_GHz, area_threshold, area2_threshold)
