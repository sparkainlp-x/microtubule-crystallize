"""Kuramoto phase layer: 13 oscillators, one per protofilament row.

d theta_i / dt = omega_i + (K / N) sum_j sin(theta_j - theta_i)
Order parameter r = |mean exp(i theta)|, 0 <= r <= 1.

r is CLASSICAL synchrony produced by coupling. It is not quantum
coherence, not superposition, not entanglement, not collapse.
A high r proves the coupling was strong, nothing more. This module
cannot test any Orch OR collapse claim, even in principle: it has
no Planck scale, no gravitational self-energy, no non-computability.
"""
import math
import random


def order_parameter(thetas):
    s = sum(complex(math.cos(t), math.sin(t)) for t in thetas)
    return abs(s) / len(thetas)


def run(n=13, K=1.0, steps=2000, dt=0.01, base_hz=7.0, spread=0.5,
        seed=42, coupled_weights=None):
    """coupled_weights: optional NxN matrix; if given, the coupling
    term for i is sum_j w_ij sin(theta_j - theta_i) / N instead of
    the uniform K term. Unused in the headline K sweep."""
    rng = random.Random(seed)
    theta = [rng.uniform(0.0, 2.0 * math.pi) for _ in range(n)]
    omega = [2.0 * math.pi * rng.gauss(base_hz, spread) for _ in range(n)]
    for _ in range(steps):
        new = []
        for i in range(n):
            if coupled_weights is None:
                c = (K / n) * sum(math.sin(theta[j] - theta[i])
                                  for j in range(n))
            else:
                c = (1.0 / n) * sum(coupled_weights[i][j] *
                                    math.sin(theta[j] - theta[i])
                                    for j in range(n))
            new.append(theta[i] + dt * (omega[i] + c))
        theta = new
    return theta, order_parameter(theta)
