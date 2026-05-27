#!/usr/bin/env python3
"""
Analysis: Why didn't we observe the Rossi Transition Curve?
"""

import numpy as np
import matplotlib.pyplot as plt

print("=" * 80)
print("WHY NO ROSSI TRANSITION CURVE IN YOUR EXPERIMENT?")
print("=" * 80)

print("""
WHAT IS THE ROSSI TRANSITION CURVE?
---------------------------
The Rossi Transition Curve shows cosmic ray intensity vs absorber thickness.
It has THREE distinct regions:

1. SOFT COMPONENT (electrons/positrons, low-energy muons)
   - Rapid decrease at small thickness (0-10 cm Pb)
   - Exponential attenuation
   - Absorbed by electromagnetic interactions

2. TRANSITION REGION (10-15 cm Pb)
   - Intensity reaches MINIMUM
   - Soft component absorbed
   - Hard component (high-energy muons) dominates

3. HARD COMPONENT (high-energy muons)
   - Slow increase after minimum!
   - Due to pion/kaon decay in atmosphere
   - More muons produced at depth

The KEY feature: intensity DECREASES then INCREASES (or flattens)
""")

print("=" * 80)
print("YOUR EXPERIMENTAL SETUP")
print("=" * 80)

print("""
Your configuration:
- Two scintillator detectors in COINCIDENCE
- Vertical separation: 16 cm
- Lead absorber BETWEEN detectors
- Threshold: area > 30 pC (relatively high energy)

Your data:
  0 mm:  3357 events (baseline)
  5 mm:  3136 events (93.4%)
  10 mm: 3119 events (92.9%)
  15 mm: 3046 events (90.7%)
  20 mm: 1523 events (45.4%)  <- anomalous drop
""")

print("\n" + "=" * 80)
print("WHY YOU DIDN'T SEE THE ROSSI CURVE")
print("=" * 80)

print("""
REASON 1: ABSORBER PLACEMENT
----------------------
Classic Rossi experiment:
  [Atmosphere with absorber at TOP]
       ↓
  [Detector telescope at BOTTOM]

Your setup:
  [Upper detector]
     ↓
  [Lead absorber HERE]  <- BETWEEN detectors
       ↓
  [Lower detector]

CRITICAL DIFFERENCE:
- Rossi: Absorber affects PRODUCTION of secondary particles in atmosphere
- Yours: Absorber only affects TRANSMISSION through lead
- You CANNOT see pion/kaon decay effects (they happen in atmosphere, not lead)

REASON 2: THICKNESS RANGE TOO SMALL
----------------------
Rossi transition occurs at: 10-15 cm lead equivalent
Your maximum thickness: 2.0 cm (20 mm)

You are in the "SOFT COMPONENT" region only!
- Not thick enough to reach transition
- Not thick enough to see hard component rise

REASON 3: COINCIDENCE REQUIREMENT
----------------------------------
Your coincidence setup preferentially selects:
- Nearly vertical muons (small angles)
- Particles that DON'T scatter much
- High-energy particles (threshold = 30 pC)

This FILTERS OUT the soft component that creates the Rossi curve!

Classic Rossi: Single detector (sees all particles)
Your setup: Coincidence (sees only straight-through particles)

REASON 4: ENERGY THRESHOLD
--------------------
Your threshold (area > 30 pC) corresponds to relatively high energy.
This means you're already selecting the "hard component"!

Soft component (electrons, low-energy muons): ALREADY FILTERED by threshold
Hard component (high-energy muons): What you're measuring

Result: You see only gradual attenuation, no transition.

REASON 5: NO ATMOSPHERIC PRODUCTION
------------------------------------
The Rossi curve's INCREASE comes from:
- Pions/kaons produced in atmosphere above absorber
- They decay to muons BELOW the absorber
- More absorber → more production → more muons

Your lead is NOT in the atmosphere!
- No pion/kaon production in 2 cm of lead
- Only absorption, no production
- Can only decrease, never increase
""")

print("\n" + "=" * 80)
print("WHAT YOU'RE ACTUALLY MEASURING")
print("=" * 80)

print("""
Your experiment measures:
1. HIGH-ENERGY MUON ATTENUATION in thin lead
2. GEOMETRIC ACCEPTANCE effects (scattering)
3. ENERGY THRESHOLD effects

This is DIFFERENT from Rossi's experiment, which measured:
1. TOTAL cosmic ray intensity (all particles)
2. ATMOSPHERIC PRODUCTION effects
3. SOFT vs HARD component separation

Your result (gradual decrease) is CORRECT for your setup!
It's not a Rossi curve - it's a muon transmission curve.
""")

print("\n" + "=" * 80)
print("HOW TO OBSERVE THE ROSSI TRANSITION CURVE")
print("=" * 80)

print("""
To see the Rossi curve, you would need:

1. SINGLE DETECTOR (not coincidence)
   - Measures total intensity
   - Includes soft component

2. ABSORBER ABOVE DETECTOR
   - Place lead on TOP of detector
   - Allows atmospheric production effects

3. LARGER THICKNESS RANGE
   - Need 0-20 cm lead (not 0-2 cm)
   - Must reach transition region

4. LOWER ENERGY THRESHOLD
   - Include soft component (electrons)
   - See the rapid initial decrease

5. DIFFERENT GEOMETRY
   - Large solid angle
   - Accept scattered particles

ALTERNATIVE: Measure at different ALTITUDES
- Go to mountain (high altitude) vs sea level
- See intensity change with atmospheric depth
- This is closer to original Rossi experiment
""")

print("\n" + "=" * 80)
print("COMPARISON: ROSSI vs YOUR EXPERIMENT")
print("=" * 80)

# Create comparison plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Rossi curve (idealized)
thickness_rossi = np.linspace(0, 20, 100)  # cm
# Soft component: exponential decay
soft = 100 * np.exp(-0.5 * thickness_rossi)
# Hard component: slight increase due to production
hard = 30 * (1 + 0.02 * thickness_rossi)
# Total
total_rossi = soft + hard

ax1.plot(thickness_rossi, soft, 'b--', linewidth=2, label='Soft component (e±)')
ax1.plot(thickness_rossi, hard, 'r--', linewidth=2, label='Hard component (μ)')
ax1.plot(thickness_rossi, total_rossi, 'k-', linewidth=3, label='Total (Rossi curve)')
ax1.axvline(10, color='green', linestyle=':', linewidth=2, label='Transition (~10 cm)')
ax1.set_xlabel('Lead Thickness (cm)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Relative Intensity', fontsize=12, fontweight='bold')
ax1.set_title('Classic Rossi Transition Curve', fontsize=14, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 20])

# Your data
thickness_yours = np.array([0, 0.5, 1.0, 1.5, 2.0])  # cm
counts_yours = np.array([3357, 3136, 3119, 3046, 1523])
counts_normalized = counts_yours / counts_yours[0] * 100

ax2.plot(thickness_yours, counts_normalized, 'o-', markersize=12, linewidth=3,
         color='blue', label='Your data')
# Fit first 4 points
from scipy.optimize import curve_fit
def exp_decay(x, N0, mu):
    return N0 * np.exp(-mu * x)
popt, _ = curve_fit(exp_decay, thickness_yours[:-1], counts_normalized[:-1])
x_fit = np.linspace(0, 2, 100)
ax2.plot(x_fit, exp_decay(x_fit, *popt), 'r--', linewidth=2,
         label=f'Exponential fit (first 4 points)')
ax2.set_xlabel('Lead Thickness (cm)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Relative Intensity (%)', fontsize=12, fontweight='bold')
ax2.set_title('Your Experiment: Muon Transmission', fontsize=14, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 2])

# Add annotations
ax1.annotate('Minimum\n(transition)', xy=(10, 35), xytext=(12, 50),
        arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=11, color='green', fontweight='bold')
ax1.annotate('Soft component\ndominates', xy=(2, 80), xytext=(4, 90),
            fontsize=10, color='blue')
ax1.annotate('Hard component\ndominates', xy=(16, 60), xytext=(14, 75),
          fontsize=10, color='red')

ax2.annotate('Only in soft\ncomponent region', xy=(1, 92), xytext=(0.5, 80),
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
         fontsize=11, color='red', fontweight='bold')
ax2.annotate('Anomalous\npoint?', xy=(2, 45), xytext=(1.2, 55),
            arrowprops=dict(arrowstyle='->', color='orange', lw=2),
            fontsize=10, color='orange', fontweight='bold')

plt.tight_layout()
plt.savefig('/home/guiyu/workspace/CAEN/rossi_comparison.png', dpi=150, bbox_inches='tight')
print("\nComparison plot saved: /home/guiyu/workspace/CAEN/rossi_comparison.png")

print("\n" + "=" * 80)
print("REFERENCES FOR ROSSI TRANSITION CURVE")
print("=" * 80)

print("""
1. Rossi, B. (1948)
   "Interpretation of Cosmic-Ray Phenomena"
   Reviews of Modern Physics, 20(3), 537-583
   - Original paper describing the transition curve

2. Rossi, B. & Greisen, K. (1941)
   "Cosmic-Ray Theory"
   Reviews of Modern Physics, 13(4), 240-309
   - Theoretical foundation

3. Grieder, P.K.F. "Cosmic Rays at Earth" (2001)
   Chapter 6: Atmospheric Effects
   - Modern treatment of Rossi curve

4. Gaisser, T.K. "Cosmic Rays and Particle Physics" (2016)
   Chapter 2: Cosmic Ray Interactions
   - Production and attenuation mechanisms

5. Educational experiments:
   - "The Rossi Transition Curve" - CERN HST2002
   - Various university cosmic ray lab manuals

KEY PHYSICS:
- Soft component: e+/e- from electromagnetic cascades
- Hard component: μ from π/K decay
- Transition: ~100 g/cm² (≈10 cm Pb, ≈1 m concrete)
- Production: π/K created in atmosphere, decay to μ
""")
print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

print("""
Your experiment is NOT designed to see the Rossi transition curve because:

1. Absorber is BETWEEN detectors (not above)
2. Thickness too small (2 cm vs 20 cm needed)
3. Coincidence setup filters soft component
4. High energy threshold excludes soft component
5. No atmospheric production in thin lead

What you measured is CORRECT for your setup:
→ High-energy muon transmission through thin lead
→ Gradual attenuation (no transition)
→ Geometric/scattering effects at 20mm

This is still valuable physics! You're measuring:
- Muon attenuation coefficient
- Energy-dependent transmission
- Detector efficiency vs absorber

To see Rossi curve: Need different experimental design
(single detector, thick absorber above, low threshold)
""")

print("=" * 80)
