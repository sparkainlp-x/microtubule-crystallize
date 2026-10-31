# DESIGN.md — microtubule-crystallize v0.1.0

## What "maximum scientific outcomes" means here

The strongest outcome a synthetic toy can honestly deliver is not
a biology claim. It is a citable, reproducible, falsifiable
software/methods record: a pre-registered protocol, all nine
experiments run, controls that can kill the headline claim, and
negatives kept in the record. That is what this package is built
to be. If Jean pushes it to GitHub and archives it on Zenodo,
it becomes citable; until then it is a local package, not a
publication, and no DOI exists for it.

## Modules

- `lattice.py` — 13x12 pattern, seam (row 12 vs row 0 inverted),
  lateral-agreement measures, defects (seam shift, row slip,
  catastrophe front), occlusions, scrambled/shuffled controls,
  12x12 cropped version, fragment helpers, sonification mapping
  (display only).
- `memory.py` — outer-product W (diagonal 0), one-step recall,
  overlap/accuracy (overall, never only among accepted),
  Youden's-J gate calibration on validation, frozen on test.
- `crystal.py` — running-mean Hebbian stream, power-iteration
  top eigenvector, subspace fidelity (k=1), residue whiteness
  (1 - |lag-1 autocorrelation|).
- `calibration.py` — fixed logistic revise (alpha = 2.0),
  Brier, net = -Brier - c*n, calibration bins.
- `kuramoto.py` — 13 oscillators, one per row, order parameter r.
- `experiments.py` — Exp 1–9 at registered defaults.

## The symmetry argument (why Exp 4 is negative by construction)

Outer-product memory is permutation-equivariant: permute the
cells of the pattern and the probe the same way, and W, recall
and accuracy permute with them, unchanged. Lattice position —
which row is the seam, which row slipped — cannot affect recall
accuracy except through the NUMBER of cells changed. Seam shift
(20 cells), row slip (6 cells) and catastrophe front (24 cells)
therefore recall exactly like the same number of random flips,
as measured (1.000 vs 1.000 in all three cases). This is not a
failure of the experiment; it is the experiment doing its job:
it proves that THIS memory cannot test lattice structure.

A memory that could test lattice structure would need to use
lateral neighbours explicitly — e.g. a local smoothing term
(lambda * lateral neighbours added to the recall field), or
row-wise Kuramoto coupling where the seam pair has a different
coupling sign. That is a different package, proposed here, not
built here, and not claimed here.

## Bug found by the results, fixed, not hidden

First gate version scored a probe by overlap(recall, stored).
For a single stored pattern, one-step recall snaps to +-stored,
so every probe — including random ones — scored +-1, giving
validation J = 0.38, held-out J = 0.53 with FPR 0.47. That is a
broken gate, not a passing one. The fix, in `memory.score_probe`,
scores overlap(probe, recall): the gate sees overlap magnitude
only, as in refusing-membrane. After the fix, held-out J = 1.00
(TPR 1.00, FPR 0.00, tau = 0.372). The first version's numbers
are kept in this file so the fix is auditable.

## Ceiling effects, reported not smoothed over

Single-pattern recall at N = 156 is extremely robust: the recall
field for a cell is a sum over 155 neighbours, so 20–24 corrupted
cells, 12 masked cells, or 30% bit flips do not flip a sign.
Exp 2 and Exp 3 at 1.000 are therefore ceiling measurements.
They do not discriminate models, and they are not presented as
if they do. Discrimination in this package comes from Exp 5
(gate), Exp 6 (calibration cost), Exp 7 (Kuramoto trend) and
Exp 8 (controls).

## Calibration cost, kept negative

Brier improves 0.250 -> 0.095 with sampling, but at the
registered n = 20, c = 0.01 the cost (0.20) exceeds the gain
(0.155), so net -0.295 is worse than no-sample -0.250. This
does not mean calibration failed; it means sampling at that
volume and price is not worth it. Fewer samples, a lower cost,
or a sharper revise rule would be a new, separately registered
experiment, not a silent edit to this one.

## Controls, read correctly

- Fixed scrambled / fixed shuffled patterns are NEW fixed
  patterns. Learning them from their own noisy streams works
  exactly as well as learning the lattice pattern (0.994 vs
  0.997). That matches the symmetry argument: the learner is
  generic.
- Per-sample reshuffled streams have no fixed pattern to learn:
  fidelity 0.011, chance. No bootstrap from pure noise.
- No-learning recall 0.903 is not "chance 0.5"; it is the
  noisy-probe baseline 1 - p. The memory's contribution is
  0.903 -> 1.000, and that is how it must be quoted.

## Falsified / not claimed

- Falsified for this memory: lattice-specific recall,
  lattice-specific crystallization, sampling-pays-at-registered-cost.
- Not claimed, ever, from this package: microtubule biology,
  quantum coherence, objective reduction, consciousness,
  non-computability, medicine, or any validation of Orch OR.
  The exclusion list from the deep-research report applies in
  full (report.md section 5, "would NOT count as evidence").

## Reproduction

```bash
python3 -m unittest tests -v   # 11 tests, fast (small reps)
python3 demo.py                # registered defaults, ~25 s
```

Seeds are fixed in `experiments.py`. `results.json` is the
demo output of the run that produced the README numbers.
