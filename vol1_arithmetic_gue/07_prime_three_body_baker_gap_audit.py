#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: BAKER ARITHMETIC GAP & COLLECTIVE STIFFNESS ASYMPTOTICS
Module: 07_prime_three_body_baker_gap_audit.py (Python 3.14 Bulletproof Edition)
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

def run_baker_gap_audit():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. Scaling Lattice Setup
    # -------------------------------------------------------------
    N_tiers = [15, 30, 60, 120, 240]
    max_N = max(N_tiers)
    primes_all = get_primes(max_N)
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: BAKER ARITHMETIC GAP & STIFFNESS ASYMPTOTICS")
    print(f"  Scaling Tiers (N) : {N_tiers}")
    print(f"  Lattice Envelope  : N = {max_N} (p_max = {primes_all[-1]:,d})")
    print("=" * 85)

    results = []
    
    # -------------------------------------------------------------
    # 2. Exhaustive Triad Search across Tiers
    # -------------------------------------------------------------
    for N in N_tiers:
        p_sub = primes_all[:N]
        p_max = p_sub[-1]
        log_p = np.log(p_sub)
        
        tri_comb = np.array(list(itertools.combinations(range(N), 3)), dtype=np.int32)
        p_i, p_j, p_k = tri_comb[:, 0], tri_comb[:, 1], tri_comb[:, 2]
        
        val_p = p_sub[p_i]
        val_q = p_sub[p_j]
        val_r = p_sub[p_k]
        
        delta = np.abs(log_p[p_i] + log_p[p_j] - log_p[p_k])
        weights = 1.0 / np.sqrt(val_p * val_q * val_r)
        
        min_idx = np.argmin(delta)
        delta_min = delta[min_idx]
        best_p, best_q, best_r = val_p[min_idx], val_q[min_idx], val_r[min_idx]
        arith_diff = abs(best_p * best_q - best_r)
        
        K_total = np.sum((delta ** 2) * weights)
        mean_delta = np.mean(delta)
        triad_count = len(tri_comb)
        
        lower_bound = 1.0 / best_r
        
        results.append({
            'N': N,
            'p_max': p_max,
            'triads': triad_count,
            'delta_min': delta_min,
            'best_triad': (best_p, best_q, best_r),
            'arith_diff': arith_diff,
            'lower_bound': lower_bound,
            'K_total': K_total,
            'mean_delta': mean_delta
        })
        
        print(f"  [Tier N = {N:>3d} | p_max = {p_max:>5,d} | Triads = {triad_count:>9,d}]")
        print(f"    - Minimizing Triad ({best_p} * {best_q} vs {best_r}) | Integer |pq - r| = {arith_diff}")
        print(f"    - Observed Gap Delta_min  : {delta_min:.6e}")
        print(f"    - Elementary Bound (1/r)  : {lower_bound:.6e} (Ratio: {delta_min/lower_bound:.4f})")
        print(f"    - Collective Stiffness K  : {K_total:.4f}")
        print("-" * 85)

    # -------------------------------------------------------------
    # 3. Diagnostic Visualization (Python 3.14 Fail-Safe Rendering)
    # -------------------------------------------------------------
    print("[*] Generating asymptotic scaling figure...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 9))
    
    p_max_list = [r['p_max'] for r in results]
    delta_min_list = [r['delta_min'] for r in results]
    bound_list = [r['lower_bound'] for r in results]
    k_total_list = [r['K_total'] for r in results]
    triad_counts = [r['triads'] for r in results]
    
    # Panel (a): Delta_min vs Theoretical Integer Bound 1/r
    ax1.loglog(p_max_list, delta_min_list, 'ro-', lw=2.2, markersize=8, label='Observed Delta_min')
    ax1.loglog(p_max_list, bound_list, 'k--', lw=1.8, label='Baker Floor ~ 1 / r*')
    ax1.set_title('(a) Asymptotic Minimal Gap vs 1/r Floor', fontweight='bold')
    ax1.set_xlabel('Max Prime Cutoff p_max')
    ax1.set_ylabel('Arithmetic Phase Gap Delta')
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend(loc='lower left', fontsize=9.0)
    
    # Panel (b): Minimizing Arithmetic Residual |p*q - r|
    labels = [f"({r['best_triad'][0]}x{r['best_triad'][1]},{r['best_triad'][2]})" for r in results]
    y_pos = np.arange(len(results))
    diffs = [r['arith_diff'] for r in results]
    ax2.bar(y_pos, diffs, color='#1f77b4', edgecolor='black', alpha=0.75, width=0.5)
    ax2.set_xticks(y_pos)
    ax2.set_xticklabels(labels, rotation=20, ha='right', fontsize=8.5)
    ax2.axhline(1.0, color='red', linestyle='--', lw=1.5, label='Absolute Integer Floor = 1')
    ax2.set_title('(b) Arithmetic Distance |p*q - r| >= 1', fontweight='bold')
    ax2.set_ylabel('Absolute Integer Distance')
    ax2.set_ylim(0, max(diffs) + 2)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9.0)
    
    # Panel (c): Collective Topological Restoring Stiffness K_total(N)
    ax3.plot(p_max_list, k_total_list, 'bs-', lw=2.2, markersize=8, label='Total Stiffness K_total')
    ax3.set_title('(c) Collective Stiffness Divergence (K -> Inf)', fontweight='bold')
    ax3.set_xlabel('Max Prime Cutoff p_max')
    ax3.set_ylabel('Total Restoring Stiffness K')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=9.0)
    
    # Panel (d): Active 3-Body Triad Channel Explosion
    ax4.plot(p_max_list, triad_counts, 'md-', lw=2.2, markersize=8, label='Triad Channels O(N^3)')
    ax4.set_title('(d) Quantum Phase Shield Scaling', fontweight='bold')
    ax4.set_xlabel('Max Prime Cutoff p_max')
    ax4.set_ylabel('Number of 3-Body Channels')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper left', fontsize=9.0)
    
    # 고정 마진 (자동 계산 충돌 방지)
    plt.subplots_adjust(top=0.92, bottom=0.10, left=0.10, right=0.95, hspace=0.32, wspace=0.30)
    
    out_png = '07_prime_three_body_baker_gap_audit.png'
    plt.savefig(out_png, dpi=200)
    plt.close(fig)
    
    t_elapsed = time.time() - t_start
    print("=" * 85)
    print(f"[+] Baker gap visual exported: {out_png}")
    print(f"[+] Total audit execution time: {t_elapsed:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_baker_gap_audit()