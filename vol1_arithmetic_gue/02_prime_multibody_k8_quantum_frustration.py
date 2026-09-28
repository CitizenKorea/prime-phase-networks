#!/usr/bin/env python3
"""
========================================================================================
PRIME PHASE NETWORK: MULTI-BODY (k=2 to k=8) PHASE FRUSTRATION & FREEZE-OUT AUDIT
Module: 02_prime_multibody_k8_quantum_frustration_simulator.py
Description:
  1. Multi-Body Vacuum Energy Condensation E_k(N) -> zeta(k) for k in [2..8]
  2. Phase Frustration Gap Audit min|ln(p1...p_{k-1} / r)| up to 8-body
  3. Exponential Attenuation of Interaction Amplitude V_k ~ O(e^{-alpha*k})
  4. Physical 'Degree-of-Freedom Freeze-out' at k >= 6
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

def run_multibody_k8_simulation():
    t_start = time.time()
    
    # -------------------------------------------------------------
    # 1. Network Configuration
    # -------------------------------------------------------------
    N_full = 45          # Full prime modes for Euler vacuum condensation
    primes_full = get_primes(N_full)
    
    N_comb = 22          # Sub-lattice for exact combinatorial frustration audit
    primes_comb = primes_full[:N_comb]
    log_p_comb = np.log(primes_comb)
    
    k_orders = np.arange(2, 9)  # k = 2, 3, 4, 5, 6, 7, 8
    
    # Exact Mathematical Targets for zeta(k)
    zeta_targets = {
        2: (np.pi ** 2) / 6.0,                 # 1.6449340668
        3: 1.2020569031595942,                 # Apery Constant
        4: (np.pi ** 4) / 90.0,                # 1.0823232337
        5: 1.0369277551433699,                 # zeta(5)
        6: (np.pi ** 6) / 945.0,               # 1.0173430620
        7: 1.0083492773819228,                 # zeta(7)
        8: (np.pi ** 8) / 9450.0               # 1.0040773562
    }
    
    print("=" * 85)
    print("  PRIME PHASE NETWORK: MULTI-BODY (k=2 to k=8) PHASE FRUSTRATION & FREEZE-OUT AUDIT")
    print(f"  Full Prime Modes (Condensation) : N = {N_full} (p_max = {primes_full[-1]})")
    print(f"  Combinatorial Audit Modes       : N = {N_comb} (p_max = {primes_comb[-1]})")
    print("=" * 85)

    # -------------------------------------------------------------
    # 2. Multi-Body Vacuum Condensation E_k(N) across k in [2..8]
    # -------------------------------------------------------------
    print("\n[*] Step 1: Evaluating Multi-Body Vacuum Condensation E_k(N)...")
    E_k_history = {k: np.zeros(N_full) for k in k_orders}
    
    for k in k_orders:
        acc = 1.0
        for idx, p in enumerate(primes_full):
            acc *= 1.0 / (1.0 - (p ** -float(k)))
            E_k_history[k][idx] = acc
            
        final_val = E_k_history[k][-1]
        target = zeta_targets[k]
        defect = final_val - 1.0
        err = abs(final_val - target)
        print(f"    - k = {k}: E_{k}(N={N_full}) = {final_val:.10f} | Target = {target:.10f} | Excite Defect = {defect:.6e}")

    # -------------------------------------------------------------
    # 3. Combinatorial Frustration Gap & Interaction Amplitude Audit
    # -------------------------------------------------------------
    print("\n[*] Step 2: Auditing Combinatorial Frustration & Amplitude Attenuation (k=2..8)...")
    
    min_gaps = []
    mean_amplitudes = []
    total_configs = []
    
    for k in k_orders:
        t_sub = time.time()
        # Combinations of choosing k distinct primes from N_comb
        comb_indices = np.array(list(itertools.combinations(range(N_comb), k)), dtype=np.int32)
        num_c = len(comb_indices)
        total_configs.append(num_c)
        
        # Interaction Amplitude: V_k = 1 / sqrt(p_1 * p_2 * ... * p_k)
        prime_matrix = primes_comb[comb_indices]  # Shape: (num_c, k)
        prod_primes = np.prod(prime_matrix.astype(np.float64), axis=1)
        amp_k = 1.0 / np.sqrt(prod_primes)
        mean_amplitudes.append(np.mean(amp_k))
        
        # Phase Frustration: Delta_k = ln(p_1 * ... * p_{k-1} / p_k)
        log_matrix = log_p_comb[comb_indices]
        # Sum of first (k-1) minus the last (largest) prime
        delta_k = np.sum(log_matrix[:, :-1], axis=1) - log_matrix[:, -1]
        abs_delta_k = np.abs(delta_k)
        min_gap = np.min(abs_delta_k)
        min_gaps.append(min_gap)
        
        dt_k = time.time() - t_sub
        print(f"    - k = {k}: {num_c:>8,d} configs | Mean Amp: {np.mean(amp_k):.4e} | Min Gap: {min_gap:.6f} ({dt_k:.2f} s)")

    # -------------------------------------------------------------
    # 4. Diagnostic Visualization (4-Panel Publication Plot)
    # -------------------------------------------------------------
    print("\n[*] Step 3: Generating Publication Diagnostic Figure...")
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9.5))
    
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(k_orders)))
    
    # Panel (a): Vacuum Energy Condensation E_k(N)
    for idx, k in enumerate(k_orders):
        ax1.plot(range(1, N_full + 1), E_k_history[k], lw=2.0, color=colors[idx], label=rf'$k={k}$ ($\zeta({k})\approx{zeta_targets[k]:.3f}$)')
    ax1.set_title(r'(a) Multi-Body Vacuum Condensation $E_k(N) \to \zeta(k)$', fontweight='bold')
    ax1.set_xlabel('Number of Active Prime Modes $N$')
    ax1.set_ylabel('Condensate Energy $E_k$')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=8.5)
    
    # Panel (b): Vacuum Excitation Defect [zeta(k) - 1] (Freeze-out)
    defects = [zeta_targets[k] - 1.0 for k in k_orders]
    ax2.semilogy(k_orders, defects, 'ro-', lw=2.2, markersize=7, label=r'Excitation Defect $\zeta(k) - 1 \sim 2^{-k}$')
    ax2.axhline(1e-2, color='gray', linestyle=':', label='1% Impact Threshold')
    ax2.axhline(1e-3, color='black', linestyle='--', label='0.1% Freeze-out Threshold')
    ax2.set_title(r'(b) Geometric Degree-of-Freedom Freeze-Out', fontweight='bold')
    ax2.set_xlabel('Interaction Order $k$ (Number of Bodies)')
    ax2.set_ylabel(r'Vacuum Defect $\zeta(k) - 1$ (Log Scale)')
    ax2.set_xticks(k_orders)
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend(loc='upper right', fontsize=9.0)
    
    # Panel (c): Coupling Amplitude Exponential Plunge
    ax3.semilogy(k_orders, mean_amplitudes, 'bs-', lw=2.2, markersize=7, label=r'Mean Coupling Amplitude $\langle V_k \rangle$')
    ax3.set_title(r'(c) Multi-Body Interaction Amplitude Attenuation', fontweight='bold')
    ax3.set_xlabel('Interaction Order $k$')
    ax3.set_ylabel(r'Interaction Amplitude $\langle V_k \rangle$ (Log Scale)')
    ax3.set_xticks(k_orders)
    ax3.grid(True, which="both", alpha=0.3)
    ax3.legend(loc='upper right', fontsize=9.0)
    
    # Panel (d): Arithmetic Frustration Gap Across Orders
    ax4.plot(k_orders, min_gaps, 'md-', lw=2.2, markersize=7, label=r'Minimum Gap $\min|\Delta\Phi_k|$')
    ax4.axhline(0.0, color='red', linestyle='--', lw=1.5, label='Zero-Frustration Line (Forbidden)')
    ax4.set_title(r'(d) Topological Phase Frustration Gap vs. Order $k$', fontweight='bold')
    ax4.set_xlabel('Interaction Order $k$')
    ax4.set_ylabel(r'Min Phase Gap $\min|\Delta\Phi_k|$ (Radians)')
    ax4.set_xticks(k_orders)
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='lower right', fontsize=9.0)
    
    plt.tight_layout()
    out_png = '02_prime_multibody_k8_quantum_frustration.png'
    plt.savefig(out_png, dpi=300)
    plt.close()
    
    t_total = time.time() - t_start
    print("=" * 85)
    print(f"[+] Multi-body audit visual exported: {out_png}")
    print(f"[+] Total execution time: {t_total:.2f} s")
    print("=" * 85 + "\n")

if __name__ == '__main__':
    run_multibody_k8_simulation()