# Verified coupled oxygen-law diagnostic

**The binding repair and both full-cell cases pass.** At50sccm air and0.65V,
adding the live linear oxygen prefactor changes inlet-to-outlet cathode reaction
current fall from1.188% to12.591%.
The extra fall is11.403 percentage points,
exceeding the preregistered5-point material-shaping threshold. This is numerical
verification of a run-local law at one point, not empirical calibration/validation.

## What was fixed

The nested array-comprehension modifier in our candidate wrapper produced ten
initialization-only qO2 assignments. Consequently the rejected candidate used its
startup factor throughout the simulation. Removing input from the qO2 declaration
and compiling with exponent default1 were separately insufficient; their rejected
translation outputs remain retained, with no full-cell build/native attempts.

A small positive decaying-state fixture reproduced the frozen nested modifier;
explicit array-literal bindings and explicit equations tracked changing states.
The successful cell repair replaces the nested modifier with ten explicit scalar
bindings in [OxygenCoupled.mo](harness/OxygenCoupled.mo). Its physical expressions
are unchanged: qO2=(local catalyst-layer oxygen pressure/p_ref)^gamma. All825
flattened functions and the entire model body match the preceding attempt after
exactly these ten algebraically identical substitutions. Generated regular
assignments now exist for every cathode factor, confirmed in
[generated-code audit](results/generated-qO2-audit.json) and
[live-binding evidence](results/live-binding-evidence.json).

The tested variant retains ordinary Real qO2 and default gamma1 from the prior
controls; neither change alone fixed the problem. Gamma0 and gamma1 now both work
through runtime override on the same executable, which rules out the prior
runtime-switch assumption as a sufficient explanation of the observed failure.
This is evidence for this exact source form and pinned compiler, not a general
claim about all array comprehensions or other versions.

## Exact physical test

Run-local `OxygenCoupled.Cell` extends the exact stable-asinh `DCell.PaperTen`:
ten dry sections,50sccm air,25sccm H2,0.65V common terminal voltage,303.15K
ambient,RH1 and atmospheric outlet; inherited geometry, transport, conservation,
alpha0.5, E_A0.75V and reference exchange-current density remain fixed.
p_ref=0.14603527167717584atm is the original native inlet diagnostic reference,
not fitted or recovered empirical calibration. Thermodynamic oxygen coupling is
retained in both cases. Production/upstream sources are untouched.

| Endpoint quantity | Native control gamma0 | Live oxygen factor gamma1 |
|---|---:|---:|
| Reaction-current inlet-to-outlet fall | 1.1878% | 12.5911% |
| Contact-current inlet-to-outlet fall | 1.0766% | 11.5132% |
| Catalyst-layer oxygen-pressure fall | 24.1638% | 21.6997% |
| Total current | 0.815186A | 0.778020A |
| Oxygen utilization | 29.9975% | 28.6298% |

Total current changes by-4.5592%. This is a
fixed-terminal-voltage comparison; currents and oxygen utilization are not
matched. Reaction and terminal-contact profiles differ because the cell permits
current redistribution; both are reported, rather than treating them as identical.

![Verified comparison](figures/coupled-comparison.png)

## Why compensation is partial

In the candidate, local cathode overpotential rises from
0.488387 to0.494406V along the
channel, even though all contacts share0.65V terminal voltage. The native
local overpotential instead falls by0.602mV. Common terminal voltage therefore
does not prescribe the same reaction-site overpotential in each section.

The candidate's exact spatial logarithmic current ratio decomposes as:

| Contribution to ln(I_out/I_in) | Value |
|---|---:|
| Reference I0 ratio | 0.00000000 |
| Explicit local oxygen factor | -0.24461844 |
| Arrhenius temperature term | -0.00733351 |
| Finite-BV overpotential/temperature term | 0.11737836 |

The positive BV contribution partly offsets the negative oxygen contribution;
it does not erase it. This algebraic decomposition closes within3e-15.
For the candidate's spatial Delta-g contributions, water=-0.797mV,
proton=-6.440mV, oxygen=+1.556mV and electron=-0.339mV sum to-6.019mV,
equal to the negative overpotential change. These are contributions in the
solved model, not independent causal interventions. Full section-by-section
cross-run changes are in [comparison.json](results/comparison.json).

## Numerical acceptance

Both native runs reached0-180s with504 saved samples. Unchanged IDA,
coloredNumerical Jacobian and tolerance1e-6 were used. Every registered
boundary, pressure-factor, rate, ORR, oxygen/electron/energy balance, KCL,
contact-voltage and settling gate passes. The worst rate residual is1.34e-15,
oxygen balance/feed3.36e-16, ORR closure5.56e-16V and KCL3.34e-16A.
Maximum144-180s contact-current drift is3.65e-10, below1e-4.
The repaired gamma0 agrees with the saved native endpoint: maximum reaction-current
relative difference4.70e-13 and contact-current difference1.41e-11.

| Execution stage | Wall seconds | Verbatim result / acceptance |
|---|---:|---|
| Check/flatten | 58.247 | `Check of OxygenCoupled.Cell completed successfully.` |
| Translation | 314.787 | `true`; no errors; below600s |
| Stock build | 108.765 | Exit0; executable exists; below240s |
| Gamma0 | 43.138 | `The simulation finished successfully.`; all gates PASS |
| Gamma1 | 48.527 | `The simulation finished successfully.`; all gates PASS |

Native limits were180s wall each. Startup electron-pressure minimum warnings,
also present in the retained native parent, remain in both logs; these runs are
not described as warning-free. The component test's tighter algebraic tolerance
was not applied to the full-cell runs. The chart and comparison used only the
verified MAT files, and the rendered chart was visually inspected.

`RC-O2KIN-COUPLED-001` is **VERIFIED for this one-point numerical diagnostic**.
The broader empirical oxygen-kinetics requirement gains no validation. Reference
pressure/amplitude calibration, paper-temperature transfer, both experimental
Tafel regimes, wet-cell behavior and Figure8 agreement remain outside this result.

## Evidence and retained attempts

- [Plan and unchanged acceptance criteria](PLAN.md)
- [Whole-source/flat audit](results/integrator-cell-audit.json)
- [Native0 verification](results/cell-native0-verification.json), [native1 verification](results/cell-native1-verification.json)
- [CSV values](results/comparison.csv), [SVG chart](figures/coupled-comparison.svg)
- [Small binding reproducer](../oxygen-binding-probe-20260929T172630Z/README.md)
- [Rejected ordinary-variable change](../oxygen-variable-binding-20260929T170713Z/README.md)
- [Rejected default-one change](../oxygen-live-default-20260929T171630Z/README.md)
- [Original failed candidate](../oxygen-coupled-point-20260929T145329Z/README.md)
- [Next decision](NEXT_TASK.md), [provenance](PROVENANCE.md), [ledger](LEDGER.md)
