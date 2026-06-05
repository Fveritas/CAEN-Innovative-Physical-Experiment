#!/usr/bin/env python3
"""
Diagnostic v4: 2D correlation between upper and lower detector area.
Gain shift → correlation shifts (same pattern, smaller lower values).
Geometry loss → "ghost" cluster at low lower area (upper fires, lower misses).
"""
import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

FILES = {
    (0, 'last'):  '/home/guiyu/workspace/CAEN/data/5181.root',
    (10, 'last'): '/home/guiyu/workspace/CAEN/data/5182.root',
    (20, 'last'): '/home/guiyu/workspace/CAEN/data/5183.root',
    (30, 'last'): '/home/guiyu/workspace/CAEN/data/5184.root',
    (40, 'this'): '/home/guiyu/workspace/CAEN/data/5185.root',
    (50, 'this'): '/home/guiyu/workspace/CAEN/data/5186.root',
}

def load(fp):
    with uproot.open(fp) as f:
        t = f['t1;1']
        return t['area'].array(library='np'), t['area2'].array(library='np')

def main():
    # Load data
    up_last_all = []
    down_last_all = []
    for n in [0, 10, 20, 30]:
        a1, a2 = load(FILES[(n, 'last')])
        up_last_all.append(a1)
        down_last_all.append(a2)
    up_last = np.concatenate(up_last_all)
    down_last = np.concatenate(down_last_all)

    up_this_all = []
    down_this_all = []
    for n in [40, 50]:
        a1, a2 = load(FILES[(n, 'this')])
        up_this_all.append(a1)
        down_this_all.append(a2)
    up_this = np.concatenate(up_this_all)
    down_this = np.concatenate(down_this_all)

    # Also compare 0pl only (clean baseline)
    up_0, down_0 = load(FILES[(0, 'last')])
    up_40, down_40 = load(FILES[(40, 'this')])

    # Clip extreme outliers
    mask_l = (up_last > -100) & (up_last < 500) & (down_last > -100) & (down_last < 500)
    mask_t = (up_this > -100) & (up_this < 500) & (down_this > -100) & (down_this < 500)
    mask_0 = (up_0 > -100) & (up_0 < 500) & (down_0 > -100) & (down_0 < 500)
    mask_40 = (up_40 > -100) & (up_40 < 500) & (down_40 > -100) & (down_40 < 500)

    ul = up_last[mask_l]
    dl = down_last[mask_l]
    ut = up_this[mask_t]
    dt = down_this[mask_t]
    u0 = up_0[mask_0]
    d0 = down_0[mask_0]
    u40 = up_40[mask_40]
    d40 = down_40[mask_40]

    # Subsample for faster plotting
    n_sample = min(30000, len(ul))
    idx_l = np.random.choice(len(ul), n_sample, replace=False)
    idx_t = np.random.choice(len(ut), min(n_sample, len(ut)), replace=False)

    # ====== ANALYSIS ======
    print("=" * 90)
    print("2D Correlation Analysis: Upper vs Lower Detector Area")
    print("=" * 90)

    # Categorize events by lower detector response
    for label, up_arr, down_arr in [
        ("0 plates (last)", u0, d0),
        ("40 plates (this)", u40, d40),
    ]:
        total = len(up_arr)
        up_ok = up_arr > 30
        down_ok = down_arr > 30
        up_low = (up_arr > 10) & (up_arr <= 30)
        down_low = (down_arr > 10) & (down_arr <= 30)
        up_null = (up_arr >= -5) & (up_arr <= 10)
        down_null = (down_arr >= -5) & (down_arr <= 10)

        print(f"\n--- {label} (n={total}) ---")
        print(f"  Up>30, Down>30 (coincidence):  {np.sum(up_ok & down_ok):>6} ({np.sum(up_ok & down_ok)/np.sum(up_ok)*100:.1f}% of Up>30)")
        print(f"  Up>30, Down low(10-30):        {np.sum(up_ok & down_low):>6}")
        print(f"  Up>30, Down null(-5 to 10):     {np.sum(up_ok & down_null):>6} ({np.sum(up_ok & down_null)/np.sum(up_ok)*100:.1f}% of Up>30)")
        print(f"  Up null, Down>30:               {np.sum(up_null & down_ok):>6}")
        print(f"  Up>30 total:                    {np.sum(up_ok):>6}")
        print(f"  Down>30 total:                  {np.sum(down_ok):>6}")

        # Conditional probability
        p_down_given_up = np.sum(up_ok & down_ok) / np.sum(up_ok) if np.sum(up_ok) > 0 else 0
        print(f"  P(Down>30 | Up>30): {p_down_given_up:.3f}")

    # ====== DIAGNOSIS ======
    print(f"\n{'='*60}")
    print("DIAGNOSIS")
    # 0 plates comparison
    frac_coin_0 = np.sum((u0>30)&(d0>30)) / np.sum(u0>30)
    frac_down_null_when_up_ok_0 = np.sum((u0>30)&(d0>=-5)&(d0<=10)) / np.sum(u0>30)

    frac_coin_40 = np.sum((u40>30)&(d40>30)) / np.sum(u40>30)
    frac_down_null_when_up_ok_40 = np.sum((u40>30)&(d40>=-5)&(d40<=10)) / np.sum(u40>30)

    print(f"P(Down>30 | Up>30): last=0pl={frac_coin_0:.3f}, this=40pl={frac_coin_40:.3f}")
    print(f"P(Down null | Up>30): last=0pl={frac_down_null_when_up_ok_0:.3f}, this=40pl={frac_down_null_when_up_ok_40:.3f}")

    delta_null = frac_down_null_when_up_ok_40 - frac_down_null_when_up_ok_0

    if delta_null > 0.1:
        print(f"\n>>> CRITICAL: When Up>30, Down has near-zero area significantly MORE often")
        print(f"    this week (40pl) than last week (0pl): {delta_null*100:.1f}% increase.")
        print(f"    This means many events that triggered the upper detector had")
        print(f"    essentially NO signal in the lower detector.")
        print(f"    >>> Primary cause: GEOMETRY MISALIGNMENT or partial blockage.")
        print(f"    Particles pass through upper detector but MISS the lower one entirely.")
    else:
        # Check if correlation still exists but shifted
        up_ok_l = u0 > 30
        up_ok_t = u40 > 30
        down_when_up_l = d0[up_ok_l]
        down_when_up_t = d40[up_ok_t]
        med_l = np.median(down_when_up_l)
        med_t = np.median(down_when_up_t)
        print(f"\nMedian Down area when Up>30: last=0pl={med_l:.1f}, this=40pl={med_t:.1f}")
        if med_t < med_l * 0.7:
            print(f"    >>> Down area significantly reduced when Up fires.")
            print(f"    >>> Primary cause: GAIN/HV drift on lower detector.")
        else:
            print(f"    >>> Both effects present or inconclusive.")

    # ====== PLOTS ======
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('2D Correlation: Upper vs Lower Detector Area', fontsize=14, fontweight='bold')

    # Plot 1: 0 plates last week
    ax = axes[0, 0]
    h = ax.hist2d(u0[idx_l if len(idx_l) < len(u0) else np.arange(len(u0))],
                  d0[idx_l if len(idx_l) < len(d0) else np.arange(len(d0))],
                  bins=[100, 100], range=[[-20, 300], [-20, 300]],
                  cmap='Blues', norm=LogNorm())
    ax.plot([30, 30], [0, 300], 'r--', alpha=0.5, linewidth=0.8)
    ax.plot([0, 300], [30, 30], 'r--', alpha=0.5, linewidth=0.8)
    ax.set_xlabel('Upper detector area', fontsize=10)
    ax.set_ylabel('Lower detector area', fontsize=10)
    ax.set_title(f'0 plates (last week)\nn={len(u0)}', fontsize=11)
    plt.colorbar(h[3], ax=ax, label='counts')

    # Plot 2: 40 plates this week
    ax = axes[0, 1]
    h = ax.hist2d(u40, d40, bins=[100, 100], range=[[-20, 300], [-20, 300]],
                  cmap='Reds', norm=LogNorm())
    ax.plot([30, 30], [0, 300], 'r--', alpha=0.5, linewidth=0.8)
    ax.plot([0, 300], [30, 30], 'r--', alpha=0.5, linewidth=0.8)
    ax.set_xlabel('Upper detector area', fontsize=10)
    ax.set_ylabel('Lower detector area', fontsize=10)
    ax.set_title(f'40 plates (this week)\nn={len(u40)}', fontsize=11)
    plt.colorbar(h[3], ax=ax, label='counts')

    # Plot 3: Difference (this - last), normalized
    ax = axes[0, 2]
    hrange = [[-20, 300], [-20, 300]]
    h_last, xe, ye = np.histogram2d(u0, d0, bins=[60, 60], range=hrange)
    h_this, _, _ = np.histogram2d(u40, d40, bins=[60, 60], range=hrange)
    # Normalize by total entries before subtracting
    diff = h_this / len(u40) - h_last / len(u0)
    extent = [xe[0], xe[-1], ye[0], ye[-1]]
    im = ax.imshow(diff.T, origin='lower', extent=extent, aspect='auto',
                   cmap='RdBu_r', vmin=-np.max(np.abs(diff))/2, vmax=np.max(np.abs(diff))/2)
    ax.plot([30, 30], [-20, 300], 'k--', alpha=0.5, linewidth=0.8)
    ax.plot([-20, 300], [30, 30], 'k--', alpha=0.5, linewidth=0.8)
    ax.set_xlabel('Upper detector area', fontsize=10)
    ax.set_ylabel('Lower detector area', fontsize=10)
    ax.set_title('Difference (this - last, normalized)\nBlue=less this week, Red=more this week', fontsize=11)
    plt.colorbar(im, ax=ax, label='Δ(density)')

    # Plot 4: Profile: mean lower area vs upper area bins
    ax = axes[1, 0]
    bins_up = np.linspace(0, 300, 31)
    for (u, d, color, label) in [(u0, d0, 'royalblue', '0pl last week'),
                                   (u40, d40, 'crimson', '40pl this week')]:
        means = []
        stds = []
        centers = []
        for i in range(len(bins_up) - 1):
            mask = (u >= bins_up[i]) & (u < bins_up[i+1])
            if np.sum(mask) > 10:
                means.append(np.mean(d[mask]))
                stds.append(np.std(d[mask]))
                centers.append((bins_up[i] + bins_up[i+1]) / 2)
        centers = np.array(centers)
        means = np.array(means)
        stds = np.array(stds)
        ax.plot(centers, means, 'o-', color=color, linewidth=2, markersize=4, label=label)
        ax.fill_between(centers, means-stds, means+stds, color=color, alpha=0.15)
    ax.plot([0, 300], [0, 300], 'k--', alpha=0.2, linewidth=0.5)
    ax.plot([0, 300], [30, 30], 'gray', alpha=0.3, linewidth=0.5)
    ax.set_xlabel('Upper detector area', fontsize=10)
    ax.set_ylabel('Mean lower detector area', fontsize=10)
    ax.set_title('Profile: <Down> vs Up area\n(If gain shift, this week curve lies below last week)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Plot 5: Lower detector area distribution (conditional on Up>30)
    ax = axes[1, 1]
    down_when_up_l = d0[u0 > 30]
    down_when_up_t = d40[u40 > 30]
    bins_cond = np.linspace(-20, 300, 101)
    ax.hist(down_when_up_l, bins=bins_cond, alpha=0.5, color='royalblue', density=True,
            label=f'0pl, n={len(down_when_up_l)}')
    ax.hist(down_when_up_t, bins=bins_cond, alpha=0.5, color='crimson', density=True,
            label=f'40pl, n={len(down_when_up_t)}')
    ax.axvline(30, color='black', linestyle='--', alpha=0.4)
    ax.set_xlabel('Lower detector area', fontsize=10)
    ax.set_ylabel('Density', fontsize=10)
    ax.set_title('Lower Area Distribution | Up>30\n(critical diagnostic)', fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(-20, 250)

    # Plot 6: Fraction of lower null (<5) vs upper area
    ax = axes[1, 2]
    bins_up2 = np.linspace(0, 200, 21)
    for (u, d, color, label) in [(u0, d0, 'royalblue', '0pl last'),
                                   (u40, d40, 'crimson', '40pl this')]:
        frac_null = []
        centers2 = []
        for i in range(len(bins_up2) - 1):
            mask = (u >= bins_up2[i]) & (u < bins_up2[i+1])
            if np.sum(mask) > 20:
                n_null = np.sum(d[mask] < 5)
                frac_null.append(n_null / np.sum(mask))
                centers2.append((bins_up2[i] + bins_up2[i+1]) / 2)
        ax.plot(centers2, frac_null, 'o-', color=color, linewidth=2, markersize=5, label=label)
    ax.set_xlabel('Upper detector area', fontsize=10)
    ax.set_ylabel('Fraction with Down area < 5', fontsize=10)
    ax.set_title('P(Down<5 | Up) vs Up area\n(High frac=geometry loss)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)

    fig.tight_layout()
    plt.savefig('/home/guiyu/workspace/CAEN/data/diagnostic_v4_2d.png', dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: /home/guiyu/workspace/CAEN/data/diagnostic_v4_2d.png")
    plt.show()

if __name__ == '__main__':
    main()
