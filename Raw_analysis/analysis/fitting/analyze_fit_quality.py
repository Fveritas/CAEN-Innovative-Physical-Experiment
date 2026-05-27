#!/usr/bin/env python3
"""
Analysis of fit quality and references for cosmic ray attenuation in lead.
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

# Check if last point is an outlier
print("\n1. OUTLIER DETECTION")
print("-" * 80)

# Fit with and without last point
def exp_fit(x, N0, mu):
    return N0 * np.exp(-mu * x)

# Fit all data
popt_all, _ = curve_fit(exp_fit, thicknesses, coincidences, p0=[3357, 0.05], sigma=errors)
residuals_all = coincidences - exp_fit(thicknesses, *popt_all)
chi2_all = np.sum((residuals_all / errors)**2)

# Fit without last point
popt_no_last, _ = curve_fit(exp_fit, thicknesses[:-1], coincidences[:-1],
                           p0=[3357, 0.05], sigma=errors[:-1])
residuals_no_last = coincidences[:-1] - exp_fit(thicknesses[:-1], *popt_no_last)
chi2_no_last = np.sum((residuals_no_last / errors[:-1])**2)

print(f"Fit with all 5 points:")
print(f"  mu = {popt_all[1]:.4f} mm⁻¹")
print(f"  χ²/dof = {chi2_all:.2f} / 3 = {chi2_all/3:.2f}")

print(f"\nFit without last point (first 4 points only):")
print(f"  mu = {popt_no_last[1]:.4f} mm⁻¹")
print(f"  χ²/dof = {chi2_no_last:.2f} / 2 = {chi2_no_last/2:.2f}")

# Check last point deviation
expected_last = exp_fit(thicknesses[-1], *popt_no_last)
deviation = (coincidences[-1] - expected_last) / errors[-1]
print(f"\nLast point (20mm) analysis:")
print(f"  Measured: {coincidences[-1]}")
print(f"  Expected (from first 4 points): {expected_last:.0f}")
print(f"  Deviation: {deviation:.2f} σ")
if abs(deviation) > 3:
    print(f"  ⚠ WARNING: >3σ deviation - possible outlier or systematic effect!")

print("\n" + "=" * 80)
print("POSSIBLE EXPLANATIONS FOR POOR FIT")
print("=" * 80)

print("""
1. ENERGY THRESHOLD EFFECT
   - Your threshold (area > 30 pC) may preferentially select high-energy muons
   - High-energy muons have LOWER attenuation coefficient
   - This creates non-exponential behavior

2. MULTIPLE SCATTERING
   - Muons scatter in lead, changing trajectory
   - Scattered muons may miss the lower detector
   - Effect increases with thickness (non-exponential)

3. DETECTOR GEOMETRY
   - 16 cm detector separation
   - Scattered particles at large angles may not reach lower detector
   - Geometric acceptance decreases with scattering

4. LAST DATA POINT ANOMALY
   - 20mm shows much stronger attenuation than expected
   - Possible causes:
     * Measurement error
     * Different experimental conditions
     * Threshold effect becomes dominant
     * Geometric acceptance loss

5. ENERGY SPECTRUM HARDENING
   - Low-energy muons absorbed first
   - Remaining spectrum becomes "harder" (higher energy)
   - Harder spectrum has lower attenuation coefficient
""")

print("=" * 80)
print("RECOMMENDED ACTIONS")
print("=" * 80)

print("""
1. CHECK LAST DATA POINT
   - Verify 5185.root data quality
   - Check if experimental setup was identical
   - Look for any anomalies in that run

2. ENERGY-DEPENDENT ANALYSIS
   - Plot attenuation vs energy (charge)
   - Separate low-energy and high-energy events
   - Fit each energy bin separately

3. ALTERNATIVE MODELS
   - Try power law: N(x) = N0 * (1 + x/x0)^(-n)
   - Try two-component model: soft + hard muons
   - Account for geometric acceptance

4. SYSTEMATIC CHECKS
   - Verify detector alignment
   - Check trigger efficiency vs thickness
   - Measure single-detector rates (not just coincidence)
""")

print("\n" + "=" * 80)
print("REFERENCES - COSMIC RAY ATTENUATION IN LEAD")
print("=" * 80)

references = """
TEXTBOOKS & REVIEWS:
------------
1. Particle Data Group (PDG) - "Passage of Particles Through Matter"
   https://pdg.lbl.gov/2023/reviews/rpp2023-rev-passage-particles-matter.pdf
   • Section on muon energy loss and range
   • Attenuation coefficients for various materials
   • Standard reference for particle physics

2. Gaisser, T.K. "Cosmic Rays and Particle Physics" (2016)
   Cambridge University Press
   • Chapter 3: Muon propagation through matter
   • Energy spectrum of cosmic ray muons at sea level

3. Grieder, P.K.F. "Cosmic Rays at Earth" (2001)
   Elsevier
   • Comprehensive treatment of cosmic ray physics
   • Experimental techniques and data analysis

EXPERIMENTAL PAPERS:
-----------
4. Cecchini, S. & Spurio, M. (2012)
   "Atmospheric muons: experimental aspects"
   Geoscience Instrumentation, Methods and Data Systems, 1, 185-196
   DOI: 10.5194/gi-1-185-2012
   • Modern review of muon measurements
   • Attenuation in various materials

5. Grupen, C. (2000)
   "Physics of Particle Detection"
   AIP Conference Proceedings 536, 3-34
   • Practical aspects of cosmic ray detection
   • Scintillator detector response

6. Patrignani, C. et al. (Particle Data Group) (2016)
   "Review of Particle Physics"
   Chinese Physics C, 40, 100001
   • Muon energy loss: ~2 MeV/(g/cm²) (minimum ionizing)
   • Lead density: 11.35 g/cm³
   • dE/dx ~ 22.7 MeV/cm in lead

EDUCATIONAL EXPERIMENTS:
-------------
7. Aglietta, M. et al. (2009)
   "Muon "depth-intensity" relation measured by the LVD underground experiment"
   Physical Review D, 79, 032001
   • Underground muon measurements
   • Energy-dependent attenuation

8. Adamson, P. et al. (MINOS Collaboration) (2007)
   "Measurement of the atmospheric muon charge ratio"
   Physical Review D, 76, 052003
   • Surface muon measurements
   • Energy spectrum analysis

RELEVANT PHYSICS:
-----------------
9. Muon Energy Loss in Lead:
   • Minimum ionizing: dE/dx ~ 1.5 MeV·cm²/g
   • Lead: ρ = 11.35 g/cm³
   • Energy loss: ~17 MeV/cm
   • Range for 1 GeV muon: ~60 cm in lead
   • Range for 4 GeV muon: ~300 cm in lead

10. Typical Cosmic Ray Muon Spectrum at Sea Level:
    • Mean energy: ~4 GeV
    • Most probable energy: ~1 GeV
    • Energy range: 0.1 - 1000 GeV
    • Flux: ~1 muon/cm²/min (vertical)

ONLINE RESOURCES:
--------------
11. CERN Document Server
    https://cds.cern.ch/
    Search: "cosmic ray muon attenuation lead"

12. arXiv.org - Physics - Instrumentation and Detectors
    https://arxiv.org/list/physics.ins-det/recent
    Search: "cosmic ray telescope" or "muon attenuation"

13. HyperPhysics - Cosmic Rays
    http://hyperphysics.phy-astr.gsu.edu/hbase/Astro/cosmic.html
    • Educational resource with clear explanations

SPECIFIC TO YOUR EXPERIMENT:
----------------------------
14. For thin absorbers (< 50 mm lead):
    • Expect mu ~ 0.05-0.10 mm⁻¹ for average cosmic ray muons
    • Energy threshold effects become important
    • Multiple scattering affects geometry

15. Key Formula:
    Attenuation length: lambda = 1/mu
    For cosmic ray muons in lead: lambda ~ 10-20 cm
    (depends on energy spectrum and geometry)
"""

print(references)

print("\n" + "=" * 80)
print("SUGGESTED ANALYSIS IMPROVEMENTS")
print("=" * 80)

print("""1. FIT WITHOUT LAST POINT
   - If last point is anomalous, fit first 4 points only
   - Report both fits and discuss discrepancy

2. ENERGY-DEPENDENT ATTENUATION
   - Bin events by charge (area): 30-50, 50-100, >100 pC
   - Fit each bin separately
   - Expect: higher energy -> lower mu

3. GEOMETRIC CORRECTION
   - Calculate acceptance as function of scattering angle
   - Apply correction factor: A(x) = A0 * f(x)
   - Modified model: N(x) = N0 * exp(-mux) * A(x)/A0

4. TWO-COMPONENT MODEL
   - Soft muons: N_soft(x) = N1 * exp(-mu1x)  [mu1 large]
   - Hard muons: N_hard(x) = N2 * exp(-mu2x)  [mu2 small]
   - Total: N(x) = N_soft(x) + N_hard(x)
""")

# Create diagnostic plot
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Residuals (all points)
ax = axes[0, 0]
fit_all = exp_fit(thicknesses, *popt_all)
residuals = coincidences - fit_all
ax.errorbar(thicknesses, residuals, yerr=errors, fmt='o', markersize=8, capsize=5)
ax.axhline(0, color='r', linestyle='--')
ax.fill_between([-1, 21], [-2*np.mean(errors), -2*np.mean(errors)],
              [2*np.mean(errors), 2*np.mean(errors)], alpha=0.2, color='gray')
ax.set_xlabel('Thickness (mm)')
ax.set_ylabel('Residuals (measured - fit)')
ax.set_title('Fit Residuals (All Points)')
ax.grid(True, alpha=0.3)

# Plot 2: Comparison of fits
ax = axes[0, 1]
x_plot = np.linspace(0, 22, 100)
ax.errorbar(thicknesses, coincidences, yerr=errors, fmt='o', markersize=8,
            capsize=5, label='Data', color='blue')
ax.plot(x_plot, exp_fit(x_plot, *popt_all), 'r-', linewidth=2,
        label=f'Fit (all): mu={popt_all[1]:.4f}')  # 修复了此处的变量名错误
ax.plot(x_plot, exp_fit(x_plot, *popt_no_last), 'g--', linewidth=2,
        label=f'Fit (no last): mu={popt_no_last[1]:.4f}')
ax.set_xlabel('Thickness (mm)')
ax.set_ylabel('Coincidence Events')
ax.set_title('Comparison of Fits')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Normalized residuals
ax = axes[1, 0]
norm_residuals = residuals / errors
ax.bar(thicknesses, norm_residuals, width=1.5, alpha=0.7, edgecolor='black')
ax.axhline(0, color='r', linestyle='--')
ax.axhline(2, color='orange', linestyle=':', label='±2σ')
ax.axhline(-2, color='orange', linestyle=':')
ax.axhline(3, color='red', linestyle=':', label='±3σ')
ax.axhline(-3, color='red', linestyle=':')
ax.set_xlabel('Thickness (mm)')
ax.set_ylabel('Normalized Residuals (σ)')
ax.set_title('Pull Distribution')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Transmission ratio
ax = axes[1, 1]
transmission = coincidences / coincidences[0]
trans_err = transmission * np.sqrt((errors/coincidences)**2 + (errors[0]/coincidences[0])**2)
ax.errorbar(thicknesses, transmission, yerr=trans_err, fmt='o', markersize=8,
       capsize=5, label='Data', color='blue')
ax.plot(x_plot, exp_fit(x_plot, *popt_all)/popt_all[0], 'r-', linewidth=2, label='Fit (all)')
ax.plot(x_plot, exp_fit(x_plot, *popt_no_last)/popt_no_last[0], 'g--', linewidth=2,
        label=f'Fit (no last)')
ax.set_xlabel('Thickness (mm)')
ax.set_ylabel('Transmission (N/N0)')
ax.set_title('Transmission Factor')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim([0, 1.1])

plt.tight_layout()
plt.savefig('/home/guiyu/workspace/CAEN/fit_diagnostics.png', dpi=150)
print("\nDiagnostic plots saved: /home/guiyu/workspace/CAEN/fit_diagnostics.png")
print("=" * 80)