#!/usr/bin/env python3
"""
Fit quality analysis and references.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data
data = [
    {'plates': 0,  'thickness_mm': 0.0,  'coincidence': 3357},
    {'plates': 10, 'thickness_mm': 5.0,  'coincidence': 3136},
    {'plates': 20, 'thickness_mm': 10.0, 'coincidence': 3119},
    {'plates': 30, 'thickness_mm': 15.0, 'coincidence': 3046},
    {'plates': 40, 'thickness_mm': 20.0, 'coincidence': 1523},
]

thicknesses = np.array([d['thickness_mm'] for d in data])
coincidences = np.array([d['coincidence'] for d in data])
errors = np.sqrt(coincidences)

print("=" * 80)
print("DATA QUALITY ANALYSIS")
print("=" * 80)

# Fit with and without last point
def exp_fit(x, N0, mu):
    return N0 * np.exp(-mu * x)

# Fit all data
popt_all, _ = curve_fit(exp_fit, thicknesses, coincidences, p0=[3357, 0.05], sigma=errors)
chi2_all = np.sum(((coincidences - exp_fit(thicknesses, *popt_all)) / errors)**2)

# Fit without last point
popt_no_last, _ = curve_fit(exp_fit, thicknesses[:-1], coincidences[:-1],
                p0=[3357, 0.05], sigma=errors[:-1])
chi2_no_last = np.sum(((coincidences[:-1] - exp_fit(thicknesses[:-1], *popt_no_last)) / errors[:-1])**2)

print(f"\nFit with all 5 points:")
print(f"  mu = {popt_all[1]:.4f} mm^-1")
print(f"  chi^2/dof = {chi2_all:.2f} / 3 = {chi2_all/3:.2f}")

print(f"\nFit without last point (first 4 points only):")
print(f"  mu = {popt_no_last[1]:.4f} mm^-1")
print(f"  chi^2/dof = {chi2_no_last:.2f} / 2 = {chi2_no_last/2:.2f}")

# Check last point deviation
expected_last = exp_fit(thicknesses[-1], *popt_no_last)
deviation = (coincidences[-1] - expected_last) / errors[-1]
print(f"\nLast point (20mm) analysis:")
print(f"  Measured: {coincidences[-1]}")
print(f"  Expected (from first 4 points): {expected_last:.0f}")
print(f"  Deviation: {deviation:.2f} sigma")
if abs(deviation) > 3:
    print(f"  WARNING: >{abs(deviation):.1f} sigma deviation - possible outlier!")

print("\n" + "=" * 80)
print("KEY REFERENCES FOR COSMIC RAY ATTENUATION IN LEAD")
print("=" * 80)

print("""
1. Particle Data Group (PDG) - "Passage of Particles Through Matter"
   https://pdg.lbl.gov/2023/reviews/rpp2023-rev-passage-particles-matter.pdf
   - THE standard reference for particle interactions
   - Muon energy loss and range tables
   - Attenuation coefficients for all materials

2. Cecchini, S. & Spurio, M. (2012)
   "Atmospheric muons: experimental aspects"
   Geoscience Instrumentation, Methods and Data Systems, 1, 185-196
   DOI: 10.5194/gi-1-185-2012
   - Modern review of muon measurements
   - Practical experimental techniques

3. Gaisser, T.K. "Cosmic Rays and Particle Physics" (2016)
   Cambridge University Press
   - Chapter 3: Muon propagation through matter
   - Energy spectrum at sea level

4. Grieder, P.K.F. "Cosmic Rays at Earth" (2001)
   Elsevier
   - Comprehensive experimental techniques
   - Data analysis methods

5. Grupen, C. "Physics of Particle Detection" (2000)
   - Practical detector physics
   - Scintillator response

ONLINE RESOURCES:
- CERN Document Server: https://cds.cern.ch/
- arXiv physics.ins-det: https://arxiv.org/list/physics.ins-det/recent
- HyperPhysics: http://hyperphysics.phy-astr.gsu.edu/hbase/Astro/cosmic.html

KEY PHYSICS VALUES:
- Muon dE/dx in lead: ~1.5 MeV*cm^2/g (minimum ionizing)
- Lead density: 11.35 g/cm^3
- Energy loss: ~17 MeV/cm
- Typical cosmic ray muon energy: 1-4 GeV (mean ~4 GeV)
- Expected mu for thin lead: 0.05-0.10 mm^-1
- Attenuation length: 10-20 cm
""")

print("=" * 80)
print("POSSIBLE REASONS FOR POOR FIT (R^2 = 0.54)")
print("=" * 80)

print("""
1. LAST POINT ANOMALY
   - 20mm point shows {:.1f} sigma deviation
   - Much stronger attenuation than expected
   - Check 5185.root data quality

2. ENERGY THRESHOLD EFFECT
   - Your threshold (area > 30 pC) selects higher energy muons
   - High-energy muons have LOWER attenuation
   - Creates non-exponential behavior

3. MULTIPLE SCATTERING
   - Muons scatter in lead
   - Scattered muons may miss lower detector
   - Effect increases with thickness

4. GEOMETRIC ACCEPTANCE
   - 16 cm detector separation
   - Scattered particles at large angles miss detector
   - Acceptance decreases with thickness

5. ENERGY SPECTRUM HARDENING
   - Low-energy muons absorbed first
   - Remaining spectrum becomes "harder"
   - Harder spectrum has lower attenuation coefficient
""".format(abs(deviation)))

print("=" * 80)
print("RECOMMENDED NEXT STEPS")
print("=" * 80)

print("""
1. VERIFY LAST DATA POINT
   - Re-check 5185.root file
   - Verify experimental conditions were identical
   - Check for any anomalies in that run

2. FIT WITHOUT LAST POINT
   - Use first 4 points only
   - Compare mu values
   - Discuss discrepancy in report

3. ENERGY-DEPENDENT ANALYSIS
   - Bin events by charge: 30-50, 50-100, >100 pC
   - Fit each energy bin separately
   - Expect: higher energy -> lower mu

4. CHECK SINGLE RATES
   - Analyze upper detector rate vs thickness
   - Analyze lower detector rate vs thickness
   - Compare with coincidence rate

5. GEOMETRIC CORRECTION
   - Calculate scattering angle distribution
   - Estimate acceptance loss
   - Apply correction factor
""")

# Create diagnostic plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Comparison of fits
ax = axes[0, 0]
x_plot = np.linspace(0, 22, 100)
ax.errorbar(thicknesses, coincidences, yerr=errors, fmt='o', markersize=10,
          capsize=5, label='Data', color='blue', linewidth=2)
ax.plot(x_plot, exp_fit(x_plot, *popt_all), 'r-', linewidth=2,
        label=f'Fit (all 5): mu={popt_all[1]:.4f}')
ax.plot(x_plot, exp_fit(x_plot, *popt_no_last), 'g--', linewidth=2,
     label=f'Fit (first 4): mu={popt_no_last[1]:.4f}')
ax.set_xlabel('Thickness (mm)', fontsize=12, fontweight='bold')
ax.set_ylabel('Coincidence Events', fontsize=12, fontweight='bold')
ax.set_title('Comparison of Fits', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Plot 2: Residuals
ax = axes[0, 1]
residuals = coincidences - exp_fit(thicknesses, *popt_all)
ax.errorbar(thicknesses, residuals, yerr=errors, fmt='o', markersize=10, capsize=5, color='blue')
ax.axhline(0, color='r', linestyle='--', linewidth=2)
ax.fill_between([-1, 21], [-2*np.mean(errors), -2*np.mean(errors)],
                [2*np.mean(errors), 2*np.mean(errors)], alpha=0.2, color='gray', label='±2 sigma')
ax.set_xlabel('Thickness (mm)', fontsize=12, fontweight='bold')
ax.set_ylabel('Residuals', fontsize=12, fontweight='bold')
ax.set_title('Fit Residuals (All Points)', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Normalized residuals (pull)
ax = axes[1, 0]
norm_residuals = residuals / errors
colors = ['blue' if abs(r) < 2 else 'orange' if abs(r) < 3 else 'red' for r in norm_residuals]
ax.bar(thicknesses, norm_residuals, width=1.5, alpha=0.7, edgecolor='black', color=colors)
ax.axhline(0, color='black', linestyle='-', linewidth=2)
ax.axhline(2, color='orange', linestyle=':', linewidth=2, label='±2 sigma')
ax.axhline(-2, color='orange', linestyle=':', linewidth=2)
ax.axhline(3, color='red', linestyle=':', linewidth=2, label='±3 sigma')
ax.axhline(-3, color='red', linestyle=':', linewidth=2)
ax.set_xlabel('Thickness (mm)', fontsize=12, fontweight='bold')
ax.set_ylabel('Pull (sigma)', fontsize=12, fontweight='bold')
ax.set_title('Normalized Residuals', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim([-5, 5])

# Plot 4: Transmission with both fits
ax = axes[1, 1]
transmission = coincidences / coincidences[0]
trans_err = transmission * np.sqrt((errors/coincidences)**2 + (errors[0]/coincidences[0])**2)
ax.errorbar(thicknesses, transmission, yerr=trans_err, fmt='o', markersize=10,
            capsize=5, label='Data', color='blue', linewidth=2)
ax.plot(x_plot, exp_fit(x_plot, *popt_all)/popt_all[0], 'r-', linewidth=2,
        label='Fit (all 5)')
ax.plot(x_plot, exp_fit(x_plot, *popt_no_last)/popt_no_last[0], 'g--', linewidth=2,
        label='Fit (first 4)')
ax.set_xlabel('Thickness (mm)', fontsize=12, fontweight='bold')
ax.set_ylabel('Transmission (N/N0)', fontsize=12, fontweight='bold')
ax.set_title('Transmission Factor', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig('/home/guiyu/workspace/CAEN/fit_diagnostics.png', dpi=150, bbox_inches='tight')
print("\nDiagnostic plots saved: /home/guiyu/workspace/CAEN/fit_diagnostics.png")
print("=" * 80)
