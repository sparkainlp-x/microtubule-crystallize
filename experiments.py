"""All nine protocol experiments, with pre-registered bars in PREREG.md.

Returns plain dicts of means and spreads. No result is hidden:
controls that match the headline are reported as matching, and
the verdict for lattice-specific claims follows from them.
"""
import math
import random

from lattice import (ROWS, COLS, N, build_pattern, build_pattern_12,
                     flip_bits, count_flips, random_flips, mask_block,
                     mask_row, mask_seam, seam_shift, row_slip,
                     catastrophe_front, scrambled, shuffled_states,
                     random_pattern, fragment_top_rows, fragment_corner,
                     sonify_row_overlaps)
from memory import (build_W, recall, overlap, accuracy, score_probe,
                    calibrate_gate, roc_table)
from crystal import (power_top_eigenvector, subspace_fidelity_1,
                     hebbian_stream, residue_lag1)
from calibration import revise, brier, net_score, calibration_bins
from kuramoto import run as kuramoto_run


def mean_std(vals):
    m = sum(vals) / len(vals) if vals else 0.0
    var = sum((v - m) ** 2 for v in vals) / len(vals) if vals else 0.0
    return m, math.sqrt(var)


def exp1_crystallize(reps=20, T=200, flip_p=0.10, seed_base=1000):
    fids, whites = [], []
    for r in range(reps):
        rng = random.Random(seed_base + r)
        pat = build_pattern(42)
        W, snaps = hebbian_stream(pat, T, flip_p, rng,
                                  checkpoints={T})
        v = power_top_eigenvector(W, seed=1234)
        lag1, white = residue_lag1(pat, v, 100, flip_p,
                                   random.Random(seed_base + 10000 + r))
        fids.append(snaps[T])
        whites.append(white)
    fm, fs = mean_std(fids)
    wm, ws = mean_std(whites)
    return {"fidelity_mean": fm, "fidelity_std": fs,
            "whiteness_mean": wm, "whiteness_std": ws,
            "fidelity_bar": 0.80, "whiteness_bar": 0.80,
            "pass_fidelity": fm > 0.80, "pass_whiteness": wm > 0.80}


def exp2_noise(reps=20, seed_base=2000):
    pat = build_pattern(42)
    W = build_W([pat])
    out = {}
    for p in (0.05, 0.10, 0.20, 0.30):
        accs = []
        for r in range(reps):
            rng = random.Random(seed_base + r)
            for _ in range(5):
                probe = flip_bits(pat, p, rng)
                accs.append(accuracy(recall(W, probe), pat))
        m, s = mean_std(accs)
        out[str(p)] = {"accuracy_mean": m, "accuracy_std": s}
    return out


def exp3_occlusion():
    pat = build_pattern(42)
    W = build_W([pat])
    masks = {"block_3x4": mask_block(pat),
             "whole_row_6": mask_row(pat, 6),
             "seam_region": mask_seam(pat)}
    out = {}
    for name, probe in masks.items():
        rec = recall(W, probe)
        out[name] = {"accuracy": accuracy(rec, pat),
                     "overlap": overlap(rec, pat),
                     "masked_cells": sum(1 for c in probe if c == 0)}
    return out


def exp4_corruption(reps=20, seed_base=4000):
    pat = build_pattern(42)
    W = build_W([pat])
    corruptions = {"seam_shift": seam_shift(pat),
                   "row_slip_3": row_slip(pat, 6, 3),
                   "catastrophe_front": catastrophe_front(pat)}
    out = {}
    for name, corr in corruptions.items():
        k = count_flips(pat, corr)
        corr_acc = accuracy(recall(W, corr), pat)
        rand_accs = []
        for r in range(reps):
            rng = random.Random(seed_base + r)
            rand = random_flips(pat, k, rng)
            rand_accs.append(accuracy(recall(W, rand), pat))
        m, s = mean_std(rand_accs)
        out[name] = {"flipped_cells": k, "corruption_accuracy": corr_acc,
                     "random_same_count_mean": m,
                     "random_same_count_std": s,
                     "corruption_hurts_more_by": m - corr_acc,
                     "lattice_specific": (m - corr_acc) >= 0.05}
    return out


def _gate_probe_sets(pat, W, n_true, n_ctrl, seed):
    rng = random.Random(seed)
    true_scores, ctrl_scores = [], []
    for _ in range(n_true):
        probe = flip_bits(pat, 0.15, rng)
        true_scores.append(score_probe(W, probe, pat))
    for _ in range(n_ctrl // 2):
        true_scores_ctrl = score_probe(W, random_pattern(rng), pat)
        ctrl_scores.append(true_scores_ctrl)
    for _ in range(n_ctrl - n_ctrl // 2):
        ctrl_scores.append(score_probe(W, shuffled_states(pat, rng), pat))
    return true_scores, ctrl_scores


def exp5_gate(seed_base=5000):
    pat = build_pattern(42)
    W = build_W([pat])
    vt, vc = _gate_probe_sets(pat, W, 100, 100, seed_base)
    tau, j_val, tpr_val, fpr_val = calibrate_gate(vt, vc)
    tt, tc = _gate_probe_sets(pat, W, 100, 100, seed_base + 1)
    held = roc_table(tt, tc, tau)
    return {"validation": {"tau": tau, "J": j_val, "TPR": tpr_val,
                           "FPR": fpr_val},
            "held_out": held, "pass_J": held["J"] > 0.50}


def exp6_calibration(reps=20, n=20, c=0.01, seed_base=6000):
    pat = build_pattern(42)
    pairs, shuffled_pairs = [], []
    briers, nets, base_briers = [], [], []
    for r in range(reps):
        rng = random.Random(seed_base + r)
        for y in (1, 0):
            overlaps = []
            for _ in range(n):
                if y == 1:
                    sample = flip_bits(pat, 0.10, rng)
                    overlaps.append(overlap(sample, pat))
                else:
                    sample = random_pattern(rng)
                    overlaps.append(overlap(sample, pat))
            mean_ov = sum(overlaps) / len(overlaps)
            p1 = revise(0.5, mean_ov, tau=0.4, alpha=2.0)
            pairs.append((p1, y))
            briers.append(brier(p1, y))
            nets.append(net_score(p1, y, n, c))
            base_briers.append(brier(0.5, y))
    # Label shuffle: same predictions, shuffled truths.
    ys = [y for _, y in pairs]
    rng = random.Random(999)
    rng.shuffle(ys)
    shuffled_brier = sum(brier(p, y) for (p, _), y in zip(pairs, ys)) / len(pairs)
    bm, bs = mean_std(briers)
    nm, ns = mean_std(nets)
    return {"brier_mean": bm, "brier_std": bs,
            "net_mean": nm, "net_std": ns,
            "no_sample_brier_mean": sum(base_briers) / len(base_briers),
            "label_shuffle_brier": shuffled_brier,
            "calibration_bins": calibration_bins(pairs),
            "beats_no_sample_net": nm > -sum(base_briers) / len(base_briers)}


def exp7_kuramoto(reps=20, seed_base=7000):
    out = {}
    for K in (0.0, 0.2, 1.0, 3.0):
        rs = []
        for r in range(reps):
            _, order = kuramoto_run(K=K, steps=1000, seed=seed_base + r)
            rs.append(order)
        m, s = mean_std(rs)
        out[str(K)] = {"r_mean": m, "r_std": s}
    return out


def exp8_controls(reps=5, T=100, flip_p=0.10, seed_base=8000):
    pat = build_pattern(42)
    # Fixed scrambled / fixed shuffled: a NEW fixed pattern, learned
    # from its own noisy stream. If these match the headline, the
    # memory is generic, not lattice-specific — that is the verdict.
    fixed = {}
    for name, target in (("fixed_scrambled", scrambled(pat, random.Random(11))),
                         ("fixed_shuffled", shuffled_states(pat, random.Random(12)))):
        fids = []
        for r in range(reps):
            rng = random.Random(seed_base + r)
            W, snaps = hebbian_stream(target, T, flip_p, rng,
                                      checkpoints={T})
            fids.append(snaps[T])
        m, s = mean_std(fids)
        fixed[name] = {"fidelity_mean": m, "fidelity_std": s}
    # Per-sample reshuffled: no fixed pattern exists in the stream.
    # Fidelity here must stay near chance, or the metric is leaky.
    reshuffled_fids = []
    for r in range(reps):
        rng = random.Random(seed_base + 100 + r)
        # Stream of freshly shuffled patterns: build W manually.
        n = len(pat)
        W = [[0.0] * n for _ in range(n)]
        for t in range(1, T + 1):
            sample = shuffled_states(pat, rng)
            sample = flip_bits(sample, flip_p, rng)
            for i in range(n):
                si = sample[i]
                Wi = W[i]
                for j in range(n):
                    Wi[j] = ((t - 1) * Wi[j] + si * sample[j]) / t
        for i in range(n):
            W[i][i] = 0.0
        v = power_top_eigenvector(W, seed=1234)
        reshuffled_fids.append(subspace_fidelity_1(v, pat))
    rm, rs = mean_std(reshuffled_fids)
    # No-learning: W = 0, recall keeps probe, overlap with pattern
    # is chance.
    W0 = [[0.0] * len(pat) for _ in range(len(pat))]
    rng = random.Random(5)
    nolearn = [accuracy(recall(W0, flip_bits(pat, 0.10, rng)), pat)
               for _ in range(20)]
    nm, ns = mean_std(nolearn)
    fixed["per_sample_reshuffled"] = {"fidelity_mean": rm,
                                      "fidelity_std": rs}
    fixed["no_learning_recall"] = {"accuracy_mean": nm,
                                   "accuracy_std": ns}
    return fixed


def exp9_game(seed_base=9000):
    pat = build_pattern_12(42)
    W = build_W([pat])
    # Gate calibrated for the 12x12 board, validation only.
    rng = random.Random(seed_base)
    vt = [score_probe(W, fragment_top_rows(pat, 12, 4), pat)
          for _ in range(20)]
    # True fragment probes are noisy fragments; control = random.
    vt = []
    vc = []
    for _ in range(50):
        frag = fragment_top_rows(pat, 12, 4)
        frag = [(-c if (c != 0 and rng.random() < 0.10) else c)
                for c in frag]
        vt.append(score_probe(W, frag, pat))
        vc.append(score_probe(W, random_pattern(rng)[:144], pat))
    tau, _, _, _ = calibrate_gate(vt, vc)
    results = {}
    for name, frag in (("top_4_rows", fragment_top_rows(pat, 12, 4)),
                       ("corner_6x6", fragment_corner(pat, 12, 6, 6))):
        rec = recall(W, frag)
        sc = overlap(rec, pat)
        results[name] = {"accepted": sc >= tau, "score": sc,
                         "accuracy": accuracy(rec, pat), "tau": tau}
        rows_ov = []
        for r in range(12):
            seg_rec = rec[r * COLS:(r + 1) * COLS]
            seg_true = pat[r * COLS:(r + 1) * COLS]
            rows_ov.append(overlap(seg_rec, seg_true))
        results[name]["sonification_pitches_hz"] = sonify_row_overlaps(rows_ov)
    results["note"] = ("Sonification pitches are display only, "
                       "never scored.")
    return results


def run_all():
    return {
        "exp1_crystallize": exp1_crystallize(),
        "exp2_noise": exp2_noise(),
        "exp3_occlusion": exp3_occlusion(),
        "exp4_corruption": exp4_corruption(),
        "exp5_gate": exp5_gate(),
        "exp6_calibration": exp6_calibration(),
        "exp7_kuramoto": exp7_kuramoto(),
        "exp8_controls": exp8_controls(),
        "exp9_game": exp9_game(),
    }
