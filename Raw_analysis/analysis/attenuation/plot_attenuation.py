#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Data from measurements
data = [
  {'plates': 0,  'thickness_mm': 0.0,  'coincidence': 3357},
    {'plates': 10, 'thickness_mm': 5.0,  'coincidence': 3136},
    {'plates': 20, 'thickness_mm': 10.0, 'coincidence': 3119},
    {'plates': 30, 'thickness_mm': 15.0, 'coincidence': 3046},
    {'plates': 40, 'thickness_mm': 20.0, 'coincidence': 1523},
]

print("=" * 80)
print("COSMIC RAY ATTENUATION BY LEAD SHIELDING")
print("=" * 80)
print("\nLead plate: 0.5 mm thickness per plate")
print("Threshold: area > 30, area2 > 30\n")

# Extract arrays
thicknesses = np.array([d['thickness_mm'] for d in data])
coincidences = np.array([d['coincidence'] for d in data])
errors = np.sqrt(coincidences)  # Poisson statistics

# Print table
print(f"{'Plates':<10} {'Thickness':<15} {'Coincidence':<15} {'Relative'}")
print(f"{'':10} {'(mm)':<15} {'Events':<15} {'to N₀'}")
print("-" * 60)
for d in data:
    rel = d['coincidence'] / data[0]['coincidence']
    print(f"{d['plates']:<10} {d['thickness_mm']:<15.1f} {d['coincidence']:<15} {rel:.4f}")

# Exponential fit: N(x) = N0 * exp(-mu * x)
def exp_atten(x, N0, mu):
    return N0 * np.exp(-mu * x)

popt, pcov = curve_fit(exp_atten, thicknesses, coincidences,
              p0=[3357, 0.05], sigma=errors)

N0, mu = popt
N0_err, mu_err = np.sqrt(np.diag(pcov))

print("\n" + "=" * 80)
print("EXPONENTIAL FIT: N(x) = N₀ × exp(-μx)")
print("=" * 80)
print(f"N₀ = {N0:.1f} ± {N0_err:.1f} events")
print(f"μ  = {mu:.4f} ± {mu_err:.4f} mm⁻¹")
print(f"μ  = {mu*10:.4f} ± {mu_err*10:.4f} cm⁻¹")

hvl = np.log(2) / mu
hvl_err = hvl * (mu_err / mu)
print(f"\nHalf-Value Layer (HVL) = {hvl:.2f} ± {hvl_err:.2f} mm")
print(f"(Thickness to reduce intensity by 50%)")

# R-squared
residuals = coincidences - exp_atten(thicknesses, *popt)
ss_res = np.sum(residuals**2)
ss_tot = np.sum((coincidences - np.mean(coincidences))**2)
r_squared = 1 - (ss_res / ss_tot)
print(f"\nR² = {r_squared:.4f}")

# Theoretical comparison
mu_theory = 0.077  # mm^-1 for cosmic ray muons in lead (approximate)
print(f"\nTheoretical μ (muons in lead): ~{mu_theory:.4f} mm⁻¹")
print(f"Measured / Theory ratio: {mu/mu_theory:.2f}")

# Create plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Linear scale
x_fit = np.linspace(0, 22, 100)
y_fit = exp_atten(x_fit, *popt)

ax1.errorbar(thicknesses, coincidences, yerr=errors, fmt='o',
             markersize=10, capsize=5, label='Measured', color='blue', linewidth=2)
ax1.plot(x_fit, y_fit, 'r-', linewidth=2,
         label=f'Fit: N₀={N0:.0f}, μ={mu:.4f} mm⁻¹')
ax1.set_xlabel('Lead Thickness (mm)', fontsize=13, fontweight='bold')
ax1.set_ylabel('Coincidence Events', fontsize=13, fontweight='bold')
ax1.set_title('Cosmic Ray Attenuation', fontsize=15, fontweight='bold')
ax1.legend(fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.tick_params(labelsize=11)

# Plot 2: Transmission factor
transmission = coincidences / coincidences[0]
trans_err = transmission * np.sqrt((errors/coincidences)**2 + (errors[0]/coincidences[0])**2)
y_fit_trans = exp_atten(x_fit, *popt) / N0

ax2.errorbar(thicknesses, transmission, yerr=trans_err, fmt='o',
             markersize=10, capsize=5, label='Measured', color='blue', linewidth=2)
ax2.plot(x_fit, y_fit_trans, 'r-', linewidth=2,
         label=f'Fit: exp(-{mu:.4f}x)')
ax2.axhline(y=0.5, color='green', linestyle='--', alpha=0.7, linewidth=2, label='50%')
ax2.axvline(x=hvl, color='green', linestyle='--', alpha=0.7, linewidth=2)
ax2.text(hvl+0.5, 0.55, f'HVL={hvl:.1f}mm', fontsize=11, color='green', fontweight='bold')
ax2.set_xlabel('Lead Thickness (mm)', fontsize=13, fontweight='bold')
ax2.set_ylabel('Transmission (N/N₀)', fontsize=13, fontweight='bold')
ax2.set_title('Transmission Factor', fontsize=15, fontweight='bold')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_ylim([0, 1.1])
ax2.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig('/home/guiyu/workspace/CAEN/lead_attenuation.png', dpi=150, bbox_inches='tight')
print(f"\n{'='*80}")
print("Plot saved: /home/guiyu/workspace/CAEN/lead_attenuation.png")
print("=" * 80)
