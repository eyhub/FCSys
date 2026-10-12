# Controlled oxygen dependence versus calibration amplitude

**PASS: three fresh actual-component runs show that changing the constant reference exchange current changes current magnitude, but cannot create the candidate's explicit oxygen dependence at fixed temperature and overpotential.** RC-O2KIN-CAL-CONTROL-001 is VERIFIED for this numerical diagnostic only. This does not establish empirical calibration or which law best matches the paper.

## Exact experiment

Run-local `OxygenControls.Matrix`, [source](harness/OxygenControls.mo), extends the unchanged qualified `OxygenLocal.Matrix` with reference-current factors 0.5, 1 and 2. Each execution contains native/default-one, disabled/gamma-zero and candidate/gamma-one actual FCSys oxygen-reduction/electron-transfer sites at three fixed overpotentials: 0.45, 0.49 and 0.53 V. Temperature is 303.78 K; prescribed oxygen partial pressure spans 0.026 to 0.22 atm over 0.1 s, including reference pressure 0.14603527167717584 atm. There are 508 output samples per execution and 27 site/case combinations. The three factors are prespecified sensitivity controls, not fitted calibration values.

The reservoir supplies oxygen while the electron potential adjusts to keep overpotential fixed. Oxygen equilibrium potential therefore changes even in the native arm. This test isolates local kinetics; it does not imply that a whole native cell is oxygen-independent. Reference exchange current is 0.00506 mA before the prescribed scale and temperature correction. The native arm has q=1; the candidate has q=pO2/p_ref. Both use the same finite Butler-Volmer relation and Arrhenius temperature factor.

## Fresh measured results

| Reference-current factor | Current at reference pressure, eta=0.49 V | Native oxygen order | Candidate oxygen order |
|---|---:|---:|---:|
| 0.5 | 42.121460 mA | 0 | 1 |
| 1 | 84.242920 mA | 0 | 1 |
| 2 | 168.485841 mA | 0 | 1 |

At reference pressure, native, disabled and candidate currents coincide for each eta and scale. Across all samples, maximum relative rate error is 2.486e-11 and maximum amplitude-scaling error is 2.486e-11, below the preregistered 1e-8 criterion. Pressure-order error is below 2e-14. Fixed eta/T, oxygen stoichiometry, electron and energy balances, full horizon, positivity, native/disabled equivalence and the oxygen equilibrium-potential shift all pass the original criteria. See the three `results/scale*-verification.json` records and [aggregate evidence](results/controlled-comparison.json).

## Retained coupled evidence and analytic separation

The two already verified `OxygenCoupled.Cell` simulations are reused after rechecking their MAT hashes; no full-cell simulation was repeated. They have ten cathode sections, 50 sccm air, 25 sccm hydrogen, 0.65 V common terminal voltage and a 180 s horizon. The native reaction-current decrease is 1.188%; the candidate decrease is 12.591%. See the [accepted coupled bundle](../oxygen-explicit-binding-20260929T172830Z/README.md).

The following are **analytic constitutive evaluations at the retained candidate endpoint**, not new coupled simulations. All curves share the inlet reference. Holding variables fixed here does not re-solve transport or conservation.

| Inputs allowed to vary across sections | Inlet-to-outlet reaction-current decrease |
|---|---:|
| Oxygen pressure; eta and T held at inlet | 21.6997% |
| Oxygen pressure and eta; T held at inlet | 12.1604% |
| Oxygen pressure and T; eta held at inlet | 22.0860% |
| Oxygen pressure, eta and T at their solved values | 12.5911% |

Solved overpotential rises by about 6.02 mV downstream and partly compensates oxygen loss. Temperature changes have a smaller effect at this operating point. The complete constitutive replay reproduces the retained currents within 1e-8 relative. These effects are nonlinear; the table is a conditional comparison, not an additive or uniquely ordered causal attribution.

![Fresh controls and retained-endpoint analytic replays](figures/controlled-comparison.png)

## Stage evidence and verbatim diagnostics

| Stage | Bound | Actual wall time | Result |
|---|---:|---:|---|
| Check/flatten | 40 s | 4.017 s | PASS |
| Translation | 40 s | 7.289 s | PASS |
| Stock native build | 120 s | 12.478 s | PASS |
| Scale 1 execution | 30 s | 0.368 s | PASS |
| Scale 0.5 execution | 30 s | 0.192 s | PASS |
| Scale 2 execution | 30 s | 0.165 s | PASS |

Pinned OpenModelica 1.27.0, MSL 3.2.3+maint.om and bundled clang. Complete source/flat comparison covers all 58 functions and the entire model body; only the declared scale and nine I0 bindings differ from the qualified parent. Primary audit and single-use release preceded translation. These short declared bounds fit within the standing 600-second test-stand allowance.

Check log: `Check of OxygenControls.Matrix completed successfully.` and `Class OxygenControls.Matrix has 964 equation(s) and 964 variable(s).` Translation returns `true` with an empty error string. Build exits 0 and produces the pinned executable. Each native log contains `solver: euler`, `0 convergence test failures` and `The simulation finished successfully.` Although DASSL was requested, this is the previously qualified algebraic runtime configuration; it does not establish dynamic DASSL behavior. The existing algebraic `newtonFTol=1e-14` is unchanged. Raw diagnostics remain in [logs](logs).

## Interpretation and limits

A constant reference-current amplitude adjustment cannot supply the missing fixed-eta oxygen slope. This distinguishes a constitutive-law difference from that specific calibration gap. Other parameter errors remain possible, and the full-cell response includes equilibrium, transport, temperature and local-potential feedback. Gamma=1 and the chosen reference pressure remain diagnostic choices pending source-matched calibration/validation. No production or immutable upstream source was modified. No Fourier analysis, broad operating sweep or paper-fit claim is included.

Next: [decision packet](NEXT_TASK.md). Traceability: [plan](PLAN.md), [provenance](PROVENANCE.md), [ledger](LEDGER.md).
