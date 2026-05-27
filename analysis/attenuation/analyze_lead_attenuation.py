#!/usr/bin/env python3
"""
Analyze cosmic ray attenuation with lead shielding.
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

# Configuration
files = {
    '5181b.root': {'n_plates': 0, 'thickness_mm': 0.0},
    '5182b.root': {'n_plates': 10, 'thickness_mm': 5.0},
    '5183b.root': {'n_plates': 20, 'thickness_mm': 10.0},
    '5184b.root': {'n_plates': 30, 'thickness_mm': 15.0},
    '5185b.root': {'n_plates': 40, 'thickness_mm': 20.0},
}

base_path = "/home/guiyu/workspace/CAEN/"
area_threshold = 30.0
area2_threshold = 30.0

print("=" * 80)
print("COSMIC RAY ATTENUATION ANALYSIS")
print("=" * 80)
print(f"\nLead plate thickness: 0.5 mm per plate")
print(f"Thresholds: area > {area_threshold}, area2 > {area2_threshold}")
print("\n" + "=" * 80)

# Collect data from all files
results = []

for filename, config in files.items():
    filepath = os.path.join(base_path, filename)

    if not os.path.exists(filepath):
        print(f"⚠ Warning: {filename} not found, skipping...")
        continue

    try:
        with uproot.open(filepath) as root_file:
            tree = root_file["t1"]

            area = tree["area"].array(library="np")
            area2 = tree["area2"].array(library="np")

            total_events = len(area)
          area_cut = area > area_threshold
            area2_cut = area2 > area2_threshold
            coincidence_cut = area_cut & area2_cut

       n_area = np.sum(area_cut)
            n_area2 = np.sum(area2_cut)
            n_coincidence = np.sum(coincidence_cut)

          results.append({
             'filename': filename,
                'n_plates': config['n_plates'],
                'thickness_mm': config['thickness_mm'],
              'total_events': total_events,
                'n_area': n_area,
             'n_area2': n_area2,
                'n_coincidence': n_coincidence,
             'coincidence_rate': n_coincidence / total_events * 100
            })

            print(f"\n{filename} ({config['n_plates']} plates, {config['thickness_mm']:.1f} mm):")
            print(f"  Total events:      {total_events:6d}")
            print(f"  Upper detector:    {n_area:6d} ({n_area/total_events*100:5.2f}%)")
            print(f"  Lower detector:    {n_area2:6d} ({n_area2/total_events*100:5.2f}%)")
        print(f"  Coincidence:       {n_coincidence:6d} ({n_coincidence/total_events*100:5.2f}%)")

    except Exception as e:
        print(f"✗ Error reading {filename}: {e}")

if len(results) == 0:
    print("\n✗ No data files found!")
    exit(1)

# Sort by thickness
results.sort(key=lambda x: x['thickness_mm'])

# Extract data for fitting
thicknesses = np.array([r['thickness_mm'] for r in results])
coincidences = np.array([r['n_coincidence'] for r in results])
total_events_arr = np.array([r['total_events'] for r in results])

# Calculate uncertainties (Poisson statistics)
coincidence_errors = np.sqrt(coincidences)

print("\n" + "=" * 80)
print("ATTENUATION ANALYSIS")
print("=" * 80)

# Exponential attenuation model: N(x) = N0 * exp(-mu * x)
def exponential_attenuation(x, N0, mu):
    return N0 * np.exp(-mu * x)

# Fit the data
try:
    # Initial guess
    p0 = [coincidences[0], 0.05]  # N0 ~ first point, mu ~ 0.05 mm^-1

    popt, pcov = curve_fit(exponential_attenuation, thicknesses, coincidences,
               p0=p0, sigma=coincidence_errors, absolute_sigma=True)

    N0_fit, mu_fit = popt
    N0_err, mu_err = np.sqrt(np.diag(pcov))

    print(f"\nExponential fit: N(x) = N₀ × exp(-μx)")
    print(f"  N₀ (no shielding): {N0_fit:.1f} ± {N0_err:.1f} events")
    print(f"  μ (attenuation):   {mu_fit:.4f} ± {mu_err:.4f} mm⁻¹")
    print(f"  μ (attenuation):   {mu_fit*10:.4f} ± {mu_err*10:.4f} cm⁻¹")

    # Half-value layer (thickness to reduce intensity by 50%)
    hvl = np.log(2) / mu_fit
    hvl_err = hvl * (mu_err / mu_fit)
    print(f"  Half-value layer:  {hvl:.2f} ± {hvl_err:.2f} mm")

    # Calculate R-squared
    residuals = coincidences - exponential_attenuation(thicknesses, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((coincidences - np.mean(coincidences))**2)
    r_squared = 1 - (ss_res / ss_tot)
    print(f"  R² (goodness of fit): {r_squared:.4f}")

    # Theoretical comparison
    # For lead: μ ≈ 0.77 cm⁻¹ for cosmic ray muons (approximate)
    mu_theory_cm = 0.77  # cm^-1
    mu_theory_mm = mu_theory_cm / 10  # mm^-1
    print(f"\n  Theoretical μ (lead, muons): ~{mu_theory_mm:.4f} mm⁻¹")
    print(f"  Your measurement / Theory: {mu_fit/mu_theory_mm:.2f}")

except Exception as e:
    print(f"\n✗ Fitting failed: {e}")
    popt = None

print("\n" + "=" * 80)
print("ATTENUATION TABLE")
print("=" * 80)
print(f"{'Plates':<8} {'Thickness':<12} {'Coincidence':<15} {'Rate (%)':<10} {'Attenuation'}")
print(f"{'':8} {'(mm)':<12} {'Events':<15} {'':10} {'Factor'}")
print("-" * 80)

N0_measured = results[0]['n_coincidence']
for r in results:
    attenuation_factor = r['n_coincidence'] / N0_measured
    print(f"{r['n_plates']:<8} {r['thickness_mm']:<12.1f} {r['n_coincidence']:<15d} "
          f"{r['coincidence_rate']:<10.2f} {attenuation_factor:.4f}")

# Create plots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Linear scale
ax = axes[0]
ax.errorbar(thicknesses, coincidences, yerr=coincidence_errors,
            fmt='o', markersize=8, capsize=5, label='Measured data', color='blue')

if popt is not None:
    x_fit = np.linspace(0, max(thicknesses)*1.1, 100)
    y_fit = exponential_attenuation(x_fit, *popt)
    ax.plot(x_fit, y_fit, 'r-', linewidth=2,
            label=f'Fit: N₀={N0_fit:.0f}, μ={mu_fit:.4f} mm⁻¹')

ax.set_xlabel('Lead Thickness (mm)', fontsize=12)
ax.set_ylabel('Coincidence Events', fontsize=12)
ax.set_title('Cosmic Ray Attenuation by Lead', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 2: Log scale
ax = axes[1]
ax.errorbar(thicknesses, coincidences, yerr=coincidence_errors,
            fmt='o', markersize=8, capsize=5, label='Measured data', color='blue')

if popt is not None:
    ax.plot(x_fit, y_fit, 'r-', linewidth=2,
            label=f'Fit: N₀={N0_fit:.0f}, μ={mu_fit:.4f} mm⁻¹')

ax.set_xlabel('Lead Thickness (mm)', fontsize=12)
ax.set_ylabel('Coincidence Events (log scale)', fontsize=12)
ax.set_title('Cosmic Ray Attenuation (Log Scale)', fontsize=14, fontweight='bold')
ax.set_yscale('log')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, which='both')

plt.tight_layout()
output_file = os.path.join(base_path, 'lead_attenuation_analysis.png')
plt.savefig(output_file, dpi=150)
print(f"\nPlot saved to: {output_file}")

# Create attenuation factor plot
fig, ax = plt.subplots(figsize=(10, 6))

attenuation_factors = coincidences / N0_measured
attenuation_errors = attenuation_factors * np.sqrt((coincidence_errors/coincidences)**2 +
                   (coincidence_errors[0]/N0_measured)**2)

ax.errorbar(thicknesses, attenuation_factors, yerr=attenuation_errors,
          fmt='o', markersize=8, capsize=5, label='Measured', color='blue')

if popt is not None:
    y_fit_normalized = exponential_attenuation(x_fit, *popt) / N0_fit
    ax.plot(x_fit, y_fit_normalized, 'r-', linewidth=2,
            label=f'Fit: exp(-{mu_fit:.4f}x)')

ax.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='50% attenuation')
if popt is not None:
    ax.axvline(x=hvl, color='green', linestyle='--', alpha=0.5)
    ax.text(hvl, 0.55, f'HVL={hvl:.1f}mm', fontsize=10, color='green')

ax.set_xlabel('Lead Thickness (mm)', fontsize=12)
ax.set_ylabel('Transmission Factor (N/N₀)', fontsize=12)
ax.set_title('Cosmic Ray Transmission Through Lead', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 1.1])

plt.tight_layout()
output_file2 = os.path.join(base_path, 'transmission_factor.png')
plt.savefig(output_file2, dpi=150)
print(f"Plot saved to: {output_file2}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
