"""Hebbian crystallization: recover a pattern subspace from a
noisy stream. "Crystallization" here means exactly this matrix
computation, nothing else. No crystal is grown.

Stream: samples = true pattern with each bit flipped w.p. p.
W is the running mean of outer(sample, sample), diagonal 0.
Subspace fidelity (k=1): squared cosine between the top
eigenvector of W (power iteration) and the true pattern.
Residue whiteness: after removing the top component from held-out
samples, whiteness = 1 - |lag-1 autocorrelation| of the residual
stream flattened in time order. White residue means the learned
subspace left unstructured noise behind.
"""
import math
import random


def power_top_eigenvector(W, seed=0, max_iter=200, tol=1e-8):
    n = len(W)
    rng = random.Random(seed)
    v = [rng.uniform(-1.0, 1.0) for _ in range(n)]
    norm = math.sqrt(sum(c * c for c in v)) or 1.0
    v = [c / norm for c in v]
    for _ in range(max_iter):
        w = [sum(W[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(c * c for c in w)) or 1.0
        w = [c / norm for c in w]
        change = math.sqrt(sum((a - b) ** 2 for a, b in zip(w, v)))
        # Sign ambiguity: also accept the negated vector as converged.
        change_neg = math.sqrt(sum((a + b) ** 2 for a, b in zip(w, v)))
        v = w
        if min(change, change_neg) < tol:
            break
    return v


def subspace_fidelity_1(v, pattern):
    """Squared cosine between unit top eigenvector and pattern."""
    n = len(pattern)
    pn = math.sqrt(n)
    dot = sum(vi * pi for vi, pi in zip(v, pattern)) / pn
    return dot * dot


def hebbian_stream(pattern, T, flip_p, rng, checkpoints=()):
    """Run a noisy stream, return (W, {t: fidelity}) at checkpoints.
    W is the running mean outer product, diagonal forced to 0."""
    n = len(pattern)
    W = [[0.0] * n for _ in range(n)]
    snaps = {}
    for t in range(1, T + 1):
        sample = [(-c if rng.random() < flip_p else c) for c in pattern]
        # Running mean: W_t = ((t-1) W_{t-1} + outer(s, s)) / t
        for i in range(n):
            si = sample[i]
            Wi = W[i]
            for j in range(n):
                Wi[j] = ((t - 1) * Wi[j] + si * sample[j]) / t
        for i in range(n):
            W[i][i] = 0.0
        if t in checkpoints:
            v = power_top_eigenvector(W, seed=1234)
            snaps[t] = subspace_fidelity_1(v, pattern)
    return W, snaps


def residue_lag1(pattern, v, T, flip_p, rng):
    """Held-out samples, residual = sample - (v.sample) v.
    Return lag-1 autocorrelation of the flattened residual stream
    and the whiteness 1 - |lag1|."""
    residuals = []
    for _ in range(T):
        sample = [(-c if rng.random() < flip_p else c) for c in pattern]
        proj = sum(vi * si for vi, si in zip(v, sample))
        residuals.extend([si - proj * vi for si, vi in zip(sample, v)])
    m = sum(residuals) / len(residuals)
    num = sum((residuals[i] - m) * (residuals[i + 1] - m)
              for i in range(len(residuals) - 1))
    den = sum((c - m) ** 2 for c in residuals)
    lag1 = num / den if den else 0.0
    return lag1, 1.0 - abs(lag1)
