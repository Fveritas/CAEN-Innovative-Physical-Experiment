#!/usr/bin/env python3
"""
Script to read basic information from ROOT data files.
"""

import uproot
import numpy as np
import sys
import os


def print_tree_info(tree):
    """Print basic information about a TTree."""
    print(f"\n  Number of entries: {tree.num_entries}")
    print(f"  Branches ({len(tree.keys())}):")
    for branch_name in tree.keys():
        branch = tree[branch_name]
        print(f"    - {branch_name}: {branch.typename}")

def read_root_file_info(file_path):
    """Read and display basic information from a ROOT file."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"Opening ROOT file: {file_path}")
    print("=" * 80)

    try:
        with uproot.open(file_path) as root_file:
            print(f"\nFile: {file_path}")
            print(f"Keys in file: {root_file.keys()}")

            for key in root_file.keys():
                obj = root_file[key]
                print(f"\n{key}:")
                print(f"  Type: {obj.classname}")

                if obj.classname == "TTree":
                  print_tree_info(obj)

    except Exception as e:
        print(f"Error reading ROOT file: {e}")
        import traceback
        traceback.print_exc()


def read_branch_data(file_path, tree_name, branch_name, max_entries=10):
    """Read and display sample data from a specific branch."""
    try:
        with uproot.open(file_path) as root_file:
            tree = root_file[tree_name]
            data = tree[branch_name].array(library="np", entry_stop=max_entries)

            print(f"\nSample data from {tree_name}/{branch_name} (first {max_entries} entries):")
            print(data)
            print(f"\nData type: {data.dtype}")
            print(f"Shape: {data.shape}")

            if len(data) > 0:
                print(f"Min: {np.min(data)}")
                print(f"Max: {np.max(data)}")
                print(f"Mean: {np.mean(data)}")
    except Exception as e:
        print(f"Error reading branch data: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_data.py <root_file_path> [tree_name] [branch_name]")
        print("\nExamples:")
        print("  python read_data.py data.root")
        print("  python read_data.py data.root tree_name branch_name")
        sys.exit(1)

    file_path = sys.argv[1]

    if len(sys.argv) >= 4:
        tree_name = sys.argv[2]
        branch_name = sys.argv[3]
        read_branch_data(file_path, tree_name, branch_name)
    else:
        read_root_file_info(file_path)
