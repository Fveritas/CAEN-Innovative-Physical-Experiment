#!/usr/bin/env python3
"""
Diagnostic v3: Log-log differential spectrum. 
Gain shift → curve shifts LEFT; Geometry loss → curve shifts DOWN.
"""
import uproot
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

FILES = {
    (0, 'last'):  '/home/guiyu/workspace/CAEN/data/5181.root',
    (10, 'last'): '/home/guiyu/workspace/CAEN/data/5182.root',
    (20, 'last'): '/home/guiyu/workspace/CAEN/data/5183.root',
    (30, 'last'): '/home/guiyu/workspace/CAEN/data/5184.root',
    (40, 'this'): '/home/guiyu/workspace/CAEN/data/5185.root',
    (50, 'this'): '/home/guiyu/workspace/CAEN/data/5186.root',
}

def load_areas(fp):
    with uproot.open(fp) as f:
        t = f['t1;1']
        return t['area'].array(library='np'), t['area2'].array(library='np')

def main():
    # Use only 0-plate (no lead) as baseline to avoid absorption confusion
    a1_0, a2_0 = load_areas(FILES[(0, 'last')])

    # This week: use only 40-plate data, but also check 50
    a1_40, a2_40 = load_areas(FILES[(40, 'this')])
    a1_50, a2_50 = load_areas(FILES[(50, 'this')])

    # Focus: lower detector area > 0 (positive pulses only, exclude baseline noise)
    down_last = a2_0[a2_0 > 0]
    down_this_40 = a2_40[a2_40 > 0]
    down_this_50 = a2_50[a2_50 > 0]

    # Also check upper detector for comparison
    up_last = a1_0[a1_0 > 0]
    up_this_40 = a1_40[a1_40 > 0]

    print("=" * 80)
    print("Log-log differential area spectrum analysis")
    print("Comparing 0-plate data (last week, no lead) vs 40/50-plate (this week)")
    print("=" * 80)

    # ====== Build log-log differential spectra ======
    bins = np.logspace(np.log10(1.5), np.log10(400), 80)

    for label, data_last, data_this, detector in [
        ("Upper (control)", up_last, up_this_40, "Upper"),
        ("Lower (problem)", down_last, down_this_40, "Lower"),
    ]:
        h_last, _ = np.histogram(data_last, bins=bins)
        h_this, _ = np.histogram(data_this, bins=bins)
        bin_centers = np.sqrt(bins[:-1] * bins[1:])
        bin_widths = np.diff(bins)

        # Density (per unit area)
        d_last = h_last / bin_widths / len(data_last)
        d_this = h_this / bin_widths / len(data_this)

        # Remove zero bins
        mask = (h_last > 0) & (h_this > 0)
        bc = bin_centers[mask]
        dl = d_last[mask]
        dt = d_this[mask]
        ratio = dt / dl

        print(f"\n--- {detector} detector: log-log spectrum ---")
        print(f"  Last week (0pl): {len(data_last)} pulses > 0")
        print(f"  This week (40pl): {len(data_this)} pulses > 0")
        print(f"  Pulse count ratio (this/last): {len(data_this)/len(data_last):.3f}")
        print(f"  Mean ratio (this/last) across bins: {np.mean(ratio):.3f}")
        print(f"  Log10 ratio std across bins: {np.log10(np.std(ratio) + 1e-10):.2f}")
        
        # Fit power law to both spectra
        # dN/dA = k * A^(-alpha)
        # log(dN/dA) = log(k) - alpha * log(A)
        def power_law(x, logk, alpha):
            return logk - alpha * x

        x_last = np.log10(bc)
        y_last = np.log10(dl)
        x_this = np.log10(bc)
        y_this = np.log10(dt)

        # Fit
        popt_last, _ = curve_fit(power_law, x_last, y_last)
        popt_this, _ = curve_fit(power_law, x_this, y_this)

        alpha_last = popt_last[1]
        alpha_this = popt_this[1]
        logk_last = popt_last[0]
        logk_this = popt_this[0]

        print(f"  Power law index: last={alpha_last:.2f}, this={alpha_this:.2f}")
        print(f"  Normalization log10(k): last={logk_last:.2f}, this={logk_this:.2f}")
        
        # If gain shift: same index, different normalization (shift left)
        # Normalization difference: logk_this - logk_last ≈ -alpha * log10(g)
        delta_logk = logk_this - logk_last
        if abs(alpha_last - alpha_this) < 0.3 and delta_logk < -0.05:
            # Consistent with gain shift
            # delta_logk = -alpha * log10(g)
            # log10(g) = -delta_logk / alpha
            log10_g = -delta_logk / ((alpha_last + alpha_this) / 2)
            g = 10 ** log10_g
            print(f"  >>> GAIN SHIFT detected: g = {g:.3f} ({g*100:.0f}% of original)")
            print(f"      This would explain a {g**((alpha_last+alpha_this)/2-1)*100:.0f}% count rate at threshold")
        elif abs(delta_logk) < 0.05:
            print(f"  >>> Same amplitude, different count → GEOMETRY issue")
        else:
            print(f"  >>> Mixed effect or shape change")

    # ====== PLOT ======
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Log-Log Differential Area Spectrum: 0 plates (last) vs 40 plates (this)',
                 fontsize=14, fontweight='bold')

    # Plot 1: Upper detector log-log
    ax = axes[0, 0]
    for data, color, alpha, label in [(up_last, 'royalblue', 0.6, 'Last week (0pl)'),
                                        (up_this_40, 'crimson', 0.6, 'This week (40pl)')]:
        h, _ = np.histogram(data, bins=bins)
        bc = np.sqrt(bins[:-1] * bins[1:])
        dw = np.diff(bins)
        d = h / dw / len(data)
        mask = h > 0
        ax.loglog(bc[mask], d[mask], 'o-', color=color, alpha=alpha, linewidth=1.5, 
                  markersize=4, label=label)
    ax.set_xlabel('Area')
    ax.set_ylabel('dN/dA (normalized)')
    ax.set_title('Upper Detector (control group)', fontsize=12)
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=9)

    # Plot 2: Lower detector log-log
    ax = axes[0, 1]
    for data, color, alpha, label in [(down_last, 'royalblue', 0.6, 'Last week (0pl)'),
                                        (down_this_40, 'crimson', 0.6, 'This week (40pl)'),
                                        (down_this_50, 'darkorange', 0.4, 'This week (50pl)')]:
        h, _ = np.histogram(data, bins=bins)
        bc = np.sqrt(bins[:-1] * bins[1:])
        dw = np.diff(bins)
        d = h / dw / len(data)
        mask = h > 0
        ax.loglog(bc[mask], d[mask], 'o-', color=color, alpha=alpha, linewidth=1.5,
                  markersize=4, label=label)
    ax.set_xlabel('Area')
    ax.set_ylabel('dN/dA (normalized)')
    ax.set_title('Lower Detector (problem)', fontsize=12)
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(fontsize=9)

    # Plot 3: Ratio (this/last) vs area — CONSTANT if geometry, SLOPING if gain
    ax = axes[1, 0]
    for data_l, data_t, color, label in [(up_last, up_this_40, 'royalblue', 'Upper (control)'),
                                           (down_last, down_this_40, 'crimson', 'Lower (problem)')]:
        h_l, _ = np.histogram(data_l, bins=bins)
        h_t, _ = np.histogram(data_t, bins=bins)
        bc = np.sqrt(bins[:-1] * bins[1:])
        # Cumulative: N(>x)
        cum_l = np.cumsum(h_l[::-1])[::-1] / len(data_l)
        cum_t = np.cumsum(h_t[::-1])[::-1] / len(data_t)
        mask = cum_l > 5e-4  # Avoid noise at high end
        ratio = cum_t[mask] / cum_l[mask]
        ax.semilogx(bc[mask], ratio, 'o-', color=color, linewidth=2, markersize=4, label=label)
    ax.axhline(y=np.mean(cum_t[cum_l > 5e-4] / cum_l[cum_l > 5e-4]),
               color='gray', linestyle='--', alpha=0.5, label='Mean ratio')
    ax.set_xlabel('Area threshold')
    ax.set_ylabel('Ratio = N_this(>A) / N_last(>A)')
    ax.set_title('Cumulative Ratio vs Threshold\n(constant→geometry  |  sloping→gain shift)', fontsize=12)
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.5)

    # Plot 4: Pulse area overlay (linear scale), normalized
    ax = axes[1, 1]
    bins_linear = np.linspace(0, 300, 101)
    for data, color, alpha, ls, label in [
        (down_last, 'royalblue', 0.6, '-', 'Last week (0pl)'),
        (down_this_40, 'crimson', 0.6, '-', 'This week (40pl)'),
    ]:
        h, edges = np.histogram(data, bins=bins_linear)
        bc = (edges[:-1] + edges[1:]) / 2
        ax.stairs(h / max(h), edges, fill=False, color=color, linewidth=1.5, label=label, alpha=alpha)
    ax.axvline(30, color='black', linestyle='--', alpha=0.4, linewidth=1)
    ax.set_xlabel('Area')
    ax.set_ylabel('Normalized counts')
    ax.set_title('Lower Detector: Full Spectrum (0pl vs 40pl)\nNormalized to peak', fontsize=12)
    ax.legend(fontsize=9)
    ax.set_xlim(0, 200)

    fig.tight_layout()
    plt.savefig('/home/guiyu/workspace/CAEN/data/diagnostic_v3.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: /home/guiyu/workspace/CAEN/data/diagnostic_v3.png")
    plt.show()

if __name__ == '__main__':
    main()
