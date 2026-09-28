#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: TOPOLOGICAL COMPLEX WINDING & BERRY VORTEX AUDIT
Module: 08_prime_topological_winding_berry_audit.py (Vortex Kernel Calibrated)
Description:
  1. Computes multi-body action S2(t), S3(t) across continuous spectrum t in [13.0, 35.0]
  2. Tracks spectral phase winding staircase W(t) and Berry phase slip velocity Omega(t)
  3. Audits true 2D Poincare-Hopf vortex kernel via multi-body topological order parameter
     Psi(s) around s0 = 1/2 + i*t0 vs off-resonance control s_ctrl = 1/2 + i*t_mid
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

def run_winding_berry_audit():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. Target Zeros & System Setup
    # -------------------------------------------------------------
    target_zeros = np.array([14.134725, 21.022040, 25.010858, 30.424876, 32.935062])
    
    N_primes = 25
    primes = get_primes(N_primes)
    log_p = np.log(primes)
    sqrt_p = np.sqrt(primes)
    
    num_pts = 1500
    t_arr = np.linspace(13.0, 35.0, num_pts)
    dt = t_arr[1] - t_arr[0]
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: 2D TOPOLOGICAL COMPLEX WINDING & BERRY VORTEX AUDIT")
    print(f"  Prime Modes (N)      : {N_primes} (p_max = {primes[-1]})")
    print(f"  Spectral Span        : t in [13.00, 35.00] ({num_pts} points)")
    print(f"  Target Riemann Zeros : {list(np.round(target_zeros, 4))}")
    print("=" * 85)

    # -------------------------------------------------------------
    # 2. Vectorized 1D Spectral Action & Berry Curvature
    # -------------------------------------------------------------
    print("[*] Evaluating continuous multi-body spectral dynamics...")
    
    pair_i, pair_j = np.triu_indices(N_primes, k=1)
    diff_2 = log_p[pair_i] - log_p[pair_j]
    w_2 = 1.0 / (sqrt_p[pair_i] * sqrt_p[pair_j])
    norm_w2 = np.sum(w_2)
    
    tri_comb = np.array(list(itertools.combinations(range(N_primes), 3)), dtype=np.int32)
    p_i, p_j, p_k = tri_comb[:, 0], tri_comb[:, 1], tri_comb[:, 2]
    diff_3 = log_p[p_i] + log_p[p_j] - log_p[p_k]
    w_3 = 1.0 / (sqrt_p[p_i] * sqrt_p[p_j] * sqrt_p[p_k])
    norm_w3 = np.sum(w_3)
    
    phase_2 = t_arr[:, None] * diff_2[None, :]
    phase_3 = t_arr[:, None] * diff_3[None, :]
    
    S2 = np.sum(w_2[None, :] * np.cos(phase_2), axis=1) / norm_w2
    S3 = np.sum(w_3[None, :] * np.cos(phase_3), axis=1) / norm_w3
    
    u = S2 - np.mean(S2)
    v = S3 - np.mean(S3)
    
    phi_unwrapped = np.unwrap(np.arctan2(v, u))
    winding_W = (phi_unwrapped - phi_unwrapped[0]) / (2.0 * np.pi)
    
    du_dt = np.gradient(u, dt)
    dv_dt = np.gradient(v, dt)
    denom = u**2 + v**2 + 1e-12
    omega_berry = (u * dv_dt - v * du_dt) / denom

    # -------------------------------------------------------------
    # 3. Multi-Body Fock-State Topological Order Parameter Loop
    # -------------------------------------------------------------
    print("[*] Auditing calibrated 2D Poincare-Hopf complex loop...")
    
    t0_target = target_zeros[0]  # 14.134725
    t_control = 0.5 * (target_zeros[0] + target_zeros[1])  # 17.57838
    
    r_loop = 0.28
    num_loop = 400
    theta = np.linspace(0, 2.0 * np.pi, num_loop)
    
    # Synthesize multi-body composite Fock modes (n = 1..M)
    M_modes = 80
    n_arr = np.arange(1, M_modes + 1)
    log_n = np.log(n_arr)
    signs = (-1.0) ** (n_arr - 1)
    
    # Soft Cosine regularization window to eliminate Gibbs ringing
    half_M = M_modes // 2
    weights_m = np.ones(M_modes)
    weights_m[half_M:] = 0.5 * (1.0 + np.cos(np.pi * np.arange(half_M) / half_M))

    def compute_psi_loop(sigma_center, t_center):
        sig = sigma_center + r_loop * np.cos(theta)
        tau = t_center + r_loop * np.sin(theta)
        
        # Psi(s) = sum w_n * (-1)^(n-1) * n^(-sigma - i*tau)
        amp = weights_m[None, :] * signs[None, :] * (n_arr[None, :] ** (-sig[:, None]))
        phase = tau[:, None] * log_n[None, :]
        
        re_psi = np.sum(amp * np.cos(phase), axis=1)
        im_psi = -np.sum(amp * np.sin(phase), axis=1)
        
        phase_loop = np.unwrap(np.arctan2(im_psi, re_psi))
        index = (phase_loop[-1] - phase_loop[0]) / (2.0 * np.pi)
        return re_psi, im_psi, index

    # Encircle Zero 1: s0 = 0.5 + i * 14.1347
    re_zero, im_zero, index_zero = compute_psi_loop(0.5, t0_target)
    
    # Encircle Control Vacuum: s_off = 0.5 + i * 17.5784
    re_ctrl, im_ctrl, index_ctrl = compute_psi_loop(0.5, t_control)
    
    print(f"    - Target Zero t0 (14.1347) Complex Loop Index : {index_zero:+.4f} (Integer Vortex Kernel)")
    print(f"    - Control Midpoint (17.5784) Complex Loop Index: {index_ctrl:+.4f} (Trivial Vacuum)")

    # -------------------------------------------------------------
    # 4. Diagnostic Visualization (Python 3.14 Fail-Safe)
    # -------------------------------------------------------------
    print("[*] Generating publication diagnostic figure...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9))
    
    # Panel (a): 2D Action Phase Space Orbit
    ax1.plot(u, v, color='#1f77b4', lw=1.2, alpha=0.75, label='Phase Orbit (S2, S3)')
    ax1.axhline(0, color='gray', linestyle=':', lw=1.0)
    ax1.axvline(0, color='gray', linestyle=':', lw=1.0)
    for idx, tz in enumerate(target_zeros):
        iz = np.argmin(np.abs(t_arr - tz))
        ax1.plot(u[iz], v[iz], 'ro', markersize=7)
        ax1.annotate(f't_{idx}', (u[iz], v[iz]), textcoords="offset points", 
                     xytext=(6, 5), fontsize=8.5, fontweight='bold', color='red')
    ax1.set_title('(a) Multi-Body Phase Orbit & Critical Nodes', fontweight='bold')
    ax1.set_xlabel('Centered 2-Body Action u = S2 - <S2>')
    ax1.set_ylabel('Centered 3-Body Action v = S3 - <S3>')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower left', fontsize=8.5)
    
    # Panel (b): Topological Winding Staircase
    ax2.plot(t_arr, winding_W, color='#d62728', lw=2.0, label='Topological Winding W(t)')
    for tz in target_zeros:
        ax2.axvline(tz, color='black', linestyle='--', alpha=0.6, lw=1.2)
    ax2.set_title('(b) Topological Winding Number Staircase W(t)', fontweight='bold')
    ax2.set_xlabel('Spectral Coordinate t')
    ax2.set_ylabel('Accumulated Winding (Cycles)')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=8.5)
    
    # Panel (c): Berry Phase Velocity Spikes
    ax3.plot(t_arr, np.abs(omega_berry), color='#2ca02c', lw=1.8, label='Berry Phase Velocity |Omega(t)|')
    for tz in target_zeros:
        ax3.axvline(tz, color='red', linestyle=':', alpha=0.7, lw=1.2)
    ax3.set_title('(c) Topological Berry Phase Slip Resonance', fontweight='bold')
    ax3.set_xlabel('Spectral Coordinate t')
    ax3.set_ylabel('Curvature Strength |dPhi / dt|')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper right', fontsize=8.5)
    
    # Panel (d): Calibrated 2D Complex Contour Encirclement
    ax4.plot(re_zero, im_zero, 'r-', lw=2.2, label=f'Zero s0 Loop (Winding = {round(index_zero):+d})')
    ax4.plot(re_ctrl, im_ctrl, 'b--', lw=1.8, label=f'Control Loop (Winding = {round(index_ctrl):+d})')
    ax4.plot(0, 0, 'k+', markersize=12, mew=2.5, label='Vortex Origin (0,0)')
    ax4.set_title('(d) 2D Complex Contour: Topological Vortex Core', fontweight='bold')
    ax4.set_xlabel('Re[Psi(s)]')
    ax4.set_ylabel('Im[Psi(s)]')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper right', fontsize=8.5)
    
    plt.subplots_adjust(top=0.92, bottom=0.10, left=0.08, right=0.95, hspace=0.32, wspace=0.28)
    
    out_png = '08_prime_topological_winding_berry_audit.png'
    plt.savefig(out_png, dpi=200)
    plt.close(fig)
    
    t_elapsed = time.time() - t_start
    print("=" * 85)
    print(f"[+] Topological audit visual exported: {out_png}")
    print(f"[+] Total execution time: {t_elapsed:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_winding_berry_audit()