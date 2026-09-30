# OpenModelica candidate qualification report

## 1. Status and intended use

As of September 30, 2026, staged-source and freshly extracted-source headless
qualification passed for the model and configuration in Section 2. A fresh
user-operated OMEdit result also passed all eight numerical checks. The user
supplied voltage-plot and TestStand-diagram images. A separately monitored GUI
repeat passed the same checks and captured actual loaded runtime paths. The
qualification supports the limited source prerelease described here.

This is a software qualification report. It is not an ASTM standard or an
experimental validation of a fuel cell. “Verified” means that a stated check
passed for the identified source and configuration. “Unqualified” means that
the report provides no acceptance evidence; it does not mean that a failure was
observed. “Headless” means execution through the compiler and native executable
without operating the graphical editor.

## 2. Source, configuration, and apparatus

**Table 1 — Qualified configuration**

| Item | Value or boundary |
|---|---|
| Library | FCSys 0.2.6, candidate port revision `om127-native-core.1` |
| Entry point | `FCSys.Assemblies.Cells.Examples.TestStand` |
| Source identity | 161 selected files listed in `SOURCE_MANIFEST.json` |
| Physical configuration | Original wet seven-region TestStand; nitrogen enabled; double-layer storage disabled; original native kinetics and operating conditions |
| Platform/compiler | Windows 64-bit; stock OpenModelica 1.27.0 and bundled clang |
| Libraries actually loaded | Modelica 3.2.3+maint.om; Complex 4.1.0+maint.om; ModelicaServices 4.1.0+maint.om |
| Translation flag | `--generateDynamicJacobian=symbolic` |
| Solver/Jacobian | IDA / `coloredSymbolical` |
| Numerical tolerance | 1 × 10^-6 |
| Nominal simulation interval | 0 to 36180 s, subject to the original oxygen-stop rule |
| Current-density ramp | `2e-6 + 3*clip((t - 180)/36000, 0, 1)` A/cm², with time `t` in seconds |
| Wall-clock bounds | Translation, including loading: 600 s; native build: 120 s; each initialization or transient execution: 40 s |

The actual transitive libraries are stated separately from the declared Modelica
dependency. No result is claimed for substituted dependencies, another operating
system, or another compiler version.

## 3. Method and observed results

The selected files were copied into an isolated source tree and compared with
the retained qualified wet-model files. Fresh flattening compared every function
and the complete model body. Translation, stock compilation, zero-time
initialization, and a transient run were separate stages. A new source archive
was then extracted into a fresh directory and independently translated, built,
and run. Neither build was seeded with old generated C, executables, or results.

**Table 2 — Results measured on September 30, 2026**

| Check or stage | Staged source | Fresh archive extraction |
|---|---|---|
| File identity | All 161 selected files match the reference | All 165 archive files match the archive manifest |
| Load/check | Passed; 8958 equations and 8958 variables; no errors; warnings retained | Dependency/load sequence executed during translation |
| Complete flat comparison | Byte-identical: 949 functions and complete model body; 5,092,838 bytes | Reused complete audit after verifying identical source and configuration |
| Translation elapsed time | 39.674 s | 41.411 s |
| Stock compilation elapsed time | 24.524 s | 22.212 s |
| Zero-time initialization | All 15 initial pressures passed; actual time bounds 0 to 0 s | Same checks passed |
| Transient elapsed time | 1.862 s | 1.848 s |
| Transient criteria | All eight checks passed | All eight checks passed |
| Runtime provenance | Actual executable and loaded modules captured; simulation DLL paths under the pinned OpenModelica installation | Same scope of capture |

The translation template, after the documented package-path substitution, was
identical to the complete script executed in the extracted-source translation.
The revised Git-layout PowerShell recipe has received static review; the entire
interactive recipe has not been rerun from this checkout. No new simulation was
performed during documentation and commit-scope review.

A subsequent user-operated OMEdit execution loaded the same 161 raw files
without source changes. Its communication log records successful loading of
Modelica 3.2.3 and the exact candidate package, followed by successful translation
in 55.004 s. The native command identifies the experiment in Table 1, including
IDA and `coloredSymbolical`. Initialization and simulation logs report success.
The saved result passes all eight checks in Table 3 and has the same SHA-256 as
the reference. This run occurred after cancellation of the active monitor;
the elapsed-time limits were not enforced by that monitor, and its loaded
runtime DLLs were not captured. Headless module captures do not fill that gap.

A separately released repeat closed the GUI runtime-path gap. Translation took
52.123 s; the monitor completed in 107.382 s without a timeout. The simulator
reported 1.53585 s total. The observer captured 45 module paths from the actual
GUI-launched native process: 20 under the pinned OpenModelica installation,
24 under Windows, and the generated executable. All eight result criteria pass
again, with exact reference MAT identity. Module file hashes were collected
after the run; they are not load-time hashes.

During setup, OMEdit saved its complete compiler-options annotation in one
run-local file. The exact substitution was audited: the other 160 selected files
were raw-identical, all equation and function source bytes were unchanged, and
the saved options equaled the complete options already applied in the previous
passing GUI translation. The complete retained flat audit was reused on that
explicit basis; no new flat was generated for this annotation-only repeat.
The repository source retains the original qualified annotation and does not
include that incidental setup edit. Both GUI results support the same declared
equations and applied configuration. Source loading and setup preceded monitor
arming; the monitor bounded the subsequent translation, build and simulation.

The user submitted a plot labeled `load.v (V)` against time in kiloseconds,
ending near 26.6 ks, and a TestStand diagram. The diagram shows environment,
test conditions, the cell, anode and cathode boundary paths, electrical adapters,
load, and ground. Some labels overlap and some router lines are faint. These
images establish the submitted display scope; they do not establish complete
visual fidelity or contain independent source-identity metadata. The association
with the tested model is supported by the user conversation and retained logs.

**Table 3 — Transient acceptance checks and results (both fresh runs)**

| Check | Acceptance criterion | Observed result |
|---|---|---|
| Finite result | All values in the native time-series matrix are finite | Passed; 379 samples |
| Voltage regression | Maximum absolute difference on the shared regular grid ≤ 1 × 10^-4 V | 0 V; 368 shared points |
| Current-density regression | Maximum absolute difference on that grid ≤ 1 × 10^-8 A/cm² | 0 A/cm² |
| Stop time | Absolute difference from the retained reference ≤ 0.1 s | 0 s; stop at 26593.842862336925 s |
| Final cathode catalyst-layer oxygen pressure | Within 0.001 Pa of 12 Pa | 11.99998985333618 Pa |
| Initial pressures | All 15 prescribed pressures satisfy `abs(actual - expected) <= 1e-9*(1 + abs(expected))` in the model's stored units | All 15 passed |
| Current ramp | Maximum absolute error ≤ 1 × 10^-8 A/cm² | Approximately 3.0003 × 10^-12 A/cm² |
| Author termination | Native log contains `There is no more O2` | Present |

The regular comparison grid has a 72.36 s interval; matching times use a tolerance
of 1 × 10^-8 s. The validator requires more than 300 shared points. The reference
is the retained manually configured wet-model GUI result, not a measurement.
Both new MAT files are byte-identical to that reference. Byte identity is an
observation for these runs, not a portability guarantee for every future build.

The oxygen termination is intentional model behavior. These results do not
demonstrate completion of the nominal 36180 s interval. Timing values describe
the observed executions and are not performance requirements for other machines.

## 4. Known problems and unqualified behavior

**Table 4 — Limitations and their practical consequences**

| Status | Item | Consequence or remaining work |
|---|---|---|
| Observed warning | Nitrogen-pressure connectors have one potential variable and no flow variable | Load/check succeeds with connector-balance warnings. Warning-free compilation is not claimed. |
| Observed warning | Real-valued equality tests in species relations are deprecated in non-function contexts | Diagnostics remain. No warning-suppression patch is included. |
| Observed setup limitation in retained GUI work | The OMEdit compiler annotation did not apply the dynamic-Jacobian flag | Enter the flag manually. Automatic open-and-Simulate operation is not qualified. |
| Observed manual GUI behavior | Package load, translation, native execution, saved numerical result, and user-submitted voltage plot and TestStand diagram | The declared manual workflow ran successfully; automatic setup is unqualified. The cancelled monitor did not enforce this run's bounds. |
| Observed GUI runtime provenance | Actual loaded DLL paths from the GUI-launched simulation process | Clean-output monitored repeat captured 20 modules under pinned OpenModelica, 24 under Windows, and the generated executable. Post-run hashes are identified separately from loaded paths. |
| Observed runtime diagnostics | Default linear-solver failures followed by total-pivoting fallback; negative-pressure minimum-constraint diagnostics | Initialization and simulation report success and regression checks pass. Warning-free behavior and physical validity of every internal quantity are not established. |
| Observed compiler diagnostics | State-selection adjustments, alias conflicts, purity diagnostics and initialization defaults, alongside connector and Real-equality warnings | Retained in the qualification logs. A successful trajectory does not resolve these diagnostics. |
| Observed display limitation | Unit-parser errors in GUI result inspection; overlapping labels and faint router lines in the submitted diagram | Complete icon, diagram and unit-conversion fidelity is unqualified. |
| Known missing documentation | `Resources/Source/Python/doc/FCRes.pdf` and `Resources/Source/Python/doc/index.html` | Two legacy FCRes links do not resolve. The percent-encoded poster resource resolves after URI decoding. |
| Unqualified | Other examples, nitrogen-disabled or double-layer configurations, dry variants, other spatial resolutions, parameter sweeps, and broad numerical domains | Shared source changes do not establish support for these configurations. |
| Unqualified | Historical Python, C, and Dymola resource workflows | Retained for source provenance; no general execution promise. |
| Excluded | Experimental oxygen-rate extension and later research changes | No selectable experimental mode is provided. |
| Not established | Empirical accuracy, calibration, and agreement with published fuel-cell measurements | This report establishes software regression only. No interlaboratory precision or measurement-bias claim is made. |

## 5. Evidence identity and availability

The following identifiers refer to locally retained evidence. Raw run directories
are not included in this source commit and do not have public download links.
The identifiers and hashes support audit requests; hashes alone do not replace
access to raw evidence.

| Evidence | Identifier |
|---|---|
| Source audit and staged run | `release-native-core-20260930T064044Z` |
| Fresh extraction and run | `release-native-repro-20260930T065148Z` |
| Fresh user-operated GUI artifacts and submitted display images | `release-manual-omedit-20260930T090719Z` |
| Monitored GUI repeat, numerical validation and actual module capture | `release-gui-dll-20260930T095920Z` |
| Retained GUI source/reference | `normal-library-omedit-20260913T084355Z` |
| Retained mobility control | `normal-library-mobility-fc-normalized-20260913T083410Z` |

Each fresh run retains stage logs, release/claim records, source identities,
native-validation results, and runtime-module observations. Runtime DLL file
hashes were collected after the run; they are not hashes measured at load time.

SHA-256 identifiers:

```text
Complete staged/reference flat:
405c5a43e3f1131bbaf33f917fcb76a4e728931ed2362473f0c37a1a497b2979

Each fresh transient MAT and retained GUI reference:
454a7d9851ef6681e65d445ad6c133dd7862c8d3218d5312dcadacb93988648a

Original 165-file source candidate ZIP:
7ff8663388a8e1761ce5b9c373de32669263263993d3fbb1e0f302999c896255
```

The ZIP identifier refers to the original qualified candidate archive. It does
not identify the revised repository documentation or a final release archive.
That archive remains preserved; final packaging requires a new identifier.

`SOURCE_MANIFEST.json` retains raw qualified-file hashes and sizes. For UTF-8
text covered by Git text attributes it also records LF-normalized hashes. Those attributes can
normalize CRLF during staging. A raw-byte mismatch caused solely by CRLF-to-LF
conversion is distinct from a content change. The normalized field does not
authorize whitespace removal, encoding changes, or other source edits. Fresh GUI
evidence shall identify the exact bytes loaded, and final release review shall
reconcile Git blobs, checkout bytes, and the distributed archive.

## 6. Release acceptance and distribution requirements

R-01: The release reviewer shall retain fresh manual OMEdit load/build/run/plot
evidence for the declared source, toolchain, and settings.

R-02: The release reviewer shall apply the eight criteria in Table 3 to the fresh
GUI result and capture the actual native executable and its loaded runtime paths.

R-03: The release reviewer shall identify the inspected diagram/display scope
and retain unresolved diagnostics beside the result.

R-04: The release reviewer shall verify the final named commit, source manifest,
archive contents, and checksums before publication. The release notes shall state
all remaining unsupported or unverified behavior.

These are project release requirements, not ASTM requirements. Fresh manual
execution, submitted images and the monitored repeat provide the stated
load/build/run/plot, numerical and runtime-path evidence for R-01 through R-03.
The final commit and archive checks required by R-04 belong to distribution
review; the release tag and checksum asset identify that distribution. Complete
visual fidelity, automatic setup and empirical accuracy remain outside scope.

The compact release archive uses the repository layout and Git blob line endings.
Its extraction is checked against the named commit and the manifest's raw or
LF-normalized source hashes. Execution evidence is reused from the qualified
source: the source-content differences are only CRLF/LF conversion, with the
same applied settings. The final Git-layout PowerShell recipe is statically
checked; the entire recipe has not been independently rerun from the final archive.
