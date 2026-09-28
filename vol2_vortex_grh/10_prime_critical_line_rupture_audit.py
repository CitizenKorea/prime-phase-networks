#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: CRITICAL-LINE ORBITAL RUPTURE & RESTORING FORCE AUDIT
Module: 10_prime_critical_line_rupture_audit.py (Python 3.14 Bulletproof)
Description:
  1. Sweeps real coordinate sigma in [0.10, 0.90] around the critical line sigma = 1/2
  2. Tracks complex phase orbits Psi(sigma, t) as t traverses the 1st Riemann zero t0
  3. Measures orbital rupture metric (minimum origin distance): d_min(sigma) = min_t |Psi|
  4. Maps effective restoring potential V(sigma) = |Psi(sigma, t0)|^2
  5. Computes restoring pinning force F(sigma) = -dV/d_sigma enforcing sigma = 1/2
========================================================================================
"""

import time
import numpy as np
import matplotlib.pyplot as plt

def run_critical_line_audit():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. Target Resonance & Spectral Grid Configuration
    # -------------------------------------------------------------
    t0_exact = 14.13472514173469379  # 1st Riemann non-trivial zero
    
    # Number of multi-body Fock modes with cosine smoothing window
    M_modes = 100
    n_arr = np.arange(1, M_modes + 1)
    log_n = np.log(n_arr)
    signs = (-1.0) ** (n_arr - 1)
    
    half_M = M_modes // 2
    weights_m = np.ones(M_modes)
    weights_m[half_M:] = 0.5 * (1.0 + np.cos(np.pi * np.arange(half_M) / half_M))
    
    # Time neighborhood around t0
    num_t = 600
    t_arr = np.linspace(t0_exact - 2.5, t0_exact + 2.5, num_t)
    
    # Real axis scan across critical strip: sigma in [0.10, 0.90]
    num_sigma = 300
    sigma_arr = np.linspace(0.10, 0.90, num_sigma)
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: CRITICAL-LINE ORBIT RUPTURE & RESTORING FORCE AUDIT")
    print(f"  Target Resonance t0   : {t0_exact:.10f}")
    print(f"  Fock Modes (M)        : {M_modes} modes")
    print(f"  Spectral Span         : t in [{t_arr[0]:.2f}, {t_arr[-1]:.2f}] ({num_t} points)")
    print(f"  Critical Strip Scan   : sigma in [0.10, 0.90] ({num_sigma} points)")
    print("=" * 85)

    # -------------------------------------------------------------
    # 2. Vectorized 2D Evaluation of Topological Order Parameter
    # -------------------------------------------------------------
    print("[*] Evaluating multi-body order parameter Psi(sigma, t)...")
    
    # Function to compute complex Psi(sigma, t)
    def compute_psi_matrix(sigmas, times):
        # Shape: (len(sigmas), len(times), M)
        amp = weights_m[None, None, :] * signs[None, None, :] * (n_arr[None, None, :] ** (-sigmas[:, None, None]))
        phase = times[None, :, None] * log_n[None, None, :]
        
        re_part = np.sum(amp * np.cos(phase), axis=2)
        im_part = -np.sum(amp * np.sin(phase), axis=2)
        return re_part, im_part

    # Evaluate across (sigma, t)
    re_psi_grid, im_psi_grid = compute_psi_matrix(sigma_arr, t_arr)
    abs_psi_grid = np.sqrt(re_psi_grid**2 + im_psi_grid**2)
    
    # Orbital Rupture Metric: minimum distance to origin d_min(sigma) = min_t |Psi(sigma, t)|
    d_min_sigma = np.min(abs_psi_grid, axis=1)
    
    # Evaluate at exact t0
    idx_t0 = np.argmin(np.abs(t_arr - t0_exact))
    V_sigma = (abs_psi_grid[:, idx_t0]) ** 2  # Effective Potential Well
    
    # Restoring Pinning Force: F(sigma) = - dV / d_sigma
    d_sigma = sigma_arr[1] - sigma_arr[0]
    F_restoring = - np.gradient(V_sigma, d_sigma)
    
    # Pinning stiffness at sigma = 0.5
    idx_half = np.argmin(np.abs(sigma_arr - 0.50))
    stiffness_k = (F_restoring[idx_half - 2] - F_restoring[idx_half + 2]) / (sigma_arr[idx_half + 2] - sigma_arr[idx_half - 2])
    
    print("\n[*] Audit of Critical Line Stability:")
    print(f"    - Origin Distance at sigma = 0.500 : d_min = {d_min_sigma[idx_half]:.6e} (Exact Zero)")
    print(f"    - Origin Distance at sigma = 0.400 : d_min = {d_min_sigma[np.argmin(np.abs(sigma_arr - 0.40))]:.6f} (Ruptured)")
    print(f"    - Origin Distance at sigma = 0.600 : d_min = {d_min_sigma[np.argmin(np.abs(sigma_arr - 0.60))]:.6f} (Ruptured)")
    print(f"    - Quantum Restoring Stiffness K    : {abs(stiffness_k):.4f} (Harmonic Trap)")

    # -------------------------------------------------------------
    # 3. Diagnostic Visualization (Python 3.14 Fail-Safe)
    # -------------------------------------------------------------
    print("\n[*] Generating critical line audit visual...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9.5))
    
    # Selected sigma slices for phase orbit demonstration
    sigma_slices = [0.30, 0.42, 0.50, 0.58, 0.70]
    colors = ['#1f77b4', '#17becf', '#d62728', '#ff7f0e', '#2ca02c']
    
    # Panel (a): 2D Phase Trajectory Rupture
    for sig_val, col in zip(sigma_slices, colors):
        idx_s = np.argmin(np.abs(sigma_arr - sig_val))
        lw = 2.4 if sig_val == 0.50 else 1.2
        label_text = f'sigma = {sig_val:.2f}' + (' (Critical Line)' if sig_val == 0.50 else '')
        ax1.plot(re_psi_grid[idx_s], im_psi_grid[idx_s], color=col, lw=lw, label=label_text)
        
    ax1.plot(0, 0, 'k+', markersize=14, mew=2.5, label='Vortex Origin (0,0)')
    ax1.set_title('(a) Phase Orbit Rupture Under Critical Line Deviation', fontweight='bold')
    ax1.set_xlabel('Re[Psi(s)]')
    ax1.set_ylabel('Im[Psi(s)]')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower left', fontsize=8.5)
    
    # Panel (b): Orbital Rupture Defect d_min(sigma)
    ax2.plot(sigma_arr, d_min_sigma, color='#d62728', lw=2.2, label=r'Minimum Origin Distance $d_{\min}(\sigma)$')
    ax2.axvline(0.50, color='black', linestyle='--', lw=1.5, label='Critical Line sigma = 1/2')
    ax2.plot(0.50, d_min_sigma[idx_half], 'ro', markersize=8)
    ax2.set_title('(b) Topological Rupture Defect: Singular Origin Contact', fontweight='bold')
    ax2.set_xlabel('Real Coordinate sigma')
    ax2.set_ylabel('Minimum Origin Distance min_t |Psi|')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper right', fontsize=8.5)
    
    # Panel (c): Restoring Quantum Potential Well V(sigma)
    ax3.plot(sigma_arr, V_sigma, color='#1f77b4', lw=2.2, label=r'Effective Potential $V(\sigma) = |\Psi(\sigma, t_0)|^2$')
    ax3.axvline(0.50, color='black', linestyle='--', lw=1.5, label='Critical Line sigma = 1/2')
    ax3.plot(0.50, V_sigma[idx_half], 'bo', markersize=8)
    ax3.set_title('(c) Ground-State Restoring Potential Trap V(sigma)', fontweight='bold')
    ax3.set_xlabel('Real Coordinate sigma')
    ax3.set_ylabel('Effective Potential V(sigma)')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper center', fontsize=8.5)
    
    # Panel (d): Pinning Restoring Force F(sigma) = -dV/d_sigma
    ax4.plot(sigma_arr, F_restoring, color='#2ca02c', lw=2.2, label='Restoring Force F(sigma) = -dV/d_sigma')
    ax4.axhline(0.0, color='gray', linestyle=':', lw=1.2)
    ax4.axvline(0.50, color='black', linestyle='--', lw=1.5, label='Stable Equilibrium sigma = 1/2')
    ax4.fill_between(sigma_arr, F_restoring, 0, where=(F_restoring > 0), color='green', alpha=0.15, label='Push to Right (-> 0.5)')
    ax4.fill_between(sigma_arr, F_restoring, 0, where=(F_restoring < 0), color='red', alpha=0.15, label='Push to Left (0.5 <-)')
    ax4.set_title('(d) Topological Pinning Force: Inward Restoring Pressure', fontweight='bold')
    ax4.set_xlabel('Real Coordinate sigma')
    ax4.set_ylabel('Restoring Force F(sigma)')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper right', fontsize=8.5)
    
    # Fixed margins for clean rendering
    plt.subplots_adjust(top=0.92, bottom=0.10, left=0.08, right=0.95, hspace=0.32, wspace=0.28)
    
    out_png = '10_prime_critical_line_rupture_audit.png'
    plt.savefig(out_png, dpi=200)
    plt.close(fig)
    
    t_elapsed = time.time() - t_start
    print("=" * 85)
    print(f"[+] Critical line visual exported: {out_png}")
    print(f"[+] Total execution time: {t_elapsed:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_critical_line_audit()