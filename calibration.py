"""Commit-sample-revise calibration game (Crystallize scoring).

Player commits p0 = probability the stream contains the pattern.
Samples n fresh noisy copies at cost c per sample (fixed in advance).
Revises by a fixed logistic rule (alpha fixed in advance, never
tuned on test data). Scores Brier (p1 - y)^2, net = -Brier - c*n.
Calibration bins are reported separately from sharpness: Brier
alone hides whether a player is sharp-but-miscalibrated.
This scores calibration about the TOY stream, not any biology.
"""
import math


def logit(p):
    p = min(max(p, 1e-6), 1.0 - 1e-6)
    return math.log(p / (1.0 - p))


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def revise(p0, mean_overlap, tau, alpha=2.0):
    """Fixed logistic update. mean_overlap is the mean probe overlap
    over the sampled copies; tau is the frozen gate threshold."""
    return sigmoid(logit(p0) + alpha * (mean_overlap - tau))


def brier(p, y):
    return (p - y) ** 2


def net_score(p1, y, n, c):
    return -brier(p1, y) - c * n


def calibration_bins(pairs, nbins=5):
    """pairs = [(p_predicted, y_true)]. Returns per-bin
    (mean_p, observed_freq, count)."""
    out = []
    for b in range(nbins):
        lo, hi = b / nbins, (b + 1) / nbins
        sel = [(p, y) for p, y in pairs
               if lo <= p < hi or (b == nbins - 1 and p == 1.0)]
        if sel:
            out.append((sum(p for p, _ in sel) / len(sel),
                        sum(y for _, y in sel) / len(sel), len(sel)))
        else:
            out.append((None, None, 0))
    return out
