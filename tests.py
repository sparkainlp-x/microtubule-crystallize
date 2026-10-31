"""Tests for microtubule-crystallize v0.1.0.
Run: python3 -m unittest tests -v
Small repetitions for speed; demo.py holds the registered numbers.
"""
import random
import unittest

from lattice import (build_pattern, build_pattern_12, seam_agreement,
                     mean_adjacent_agreement, flip_bits, mask_row,
                     seam_shift, row_slip, scrambled, shuffled_states,
                     random_pattern, fragment_top_rows)
from memory import build_W, recall, overlap, accuracy, calibrate_gate
from crystal import (power_top_eigenvector, subspace_fidelity_1,
                     hebbian_stream)
from calibration import revise, brier
from kuramoto import run as kuramoto_run
from experiments import exp3_occlusion, exp7_kuramoto


class TestLattice(unittest.TestCase):
    def test_size_and_seam(self):
        x = build_pattern(42)
        self.assertEqual(len(x), 156)
        self.assertTrue(all(c in (-1, 1) for c in x))
        # Seam neighbours disagree on average; other neighbours agree.
        self.assertLess(seam_agreement(x), mean_adjacent_agreement(x))

    def test_corruptions_change_pattern(self):
        x = build_pattern(42)
        self.assertNotEqual(seam_shift(x), x)
        self.assertNotEqual(row_slip(x), x)
        self.assertEqual(len(scrambled(x, random.Random(1))), 156)
        self.assertEqual(len(shuffled_states(x, random.Random(1))), 156)

    def test_12x12_is_cropped(self):
        x12 = build_pattern_12(42)
        self.assertEqual(len(x12), 144)
        self.assertEqual(x12, build_pattern(42)[:144])


class TestMemory(unittest.TestCase):
    def test_perfect_recall_no_noise(self):
        x = build_pattern(42)
        W = build_W([x])
        self.assertEqual(recall(W, x), x)

    def test_gate_separates_true_from_random(self):
        x = build_pattern(42)
        W = build_W([x])
        rng = random.Random(0)
        true = [overlap(recall(W, flip_bits(x, 0.15, rng)), x)
                for _ in range(30)]
        ctrl = [overlap(recall(W, random_pattern(rng)), x)
                for _ in range(30)]
        tau, j, _, _ = calibrate_gate(true, ctrl)
        self.assertGreater(j, 0.0)
        self.assertTrue(-1.0 <= tau <= 1.0)


class TestCrystal(unittest.TestCase):
    def test_crystallize_recovers_pattern(self):
        x = build_pattern(42)
        rng = random.Random(7)
        W, snaps = hebbian_stream(x, 150, 0.10, rng, checkpoints={150})
        self.assertGreater(snaps[150], 0.5)

    def test_top_eigenvector_is_pattern_like(self):
        x = build_pattern(42)
        W = build_W([x])
        v = power_top_eigenvector(W, seed=1)
        self.assertGreater(subspace_fidelity_1(v, x), 0.9)


class TestCalibrationKuramoto(unittest.TestCase):
    def test_revise_moves_with_overlap(self):
        up = revise(0.5, 0.8, tau=0.4)
        down = revise(0.5, 0.0, tau=0.4)
        self.assertGreater(up, 0.5)
        self.assertLess(down, 0.5)
        self.assertAlmostEqual(brier(0.5, 1), 0.25)

    def test_kuramoto_rises_with_K(self):
        _, r0 = kuramoto_run(K=0.0, steps=500, seed=3)
        _, r3 = kuramoto_run(K=3.0, steps=500, seed=3)
        self.assertGreater(r3, r0)

    def test_occlusion_runs(self):
        out = exp3_occlusion()
        self.assertIn("block_3x4", out)
        self.assertIn("seam_region", out)


class TestGame(unittest.TestCase):
    def test_fragment_is_partial(self):
        x = build_pattern_12(42)
        frag = fragment_top_rows(x, 12, 4)
        self.assertEqual(sum(1 for c in frag if c != 0), 48)


if __name__ == "__main__":
    unittest.main()
