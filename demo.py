"""Demo: run all nine protocol experiments at registered defaults
and print the table. This is the run whose numbers go into README.
"""
import json

from experiments import run_all


def main():
    res = run_all()
    print(json.dumps(res, indent=2, default=str))
    print()
    print("=== Verdicts against PREREG ===")
    e1 = res["exp1_crystallize"]
    print(f"Exp1 fidelity {e1['fidelity_mean']:.3f} (bar 0.80) "
          f"pass={e1['pass_fidelity']}; whiteness {e1['whiteness_mean']:.3f} "
          f"pass={e1['pass_whiteness']}")
    e5 = res["exp5_gate"]
    print(f"Exp5 held-out J {e5['held_out']['J']:.3f} (bar 0.50) "
          f"pass={e5['pass_J']}")
    e4 = res["exp4_corruption"]
    for name, v in e4.items():
        print(f"Exp4 {name}: corruption {v['corruption_accuracy']:.3f} vs "
              f"random same-count {v['random_same_count_mean']:.3f} "
              f"lattice_specific={v['lattice_specific']}")
    e8 = res["exp8_controls"]
    print(f"Exp8 fixed_scrambled fidelity {e8['fixed_scrambled']['fidelity_mean']:.3f}; "
          f"fixed_shuffled {e8['fixed_shuffled']['fidelity_mean']:.3f}; "
          f"per-sample reshuffled {e8['per_sample_reshuffled']['fidelity_mean']:.3f}; "
          f"no-learning recall {e8['no_learning_recall']['accuracy_mean']:.3f}")
    print("Reading: if fixed controls match Exp1, the memory is "
          "generic, not lattice-specific. That is a result.")


if __name__ == "__main__":
    main()
