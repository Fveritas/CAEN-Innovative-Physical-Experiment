#!/usr/bin/env python3
"""
Analyze timing information to estimate cosmic ray velocity.
"""

import uproot
import numpy as np
import sys
import os


def analyze_timing(file_path, area_threshold=30, area2_threshold=30):
    """
    Analyze timing information from cosmic ray data.

    Note: The current ROOT file only stores Index_minamp for one channel.
    To properly measure velocity, we need timing info from BOTH detectors.
    """

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"Analyzing timing: {file_path}")
    print("=" * 80)

    try:
        with uproot.open(file_path) as root_file:
            tree = root_file["t1"]

            # Read data
            area = tree["area"].array(library="np")
            area2 = tree["area2"].array(library="np")
            index_minamp = tree["Index_minamp"].array(library="np")

       # Apply coincidence cut
            coincidence_cut = (area > area_threshold) & (area2 > area2_threshold)

          # Get coincidence events
            index_minamp_coin = index_minamp[coincidence_cut]

            print(f"\nCoincidence events: {np.sum(coincidence_cut)}")
            print(f"\nIndex_minamp statistics (for coincidence events):")
            print(f"  Min:  {np.min(index_minamp_coin)}")
            print(f"  Max:  {np.max(index_minamp_coin)}")
            print(f"  Mean: {np.mean(index_minamp_coin):.2f}")
            print(f"  Std:  {np.std(index_minamp_coin):.2f}")

            print(f"\n" + "=" * 80)
            print("LIMITATION:")
            print("The current data processing (Get_AllValue_Measure.C) only saves")
            print("Index_minamp for ONE channel (the last one processed).")
            print("\nTo measure cosmic ray velocity, you need:")
            print("  1. Peak time from BOTH detectors (upper and lower)")
            print("  2. Distance between the two detectors")
            print("\nSuggested fix:")
            print("  Modify Get_AllValue_Measure.C to save TWO variables:")
            print("    - Index_minamp1 (for channel 0 / upper detector)")
            print("    - Index_minamp2 (for channel 1 / lower detector)")
            print("  Then: time_diff = (Index_minamp2 - Index_minamp1) * sampling_interval")
            print("        velocity = distance / time_diff")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_timing.py <root_file> [area_threshold] [area2_threshold]")
        sys.exit(1)

    file_path = sys.argv[1]
    area_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    area2_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0

    analyze_timing(file_path, area_threshold, area2_threshold)
