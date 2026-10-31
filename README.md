# Microtubule Crystallize

**A classical toy that crystallizes a microtubule-like lattice —
and, more importantly, checks whether the lattice matters at all.**

Stdlib-only Python, AGPL-3.0-only. Implements all nine experiments
from the 2026-10-27 deep-research protocol, with thresholds fixed
in `PREREG.md` before the demo run.

"Crystallization" here means exactly one thing: Hebbian subspace
learning from a noisy stream. No crystal is grown, no microtubule
is measured, no brain is involved, no quantum state exists in
this package.

## Verified (demo.py, registered defaults, results in `results.json`)

- **Exp 1 crystallization:** subspace fidelity **0.997 ± 0.000** (bar 0.80),
  residue whiteness **0.994 ± 0.004** (bar 0.80). Pass.
- **Exp 2 noise:** recall accuracy **1.000 at p = 0.05, 0.10, 0.20, 0.30**.
  Ceiling, not a discrimination — see DESIGN.md.
- **Exp 3 occlusion:** accuracy **1.000** for block, whole-row and
  seam masks. Ceiling again.
- **Exp 4 lattice corruption: NEGATIVE.** Seam shift, row slip and
  catastrophe front all recall at 1.000, exactly like the same
  number of random flips. `lattice_specific = false` for all three.
  This memory does not use lattice position (see symmetry argument
  in DESIGN.md).
- **Exp 5 refusing gate:** frozen τ\* = **0.372**, held-out
  **TPR 1.00, FPR 0.00, J = 1.00** (bar 0.50). Pass, after a bug fix
  documented in DESIGN.md (first gate version gave J = 0.53 with
  FPR 0.47 — that version is not hidden, it is the reason the
  score definition changed).
- **Exp 6 calibration:** Brier **0.095 ± 0.004** (no-sample baseline
  0.250), bins 0.31 → 0.0 and 0.69 → 1.0, label-shuffle Brier 0.287
  (worse, as it should be). BUT net of sampling cost at the
  registered n = 20, c = 0.01: **-0.295 vs -0.250 no-sample** —
  sampling improves calibration but does not pay for itself at
  that cost. That negative is kept, not tuned away.
- **Exp 7 Kuramoto:** r = **0.20 (K=0), 0.21 (0.2), 0.28 (1.0),
  0.39 (3.0)**. Partial classical synchrony only; r at K=0 is
  finite-size noise (expected ~1/√13 ≈ 0.28).
- **Exp 8 controls:** fixed scrambled fidelity **0.994**, fixed
  shuffled **0.994** — they match Exp 1, proving the memory is
  generic, not lattice-specific. Per-sample reshuffled fidelity
  **0.011** (chance: no bootstrap from pure noise). No-learning
  recall **0.903**, which is exactly the noisy-probe baseline
  (1 − p at p = 0.10); memory adds 0.903 → 1.000.
- **Exp 9 game (12×12 cropped):** top-4-rows and 6×6-corner
  fragments both accepted, score 1.000, accuracy 1.000, τ = 0.361.
  Sonification pitches are display only, never scored.

## Run it

```bash
python3 -m unittest tests -v   # 11 tests
python3 demo.py                # all nine experiments
```

## Honest limits — what this does NOT give

- No biology: no tubulin, no real microtubule, no cell.
- No consciousness, no quantum computation, no objective
  reduction, no medical application. Penrose's 2020 Nobel was
  for black holes, not Orch OR; Orch OR remains contested.
- No lattice-specific memory claim: Exp 4 and Exp 8 falsify it
  for outer-product memory. A lattice-aware memory (local
  lateral coupling) would be a different, future package.
- Single-pattern recall at N = 156 is at ceiling; raw accuracy
  alone discriminates nothing here. The discriminating results
  are the gate, the calibration cost, and the controls.

Full account in `DESIGN.md`. Pre-registration in `PREREG.md`.

## Credits

Authors: Jean-François Brisson and Mun Seok Lee.
Lee, author of the Digital to Wave paradigm (Zenodo 21947036,
21947108), is the inspiration friend behind this wave and
membrane work. This package's code was built by Brisson with
AI assistance, except where a file already credits Lee as
author; the joint credit here is for the shared programme,
not a claim that Lee wrote every line of this package.
