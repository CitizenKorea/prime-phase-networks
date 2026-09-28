#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: MULTI-BODY EFFECTIVE HAMILTONIAN & ZERO-MODE AUDIT
Module: 09_prime_effective_hamiltonian_audit.py (Python 3.14 Bulletproof)
Description:
  1. Constructs the 2-body pairwise coherence Hamiltonian matrix H2(t)
  2. Synthesizes the 3-body arithmetic frustration mean-field matrix H3(t)
  3. Assembles the unified multi-body Hamiltonian: H_eff(t) = H2(t) + g3 * H3(t)
  4. Fully diagonalizes H_eff(t) across t in [13.0, 35.0] covering first 5 Riemann zeros
  5. Audits zero-energy modes, spectral determinants, and 3-body level repulsion opening
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

def run_hamiltonian_audit():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. Configuration & Prime Mode Basis Setup
    # -------------------------------------------------------------
    target_zeros = np.array([14.134725, 21.022040, 25.010858, 30.424876, 32.935062])
    
    N_primes = 25  # Basis size (25 prime modes, p_max = 97)
    primes = get_primes(N_primes)
    log_p = np.log(primes)
    sqrt_p = np.sqrt(primes)
    inv_sqrt_p = 1.0 / sqrt_p
    
    num_pts = 450
    t_arr = np.linspace(13.0, 35.0, num_pts)
    
    # 3-body coupling strength parameter
    g3 = 0.35
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: MULTI-BODY EFFECTIVE HAMILTONIAN SPECTRUM AUDIT")
    print(f"  Basis Dimension (N)  : {N_primes} prime modes (p_max = {primes[-1]})")
    print(f"  Spectral Sweep Span  : t in [13.00, 35.00] ({num_pts} points)")
    print(f"  3-Body Coupling (g3) : {g3:.2f}")
    print(f"  Target Riemann Zeros : {list(np.round(target_zeros, 4))}")
    print("=" * 85)

    # -------------------------------------------------------------
    # 2. Tensor Construction: Pairwise & Triad Phase Matrices
    # -------------------------------------------------------------
    print("[*] Precomputing 2-body and 3-body interaction tensors...")
    
    # Pairwise phase difference matrix: diff2[p, q] = ln(p) - ln(q)
    diff2 = log_p[:, None] - log_p[None, :]
    w2 = inv_sqrt_p[:, None] * inv_sqrt_p[None, :]
    
    # Triad phase difference tensor: diff3[p, q, r] = ln(p) + ln(q) - ln(r)
    # Shape: (N, N, N)
    diff3 = log_p[:, None, None] + log_p[None, :, None] - log_p[None, None, :]
    w3_r = inv_sqrt_p[None, None, :]  # 1/sqrt(r)
    
    # Mask out diagonal indices (r != p and r != q)
    mask_r = np.ones((N_primes, N_primes, N_primes), dtype=bool)
    for p_idx in range(N_primes):
        for q_idx in range(N_primes):
            mask_r[p_idx, q_idx, p_idx] = False
            mask_r[p_idx, q_idx, q_idx] = False
            
    # -------------------------------------------------------------
    # 3. Vectorized Spectral Diagonalization over t
    # -------------------------------------------------------------
    print("[*] Assembling and diagonalizing H_eff(t) across spectrum...")
    
    eigvals_h2_only = np.zeros((num_pts, N_primes))
    eigvals_heff = np.zeros((num_pts, N_primes))
    log_det_heff = np.zeros(num_pts)
    min_eig_heff = np.zeros(num_pts)
    spectral_gap = np.zeros(num_pts)
    
    for idx, t in enumerate(t_arr):
        # 1. 2-Body Matrix H2(t)
        H2 = w2 * np.cos(t * diff2)
        # Symmetrize explicitly
        H2 = 0.5 * (H2 + H2.T)
        
        # 2. 3-Body Mean-Field Matrix H3(t)
        # Sum over r: H3_pq = (1/sqrt(pq)) * sum_{r} (1/sqrt(r)) * cos(t * ln(pq/r))
        cos3_tensor = np.cos(t * diff3) * w3_r * mask_r
        H3_unweighted = np.sum(cos3_tensor, axis=2)
        H3 = w2 * H3_unweighted
        H3 = 0.5 * (H3 + H3.T)
        
        # 3. Unified Effective Hamiltonian
        H_eff = H2 + g3 * H3
        
        # Diagonalization (Hermitian / Real Symmetric)
        ev_h2 = np.linalg.eigvalsh(H2)
        ev_eff = np.linalg.eigvalsh(H_eff)
        
        eigvals_h2_only[idx, :] = ev_h2
        eigvals_heff[idx, :] = ev_eff
        
        min_eig_heff[idx] = ev_eff[0]
        spectral_gap[idx] = ev_eff[1] - ev_eff[0]
        
        # Regularized Spectral Log-Determinant: sum ln(|lambda_i| + 1e-6)
        log_det_heff[idx] = np.sum(np.log(np.abs(ev_eff) + 1e-6))

    # Evaluate properties at the first Riemann zero t0
    t0_exact = target_zeros[0]
    idx_t0 = np.argmin(np.abs(t_arr - t0_exact))
    print(f"\n[*] Audit at 1st Riemann Zero t0 = {t0_exact:.6f}:")
    print(f"    - Ground State Eigenvalue lambda_min : {min_eig_heff[idx_t0]:+.6f}")
    print(f"    - Ground State Spectral Gap Delta   : {spectral_gap[idx_t0]:.6f}")
    print(f"    - Spectral Log-Determinant ln|det|  : {log_det_heff[idx_t0]:.4f}")

    # -------------------------------------------------------------
    # 4. Diagnostic Visualization (Python 3.14 Fail-Safe)
    # -------------------------------------------------------------
    print("\n[*] Generating multi-body Hamiltonian diagnostic figure...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9.5))
    
    # Panel (a): Complete Eigenvalue Flow Spectrum lambda_k(t)
    for k in range(N_primes):
        alpha_val = 0.85 if k < 4 else 0.25
        lw_val = 1.6 if k < 4 else 0.8
        color_val = '#1f77b4' if k >= 2 else ('#d62728' if k == 0 else '#2ca02c')
        ax1.plot(t_arr, eigvals_heff[:, k], color=color_val, lw=lw_val, alpha=alpha_val)
        
    for tz in target_zeros:
        ax1.axvline(tz, color='black', linestyle='--', alpha=0.6, lw=1.2)
    ax1.axhline(0.0, color='gray', linestyle=':', lw=1.2)
    ax1.set_title('(a) Multi-Body Hamiltonian Eigenvalue Flow (N=25)', fontweight='bold')
    ax1.set_xlabel('Spectral Parameter t')
    ax1.set_ylabel('Eigenvalues lambda_k(t)')
    ax1.grid(True, alpha=0.3)
    
    # Panel (b): Ground State Level Motion & Zero-Mode Alignment
    ax2.plot(t_arr, min_eig_heff, color='#d62728', lw=2.2, label='Ground State lambda_0(t)')
    for idx_z, tz in enumerate(target_zeros):
        ax2.axvline(tz, color='black', linestyle='--', alpha=0.6, lw=1.2)
        ax2.plot(tz, min_eig_heff[np.argmin(np.abs(t_arr - tz))], 'ro', markersize=6)
    ax2.axhline(0.0, color='gray', linestyle=':', lw=1.2)
    ax2.set_title('(b) Ground State Potential Well & Zero Trapping', fontweight='bold')
    ax2.set_xlabel('Spectral Parameter t')
    ax2.set_ylabel('Ground State Energy lambda_0')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right', fontsize=8.5)
    
    # Panel (c): Spectral Gap Opening (2-Body vs 3-Body Level Repulsion)
    gap_h2 = eigvals_h2_only[:, 1] - eigvals_h2_only[:, 0]
    ax3.plot(t_arr, gap_h2, 'g--', lw=1.6, label='2-Body Gap (g3=0)')
    ax3.plot(t_arr, spectral_gap, 'b-', lw=2.0, label='Full Multi-Body Gap (g3=0.35)')
    for tz in target_zeros:
        ax3.axvline(tz, color='red', linestyle=':', alpha=0.7, lw=1.2)
    ax3.set_title('(c) 3-Body Frustration Enforces Avoided Crossings', fontweight='bold')
    ax3.set_xlabel('Spectral Parameter t')
    ax3.set_ylabel('Spectral Gap lambda_1 - lambda_0')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper right', fontsize=8.5)
    
    # Panel (d): Regularized Spectral Determinant ln|det H_eff|
    ax4.plot(t_arr, log_det_heff, color='#9467bd', lw=2.0, label='Spectral ln|det H_eff(t)|')
    for tz in target_zeros:
        ax4.axvline(tz, color='black', linestyle='--', alpha=0.6, lw=1.2)
    ax4.set_title('(d) Quantum Secular Determinant Dips at Resonances', fontweight='bold')
    ax4.set_xlabel('Spectral Parameter t')
    ax4.set_ylabel('Log-Determinant ln|det H|')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='lower left', fontsize=8.5)
    
    # Bulletproof layout
    plt.subplots_adjust(top=0.92, bottom=0.10, left=0.08, right=0.95, hspace=0.32, wspace=0.28)
    
    out_png = '09_prime_effective_hamiltonian_audit.png'
    plt.savefig(out_png, dpi=200)
    plt.close(fig)
    
    t_elapsed = time.time() - t_start
    print("=" * 85)
    print(f"[+] Hamiltonian audit visual exported: {out_png}")
    print(f"[+] Total execution time: {t_elapsed:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_hamiltonian_audit()