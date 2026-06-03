# Data Processing

This directory contains preprocessing scripts for converting large CAEN ROOT
files into lightweight NumPy files used by later analysis.

## Script

Dependencies:

```bash
python3 -m pip install -r requirements.txt
```

If the editor reports that `uproot` cannot be resolved, select the same
Python interpreter used in the terminal. In this workspace, `/usr/bin/python3`
can import `uproot`.

```bash
python3 data_processing/preprocess_root_data.py --overwrite
```

Default behavior:

- reads ROOT files from `Raw_data/`
- saves processed arrays to `Processed_data/npz/`
- saves run summaries to `Processed_data/summary/`
- keeps only core scalar branches:
  - `area`
  - `area2`
  - `amp`
  - `base`
  - `rms`
  - `Index_minamp`
  - optional time branches when available in `5181b.root`

Use extended mode to also save `Index`, `overshoot`, and `overshoot_Last`:

```bash
python3 data_processing/preprocess_root_data.py --branches extended --overwrite
```

Process selected runs only:

```bash
python3 data_processing/preprocess_root_data.py --runs 5181 5182 --overwrite
```

## Output Layout

```text
Processed_data/
  npz/
    5181.npz
    5182.npz
    ...
  summary/
    preprocess_summary.csv
    preprocess_summary.json
```

Each `.npz` file contains event arrays plus run metadata:

- `week`
- `lead_plates`
- `lead_thickness_mm`
- `radiation_lengths`
- `mass_thickness_g_cm2`

The summary files contain quick checks such as event count, mean `area`,
mean `area2`, and the number of events passing the default
`area > 30` and `area2 > 30` coincidence cut.
