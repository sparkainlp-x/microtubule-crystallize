# Pre-registration — microtubule-crystallize v0.1.0

Written BEFORE the full demo run. These numbers are not moved after
seeing results. If a result misses a bar, it is reported as a miss,
not re-thresholded.

## Frame (fixed)
- Faithful lattice: 13 rows (protofilaments) x 12 columns, N = 156,
  row-major. Row 12 neighbours row 0 across the seam.
- Cell state: +1 = "straight / GTP-like", -1 = "curved / GDP-like".
  Analogy label only. No GTP, no hydrolysis, no mechanics, no neuron,
  no quantum state in this package.
- 12x12 game version: first 12 rows of the same construction,
  declared as a cropped toy, not a real microtubule (12 != 13).
- All randomness from `random.Random(seed)`; seeds are fixed in
  `experiments.py` and `demo.py`. No threshold is tuned on test data:
  the refusing gate is calibrated on validation only, then frozen.

## Bars (good-result criteria)
- Exp 1 crystallization: mean subspace fidelity (k=1) > 0.80 at the
  end of the stream, and mean residue |lag-1 autocorrelation| < 0.20.
- Exp 2 noise: mean recall accuracy > 0.90 at bit-flip p = 0.10 and
  > 0.70 at p = 0.20 (overall, not only among accepted).
- Exp 3 occlusion: recall is reported separately for block, whole-row
  and seam masks; no bar is set for perfect recall under a full mask
  (perfect recall there would be treated as a leak, not a success).
- Exp 4 lattice corruption: corruption is declared lattice-specific
  ONLY if it hurts recall more than the same number of random flips,
  by at least 0.05 accuracy, on average. Otherwise the honest verdict
  is "no lattice-specific effect in this memory" — that negative is
  a result, not a failure to report.
- Exp 5 gate: held-out Youden's J > 0.50.
- Exp 6 calibration: calibration bins track the diagonal within
  sampling error, sampling beats the no-sample baseline net of
  cost, and the label-shuffle control gives a WORSE Brier than the
  unshuffled score with calibration slope near 0. A good score
  under label shuffle would be leakage.
- Exp 7 Kuramoto: order parameter r rises with coupling K, and
  r at K = 0 is near 0. r is classical synchrony only.
- Exp 8 controls: scrambled, shuffled, no-learning and random-pattern
  controls are expected at chance for crystallization/recall. Any
  control matching the headline result falsifies that headline claim.
- Exp 9 game: fragment recall above chance with honest refusals.
  Sonification is display only and is never scored.

## Replication
- Cheap cells (recall, gate, calibration, Kuramoto, controls):
  20 independent repetitions, different seeds, means with spread.
- Crystallization (Exp 1, the expensive cell): 20 repetitions,
  T = 200 noisy samples per repetition, stream flip p = 0.10.
- Demo defaults in `demo.py` are the registered defaults. Tests use
  smaller repetitions for speed and do NOT replace the demo numbers.
