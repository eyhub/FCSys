# OpenModelica port: changes from upstream

## 1. Scope and source basis

This document describes candidate revision `om127-native-core.1` of FCSys 0.2.6
for OpenModelica 1.27.0 on Windows 64-bit. The comparison base is
[kdavies4/FCSys](https://github.com/kdavies4/FCSys), commit
`cb4b17f34313b9d8f2d4223d5365684b4dc1ab65`. The fork is
[eyhub/FCSys](https://github.com/eyhub/FCSys).

The selected library contains 16 Modelica files, `package.order`, and 144 resource
files. Twelve Modelica files differ from upstream. The other four Modelica files,
`package.order`, and all 144 resource files are unchanged. The complete selected
library matches the retained September 13 wet-TestStand package. This preparation
does not combine later research variants with that package.

The qualified model is `FCSys.Assemblies.Cells.Examples.TestStand`: the original
wet seven-region configuration, with nitrogen enabled and double-layer storage
disabled. [QUALIFICATION.md](QUALIFICATION.md) gives the evidence and its limits.

## 2. File-by-file changes

Paths in Table 1 are relative to `FCSys 0.2.6/`. The table explains purpose and
scope; the source diff defines the actual change. A successful integrated run
does not establish that every changed branch works for every configuration.

**Table 1 — Selected source changes**

| File | Change and purpose | Evidence boundary |
|---|---|---|
| `Assemblies.mo` | Makes electronic, phase, and thermal connections explicit; declares thermal junctions and typed boundary buses; conditions nitrogen measurement on nitrogen inclusion; adds OMEdit setup annotations. | Verified in the selected wet TestStand. Other topologies and the nitrogen-disabled branch are not qualified. Annotations alone do not establish automatic OMEdit setup. |
| `Characteristics.mo` | Makes coefficient matrices explicit; expands thermodynamic polynomial evaluations and derivatives into finite sums; supplies an explicit entropy inverse for the sulfonate species; converts binary mobility for FC units while preserving the original LH reference. | Wet regression and a retained 12-row mobility control, maximum relative error approximately 4.622 × 10^-15. This is not a general proof over all temperatures, pressures, or species. |
| `Chemistry.mo` | Makes reaction-connector translational cardinality an explicit parameter, including redeclarations. | Wet integration. The `ElectronTransfer` equations and original constant reference-current closure remain unchanged. No oxygen-dependent rate multiplier is added. |
| `Conditions.mo` | Introduces explicit input, output, and phase buses and an electronic-current connector; makes enumeration selection and router types explicit. | Wet integration; other adapters and absent-phase combinations remain unqualified. |
| `Connectors.mo` | Adds fixed-cardinality exchange nodes, signal inputs, and a node that calculates common velocity from species weights. | Common-signal source lineage and wet integration; no universal connector-equivalence claim. |
| `Phases.mo` | Declares typed gas, graphite, ionomer, and liquid boundary buses; conditions fixed exchange nodes on included species; connects gas weight and weighted-velocity outputs; makes geometry indexing explicit. | Wet integration. Later dry gas–liquid specialization is excluded. |
| `Regions.mo` | Converts explicitly between enumeration and integer indices in area calculations; uses typed face buses. | Selected geometry only; other spatial dimensions are not qualified. |
| `Species.mo` | Scalarizes diagnostic and stream sums; makes axis mappings explicit; specializes one-axis momentum equations; reorients momentum and heat-transfer equations using stable reciprocal upwind factors; gives explicit ideal-gas and selected entropy relations; replaces zero-resistance heat-transfer products with temperature equalities; exposes common-velocity weights. | Wet trajectory and all 15 prescribed initial pressures. The zero-resistance rewrite has positive-inventory scope. Zero inventory, arbitrary transport dimensions, and broader numerical domains are not established. |
| `Subregions.mo` | Adds typed phase face buses and conditional fixed exchange nodes. | Selected wet configuration; later dry exchange specialization is excluded. |
| `Units.mo` | Uses standard function icons and selects the FC base-unit representation instead of LH. | The mobility conversion in `Characteristics.mo` is part of the same selection. Mixing this file with an unconverted LH-based variant is outside qualification. |
| `Utilities.mo` | Replaces the external C charge parser with Modelica code; makes enumeration conversions explicit; replaces nested polynomial expressions with finite sums; adds a stable `1/(1 + exp(x))` evaluation and its derivative. | Wet integration. Arbitrary formula-string parser equivalence and all polynomial domains are not freshly qualified. The reciprocal factor avoids direct evaluation of a large positive exponential; it does not guarantee convergence. |
| `package.mo` | Changes the declared Modelica dependency from 3.2.1 to 3.2.3. | Actual dependency versions are recorded in QUALIFICATION.md. |

## 3. Interpretation of equation and unit changes

The port includes structural, numerical, initialization, and unit-representation
changes. Describing all changes as syntax fixes would understate their scope.
No new physical mechanism or parameter calibration was introduced when assembling
this candidate. This statement does not assert universal equivalence between all
upstream and ported equations.

The FC unit selection and mobility conversion are retained together. The
conversion preserves the original LH mobility reference; it is not a fit to the
desired voltage curve. Native reaction kinetics, the operating conditions,
current ramp, and oxygen-stop rule remain the selected baseline.

## 4. Changes intentionally excluded

The candidate excludes later residual-enthalpy domain guards, the cancellation-safe
negative `asinh` branch, dry gas–liquid weighting, externally supplied shear
closures, normalized shear options, oxygen-entropy trial continuation, and the
oxygen-dependent reaction-rate extension. Their evidence concerns different
research configurations. They require separate review and wet-model regression
before a backport can be qualified. No default-native/experimental selector is
included.

## 5. Repository and archive contents

The Git checkout retains upstream history, license notices, legacy resources,
and the existing generated `help/` tree. Those inherited files are not new port
additions. The compact source ZIP omits 790 generated help files; it retains all
144 resource files, including the 11 PDFs already distributed upstream. The
upstream help may describe pre-port behavior and is not evidence of current
OpenModelica support.

New support material is limited to the setup instructions, this change record,
the qualification report, the translation template, and the source manifest.
The root README points readers to those instructions. Generated C, executables,
DLLs, MAT results, raw run directories, research harnesses, thesis documents,
private configuration, and newly acquired research papers are not commit inputs.

Original authorship and license notices remain in the source and resources.
The port does not imply endorsement by the upstream authors. Source identity
and Git line-ending treatment are described in `SOURCE_MANIFEST.json` and
QUALIFICATION.md.
