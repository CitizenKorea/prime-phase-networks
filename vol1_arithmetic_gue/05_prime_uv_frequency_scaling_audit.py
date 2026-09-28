#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: UV HIGH-FREQUENCY SCALING & ZERO-PINNING AUDIT
Module: 05_prime_uv_frequency_scaling_audit.py
Description:
  1. Scales prime oscillator count N across [15, 35, 75, 150, 300, 600, 1200]
     (Max prime expands from p=47 up to p=9,743: UV completion)
  2. Uses O(N) vectorized identity for pairwise cross-coupling action S_2(t; N)
  3. Tracks stationary peak convergence: Delta t(N) = |t*(N) - t0|
  4. Audits spectral stiffness / curvature surge K(N) = |d^2 S_2 / dt^2|
  5. Generates 4-panel diagnostic figure showing micro-scale zero trapping
========================================================================================
"""

import time
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

def run_uv_scaling_audit():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. Physics Configuration & Grid Setup
    # -------------------------------------------------------------
    t0_exact = 14.13472514173469379  # 1st Riemann non-trivial resonance
    
    # Range of prime modes to audit (UV frequency ladder)
    N_list = [15, 35, 75, 150, 300, 600, 1200]
    max_N = max(N_list)
    primes_all = get_primes(max_N)
    
    # High-resolution spectral grid around t0 (+/- 0.5)
    num_pts = 1000
    t_arr = np.linspace(t0_exact - 0.5, t0_exact + 0.5, num_pts)
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: UV HIGH-FREQUENCY SCALING & ZERO-PINNING AUDIT")
    print(f"  Audit Tiers (N)    : {N_list}")
    print(f"  Max Prime Lattice  : N = {max_N} (p_max = {primes_all[-1]:,d})")
    print(f"  Target Resonance t0: {t0_exact:.10f}")
    print("=" * 85)

    # -------------------------------------------------------------
    # 2. Vectorized O(N) Evaluation across Scaling Tiers
    # -------------------------------------------------------------
    # S_2(t) is directly computed via the exact identity:
    # 2 * sum_{p<q} cos(t ln(p/q)) / sqrt(pq) = |sum p^{-1/2-it}|^2 - sum 1/p
    log_p_all = np.log(primes_all)
    inv_sqrt_p_all = 1.0 / np.sqrt(primes_all)
    
    # Precompute phase matrix for all primes: shape (num_pts, max_N)
    phase_all = t_arr[:, None] * log_p_all[None, :]
    cos_matrix = np.cos(phase_all) * inv_sqrt_p_all[None, :]
    sin_matrix = np.sin(phase_all) * inv_sqrt_p_all[None, :]
    
    # Velocity matrices: -d/dt (phase) = ln(p)
    dcos_matrix = -np.sin(phase_all) * (log_p_all * inv_sqrt_p_all)[None, :]
    dsin_matrix =  np.cos(phase_all) * (log_p_all * inv_sqrt_p_all)[None, :]
    
    # Acceleration matrices: -d^2/dt^2
    d2cos_matrix = -np.cos(phase_all) * ((log_p_all ** 2) * inv_sqrt_p_all)[None, :]
    d2sin_matrix = -np.sin(phase_all) * ((log_p_all ** 2) * inv_sqrt_p_all)[None, :]
    
    audit_results = []
    s2_curves = {}
    
    print("\n[*] Auditing finite-size scaling and high-frequency wave convergence...")
    
    for N in N_list:
        p_sub = primes_all[:N]
        p_max = p_sub[-1]
        
        # 1-Body amplitudes A(t) and B(t)
        A = np.sum(cos_matrix[:, :N], axis=1)
        B = -np.sum(sin_matrix[:, :N], axis=1)
        
        dA = np.sum(dcos_matrix[:, :N], axis=1)
        dB = -np.sum(dsin_matrix[:, :N], axis=1)
        
        d2A = np.sum(d2cos_matrix[:, :N], axis=1)
        d2B = -np.sum(d2sin_matrix[:, :N], axis=1)
        
        # Pairwise Cross-Coupling unnormalized: 0.5 * (A^2 + B^2 - sum(1/p))
        sum_inv_p = np.sum(1.0 / p_sub)
        unnorm_S2 = 0.5 * (A**2 + B**2 - sum_inv_p)
        
        # Analytical 1st and 2nd derivatives
        unnorm_dS2 = A * dA + B * dB
        unnorm_d2S2 = (dA**2 + dB**2) + (A * d2A + B * d2B)
        
        # Normalization factor: sum_{p<q} 1/sqrt(pq) = 0.5 * ((sum 1/sqrt(p))^2 - sum 1/p)
        norm_factor = 0.5 * ((np.sum(inv_sqrt_p_all[:N]))**2 - sum_inv_p)
        
        S2 = unnorm_S2 / norm_factor
        dS2 = unnorm_dS2 / norm_factor
        d2S2 = unnorm_d2S2 / norm_factor
        
        s2_curves[N] = S2
        
        # Locate local stationary peak (zero-crossing of dS2)
        idx_peak = np.argmin(np.abs(dS2))
        t_peak = t_arr[idx_peak]
        
        offset = t_peak - t0_exact
        abs_offset = abs(offset)
        curvature_at_peak = d2S2[idx_peak]
        stiffness = abs(curvature_at_peak)
        
        # Mean high-frequency dephasing cycle of this lattice: pi / ln(p_max)
        dephasing_cycle = np.pi / np.log(p_max)
        
        audit_results.append({
            'N': N,
            'p_max': p_max,
            't_peak': t_peak,
            'offset': offset,
            'abs_offset': abs_offset,
            'stiffness': stiffness,
            'dephase': dephasing_cycle
        })
        
        print(f"  [N = {N:>4d} | p_max = {p_max:>5,d}]  t* = {t_peak:.6f}  |  Offset = {offset:+.6f}  |  Stiffness K = {stiffness:.4f}  |  Dephase dt = {dephasing_cycle:.4f}")

    # -------------------------------------------------------------
    # 3. Diagnostic Visualization (4-Panel High-Precision Plot)
    # -------------------------------------------------------------
    print("\n[*] Generating high-frequency scaling diagnostic visual...")
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9.5))
    
    colors = plt.cm.viridis(np.linspace(0.15, 0.95, len(N_list)))
    
    # Panel (a): Resonance Line-Shape Evolution
    for idx, N in enumerate(N_list):
        ax1.plot(t_arr, s2_curves[N], lw=1.8, color=colors[idx], 
                 label=rf'$N={N}$ ($p={primes_all[N-1]}$)')
    ax1.axvline(t0_exact, color='red', linestyle='--', lw=1.5, label=rf'True Riemann $t_0$ ({t0_exact:.4f})')
    ax1.set_title(r'(a) High-Frequency Resonance Line-Shape Sharpening', fontweight='bold')
    ax1.set_xlabel('Spectral Coordinate $t$')
    ax1.set_ylabel(r'Normalized Pairwise Action $S_2(t)$')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=8.0)
    
    # Panel (b): Peak Offset Decay (Convergence to Zero)
    p_max_vals = [r['p_max'] for r in audit_results]
    offsets = [r['abs_offset'] for r in audit_results]
    ax2.loglog(p_max_vals, offsets, 'ro-', lw=2.2, markersize=7, label=r'Peak Discrepancy $|t^*(N) - t_0|$')
    ax2.set_title(r'(b) Finite-Size Scaling: UV Coordinate Convergence', fontweight='bold')
    ax2.set_xlabel(r'UV Prime Cutoff $p_{\max}$ (Log Scale)')
    ax2.set_ylabel(r'Coordinate Offset $|t^* - t_0|$ (Log Scale)')
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9.0)
    
    # Panel (c): Spectral Stiffness (Curvature) Locking
    stiffness_vals = [r['stiffness'] for r in audit_results]
    ax3.semilogx(p_max_vals, stiffness_vals, 'bs-', lw=2.2, markersize=7, label=r'Lattice Stiffness $K(N) = |S_2^{\prime\prime}(t^*)|$')
    ax3.set_title(r'(c) Spectral Stiffness: Potential Well Lock-in', fontweight='bold')
    ax3.set_xlabel(r'UV Prime Cutoff $p_{\max}$ (Log Scale)')
    ax3.set_ylabel(r'Topological Stiffness $K(N)$')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=9.0)
    
    # Panel (d): Microscopic Dephasing Cycle Compression
    dephase_vals = [r['dephase'] for r in audit_results]
    ax4.plot(p_max_vals, dephase_vals, 'md-', lw=2.2, markersize=7, label=r'Dephasing Cycle $\Delta t_{\mathrm{cycle}} \approx \pi / \ln p_{\max}$')
    ax4.axhline(0.0, color='gray', linestyle=':', lw=1.2)
    ax4.set_title(r'(d) UV High-Frequency Dephasing Compression', fontweight='bold')
    ax4.set_xlabel(r'UV Prime Cutoff $p_{\max}$')
    ax4.set_ylabel(r'Dephasing Resolution $\Delta t$ (Radians)')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper right', fontsize=9.0)
    
    plt.tight_layout()
    out_png = '05_prime_uv_frequency_scaling_audit.png'
    plt.savefig(out_png, dpi=300)
    plt.close()
    
    t_elapsed = time.time() - t_start
    print("=" * 85)
    print(f"[+] UV scaling visual exported: {out_png}")
    print(f"[+] Total execution time: {t_elapsed:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_uv_scaling_audit()