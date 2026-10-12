# Matched native/candidate polarization comparison

**Physical/numerical comparison: PASS.** Maximum absolute current difference at matched voltage is **22.94%**. Does not pass the provisional 5% current-deviation screen; do not qualify/package it as a curve-preserving option on this evidence.

The engineering distinction matters: a smooth, conservative polarization curve may still differ substantially from the original. The 5% screen was proposed before execution as a provisional regression tolerance, not supplied by a paper or silently fitted after seeing results. Both curve shape and numerical deviations are reported below so the packaging decision is reviewable.

## Exact scope and conditions

Original means the native FCSys electron-transfer law in the same qualified dry ten-section `DCell.PaperTen` harness. Candidate means the unchanged run-local `OxygenCoupled.Cell` with gamma1 and local catalyst-layer oxygen factor q=pO2/p_ref. The fixed reference pressure is0.14603527167717584atm at every voltage/flow. There is no amplitude fitting, voltage-dependent renormalization or temperature change between arms.

Both use ten0.22cm2 sections (2.2cm2 total), 110mm flow length,2mm effective width,303.15K ambient, RH1, atmospheric outlet,25sccm H2 and20/50sccm air, with sccm reference298.15K/100000Pa. They share material/kinetic parameters and180s simulation horizon, IDA/coloredNumerical and1e-6 tolerance. Actual saved boundary and I0/E_A/alpha values are compared at every pair. This is neither the differently configured author's50cm2 TestStand curve nor experimental validation.

Reuse eight accepted native MAT trajectories and the accepted candidate50sccm/0.65V point, all rehashed. Run seven missing candidate points plus two native-equivalence controls. The new controls at20sccm/0.75V and50sccm/0.55V match the retained native endpoints; maximum relative error among their compared channels is below6e-11. Thus the disabled option preserves the native response at these additional controls.

## Polarization results

| Air (sccm) | Voltage (V) | Original current (A) | Candidate current (A) | Change |
|---:|---:|---:|---:|---:|
| 20 | 0.65 | 0.719500 | 0.554448 | -22.94% |
| 20 | 0.70 | 0.454667 | 0.398606 | -12.33% |
| 20 | 0.75 | 0.256284 | 0.256898 | +0.24% |
| 50 | 0.55 | 1.621785 | 1.326068 | -18.23% |
| 50 | 0.60 | 1.195890 | 1.051592 | -12.07% |
| 50 | 0.65 | 0.815186 | 0.778020 | -4.56% |
| 50 | 0.70 | 0.506159 | 0.528635 | +4.44% |
| 50 | 0.75 | 0.281586 | 0.323571 | +14.91% |

![Matched polarization curves](figures/polarization-comparison.png)

The registered total-current monotonicity gate requires current to increase as imposed voltage decreases for each airflow. Its result is recorded independently from the closeness screen in [machine-readable comparison](results/polarization-comparison.json). [CSV](results/polarization-comparison.csv) retains the pointwise differences.

At matched current, piecewise-linear interpolation of the accepted points gives:

- 20 sccm: maximum interpolated voltage difference 31.162 mV within shared current range.
- 50 sccm: maximum interpolated voltage difference 34.717 mV within shared current range.

These are interpolated numerical comparisons within overlap only; there is no extrapolation. Sparse sampling cannot rule out every feature between points.

## Verification and stage evidence

| Case | Wall seconds | Process | Scientific gates |
|---|---:|---|---|
| g0-air20-V750-r2 | 110.603 | PASS | PASS |
| g0-air50-V550 | 120.898 | PASS | PASS |
| g1-air50-V750 | 53.719 | PASS | PASS |
| g1-air50-V700 | 49.747 | PASS | PASS |
| g1-air50-V600 | 55.030 | PASS | PASS |
| g1-air50-V550 | 59.090 | PASS | PASS |
| g1-air20-V750 | 49.954 | PASS | PASS |
| g1-air20-V700 | 54.168 | PASS | PASS |
| g1-air20-V650 | 47.249 | PASS | PASS |


Every scientific PASS requires finite complete0..180s data, fixed boundaries, positive oxygen/current, live pressure multiplier, rate-law identity, oxygen stoichiometry, electron/energy/oxygen conservation, ORR chemical-potential closure, KCL/contact voltage and late-window settling. Acceptance limits are unchanged from the prior coupled verifier: rate/q/stoichiometry/ORR1e-8, electron/energy1e-10A/W, KCL/oxygen1e-7, contact voltage1e-8V and relative settling1e-4. Runtime bounds are180wall seconds per call. Parent source/flat/build qualification and actual executable are reused; no new translation/build is claimed.

One earlier launch failed before simulation because the runtime copy omitted binary sparsity files: `Could not open sparsity pattern file OxygenCoupled.Cell_JacLSJac0.bin.` The failed attempt is retained. A fresh primary release copied all2773 generated binary assets alongside the identical executable/XML/JSON. It changed no equations or solver settings. The corrected executions report `The initialization finished successfully without homotopy method.` and `The simulation finished successfully.` Raw startup negative-electron-pressure minimum warnings are retained, as in the accepted parent; these are not warning-free runs. See [correction](RUNTIME_CORRECTION.md), [provenance](PROVENANCE.md) and per-case logs/results.

## Decision and limits

Does not pass the provisional 5% current-deviation screen; do not qualify/package it as a curve-preserving option on this evidence. Numerical stability/conservation and closeness to the native curve are separate conclusions. A larger shift does not by itself prove the oxygen-aware law is physically wrong, because the original is also a model rather than measured truth. It does show that the current fixed-reference candidate is not a negligible perturbation throughout this range.

Native-qualified domain is0.55..0.75V at50sccm and0.65..0.75V at20sccm. Retained lower-voltage native trajectories terminated on oxygen depletion or timed out, so they cannot establish a matched polarization reference. No open-circuit, full limiting-current range, wet-cell, thermal sweep, transient-control or empirical-fit claim follows. No production source/default was changed. RC-O2KIN-POLARIZATION-001 records this exact comparison; broader empirical oxygen-law acceptance is unchanged.

See [next-task packet](NEXT_TASK.md), [preregistered plan](PLAN.md) and [ledger](LEDGER.md).
