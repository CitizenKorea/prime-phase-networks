#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: 3-BODY KNOT RESONANCE & RIEMANN ZERO TOPOLOGICAL SCANNER
Module: 03_prime_three_body_riemann_resonance_scanner.py
Description:
  1. Sweeps spectral coordinate t in [10, 30] across the first 3 Riemann zeros:
     t0 = 14.134725, t1 = 21.022040, t2 = 25.010858
  2. Compares 2-body pairwise action S_2(t) against 3-body frustrated knot action S_3(t)
  3. Tests Topological Inversion Ratio R_{3/2}(t) = |S_3(t)| / (|S_2(t)| + eps)
  4. Plots 2D Phase-Space Trajectory (S_2 vs S_3) limit-cycle dynamics
========================================================================================
"""

import time
import itertools
import numpy as np
import matplotlib.pyplot as plt

def get_primes(n):
    """Return the first n prime numbers."""
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return np.array(primes, dtype=np.int64)

def run_riemann_resonance_scan():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. System Parameters
    # -------------------------------------------------------------
    N_primes = 30  # 30 primes yield 435 pairs and 4,060 triplets
    primes = get_primes(N_primes)
    log_p = np.log(primes)
    
    # Target Riemann non-trivial zeros in range [10, 30]
    riemann_zeros = [14.1347251417, 21.0220396388, 25.0108575801]
    
    # Spectral coordinate sweep
    num_t = 600
    t_arr = np.linspace(10.0, 30.0, num_t)
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: 3-BODY KNOT & RIEMANN ZERO RESONANCE SCANNER")
    print(f"  Prime Modes: N = {N_primes} (p_max = {primes[-1]})")
    print(f"  Spectral Sweep: t in [10.0, 30.0] ({num_t} sample points)")
    print(f"  Target Zeros  : t0 = {riemann_zeros[0]:.4f}, t1 = {riemann_zeros[1]:.4f}, t2 = {riemann_zeros[2]:.4f}")
    print("=" * 85)

    # -------------------------------------------------------------
    # 2. Vectorized 2-Body and 3-Body Phase Arrays
    # -------------------------------------------------------------
    # 2-Body: Delta_2 = ln(p/q), Weight = 1 / sqrt(pq)
    pair_i, pair_j = np.triu_indices(N_primes, k=1)
    delta_2 = log_p[pair_i] - log_p[pair_j]
    w_2 = 1.0 / np.sqrt(primes[pair_i] * primes[pair_j])
    norm_w2 = np.sum(w_2)
    
    # 3-Body: Delta_3 = ln(pq/r), Weight = 1 / sqrt(pqr)
    tri_comb = np.array(list(itertools.combinations(range(N_primes), 3)), dtype=np.int32)
    p_i, p_j, p_k = tri_comb[:, 0], tri_comb[:, 1], tri_comb[:, 2]
    
    # Symmetric 3-body phase metric: ln(p*q / r)
    delta_3 = log_p[p_i] + log_p[p_j] - log_p[p_k]
    w_3 = 1.0 / np.sqrt(primes[p_i] * primes[p_j] * primes[p_k])
    norm_w3 = np.sum(w_3)
    
    print(f"[*] Precomputed: {len(pair_i):,d} 2-body pairs | {len(tri_comb):,d} 3-body triangles")

    # -------------------------------------------------------------
    # 3. High-Speed Vectorized Spectral Sweep
    # -------------------------------------------------------------
    print("[*] Sweeping spectral coordinate matrix...")
    
    # Shape: (num_t, num_pairs)
    cos_2 = np.cos(t_arr[:, None] * delta_2[None, :])
    S2_t = np.sum(cos_2 * w_2[None, :], axis=1) / norm_w2
    
    # Shape: (num_t, num_triplets)
    cos_3 = np.cos(t_arr[:, None] * delta_3[None, :])
    S3_t = np.sum(cos_3 * w_3[None, :], axis=1) / norm_w3
    
    # Topological Inversion Ratio: R_{3/2} = |S3| / (|S2| + eps)
    eps = 0.015
    ratio_32 = np.abs(S3_t) / (np.abs(S2_t) + eps)
    
    # Audit at exact Riemann zeros
    print("\n" + "-" * 85)
    print("  AUDIT AT EXACT RIEMANN NON-TRIVIAL ZEROS:")
    print("-" * 85)
    for z_idx, tz in enumerate(riemann_zeros):
        idx_z = np.argmin(np.abs(t_arr - tz))
        print(f"  [Zero {z_idx} at t = {tz:.4f}]")
        print(f"    - 2-Body Action S_2(t)          : {S2_t[idx_z]:+.6f}")
        print(f"    - 3-Body Knot Action S_3(t)     : {S3_t[idx_z]:+.6f}")
        print(f"    - Topological Ratio |S3|/(|S2|) : {ratio_32[idx_z]:.4f}")
    print("-" * 85)

    # -------------------------------------------------------------
    # 4. Publication Diagnostic Figure Generation
    # -------------------------------------------------------------
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9.5))
    
    # Panel (a): 2-Body Action S_2(t)
    ax1.plot(t_arr, S2_t, color='#2ca02c', lw=1.8, label=r'2-Body Action $S_2(t)$ (Pairwise)')
    for idx_z, tz in enumerate(riemann_zeros):
        ax1.axvline(tz, color='black', linestyle='--', alpha=0.7, 
                    label=rf'Riemann $t_{idx_z}$ ({tz:.2f})' if idx_z == 0 else "")
    ax1.axhline(0.0, color='gray', linestyle=':', lw=1.0)
    ax1.set_title(r'(a) 2-Body Pairwise Coherence Action $S_2(t)$', fontweight='bold')
    ax1.set_xlabel('Spectral Coordinate $t$')
    ax1.set_ylabel(r'Normalized Action $S_2(t)$')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=9.0)
    
    # Panel (b): 3-Body Frustrated Knot Action S_3(t)
    ax2.plot(t_arr, S3_t, color='#d62728', lw=1.8, label=r'3-Body Knot Action $S_3(t)$ ($\zeta(3)$ Frustrated)')
    for tz in riemann_zeros:
        ax2.axvline(tz, color='black', linestyle='--', alpha=0.7)
    ax2.axhline(0.0, color='gray', linestyle=':', lw=1.0)
    ax2.set_title(r'(b) 3-Body Frustrated Knot Action $S_3(t)$', fontweight='bold')
    ax2.set_xlabel('Spectral Coordinate $t$')
    ax2.set_ylabel(r'Normalized Action $S_3(t)$')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right', fontsize=9.0)
    
    # Panel (c): Topological Dominance Ratio R_{3/2}(t)
    ax3.plot(t_arr, ratio_32, color='#9467bd', lw=2.0, label=r'$\mathcal{R}_{3/2}(t) = |S_3| / (|S_2| + \epsilon)$')
    for idx_z, tz in enumerate(riemann_zeros):
        idx_near = np.argmin(np.abs(t_arr - tz))
        ax3.plot(tz, ratio_32[idx_near], 'ro', markersize=8)
        ax3.annotate(rf'$t_{idx_z}$', (tz, ratio_32[idx_near]),
                     textcoords="offset points", xytext=(0, 8), ha='center', fontweight='bold')
        ax3.axvline(tz, color='black', linestyle='--', alpha=0.7)
    ax3.set_title(r'(c) Topological Knot Dominance $\mathcal{R}_{3/2}(t)$', fontweight='bold')
    ax3.set_xlabel('Spectral Coordinate $t$')
    ax3.set_ylabel(r'Inversion Ratio $\mathcal{R}_{3/2}$')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper right', fontsize=9.0)
    
    # Panel (d): 2D Topological Phase-Space Orbit (S_2 vs S_3)
    scatter = ax4.scatter(S2_t, S3_t, c=t_arr, cmap='viridis', s=12, alpha=0.65)
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('Coordinate $t$', rotation=270, labelpad=15)
    
    for idx_z, tz in enumerate(riemann_zeros):
        idx_near = np.argmin(np.abs(t_arr - tz))
        ax4.plot(S2_t[idx_near], S3_t[idx_near], 'r*', markersize=14, 
                 label=rf'Zero $t_{idx_z}$' if idx_z == 0 else "")
    ax4.axvline(0.0, color='gray', linestyle=':', lw=1.0)
    ax4.axhline(0.0, color='gray', linestyle=':', lw=1.0)
    ax4.set_title(r'(d) Topological Phase Orbit $(S_2(t), S_3(t))$', fontweight='bold')
    ax4.set_xlabel(r'2-Body Action $S_2$')
    ax4.set_ylabel(r'3-Body Knot Action $S_3$')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper left', fontsize=9.0)
    
    plt.tight_layout()
    out_png = '03_prime_three_body_riemann_resonance_scanner.png'
    plt.savefig(out_png, dpi=300)
    plt.close()
    
    t_elapsed = time.time() - t_start
    print("=" * 85)
    print(f"[+] Resonance scan visual exported: {out_png}")
    print(f"[+] Total execution time: {t_elapsed:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_riemann_resonance_scan()