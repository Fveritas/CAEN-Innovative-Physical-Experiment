#!/usr/bin/env python3
"""
Cosmic ray analysis script for CAEN data.
Analyzes area and area2 distributions and coincidence events.
"""

import uproot
import numpy as np
import sys
import os


def analyze_cosmic_rays(file_path, area_threshold=30, area2_threshold=30):
    """
    Analyze cosmic ray data from ROOT file.

    Parameters:
    -----------
    file_path : str
        Path to the ROOT file
    area_threshold : float
      Threshold for area (detector 1)
    area2_threshold : float
        Threshold for area2 (detector 2)
  """

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"Analyzing: {file_path}")
    print("=" * 80)

    try:
        with uproot.open(file_path) as root_file:
            tree = root_file["t1"]

            # Read data
            area = tree["area"].array(library="np")
            area2 = tree["area2"].array(library="np")

            total_entries = len(area)

            # Apply cuts
            area_cut = area > area_threshold
            area2_cut = area2 > area2_threshold
            coincidence_cut = area_cut & area2_cut

            # Count events
            n_area = np.sum(area_cut)
            n_area2 = np.sum(area2_cut)
            n_coincidence = np.sum(coincidence_cut)

            # Print results
            print(f"\nTotal entries: {total_entries}")
            print(f"\nThresholds:")
            print(f"  area  > {area_threshold}")
            print(f"  area2 > {area2_threshold}")
            print(f"\nResults:")
            print(f"  Upper detector (area > {area_threshold}):  {n_area:6d} events ({n_area/total_entries*100:6.2f}%)")
            print(f"  Lower detector (area2 > {area2_threshold}): {n_area2:6d} events ({n_area2/total_entries*100:6.2f}%)")
            print(f"  Coincidence (both):                         {n_coincidence:6d} events ({n_coincidence/total_entries*100:6.2f}%)")

         # Statistics
            print(f"\nArea statistics:")
            print(f"  Min:  {np.min(area):8.2f}")
            print(f"  Max:  {np.max(area):8.2f}")
            print(f"  Mean: {np.mean(area):8.2f}")
            print(f"  Std:  {np.std(area):8.2f}")

            print(f"\nArea2 statistics:")
            print(f"  Min:  {np.min(area2):8.2f}")
            print(f"  Max:  {np.max(area2):8.2f}")
            print(f"  Mean: {np.mean(area2):8.2f}")
            print(f"  Std:  {np.std(area2):8.2f}")

            # Efficiency
            if n_area > 0:
                efficiency = n_coincidence / n_area * 100
                print(f"\nCoincidence efficiency (relative to upper detector): {efficiency:.2f}%")

            return {
             'total': total_entries,
                'n_area': n_area,
                'n_area2': n_area2,
            'n_coincidence': n_coincidence
            }

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_cosmic_rays.py <root_file> [area_threshold] [area2_threshold]")
        print("\nExample:")
        print("  python analyze_cosmic_rays.py 5181.root")
        print("  python analyze_cosmic_rays.py 5181.root 30 30")
        sys.exit(1)

    file_path = sys.argv[1]
    area_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    area2_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0

    analyze_cosmic_rays(file_path, area_threshold, area2_threshold)
