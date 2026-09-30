# FCSys 0.2.6 — OpenModelica native-core candidate

Port revision: `om127-native-core.1`. Source candidate for OpenModelica 1.27.0,
Windows 64-bit. No stable-release or full-library compatibility claim.

The qualified example is `FCSys.Assemblies.Cells.Examples.TestStand`, using the
original wet seven-region configuration, nitrogen enabled, double layer disabled,
original current ramp and oxygen-stop rule. Native kinetics are preserved. This
package includes no experimental oxygen-rate option or dry research harness.

Read [PORT_CHANGES.md](PORT_CHANGES.md) for the file-by-file changes and
[QUALIFICATION.md](QUALIFICATION.md) for acceptance criteria, measured results,
known problems, and unqualified behavior. The historical upstream installation
instructions do not replace this port-specific setup.

## Prerequisites

An existing stock OpenModelica 1.27.0 64-bit installation, bundled clang, and
installed libraries Modelica 3.2.3+maint.om, Complex 4.1.0+maint.om and
ModelicaServices 4.1.0+maint.om. No installer or private runtime is included.
The library declares Modelica 3.2.3; the transitive dependencies actually observed
in qualification are 4.1.0. Do not silently substitute other versions.

## Headless example (PowerShell)

Use a clean checkout. Set `$omRoot` to your OpenModelica installation and
`$libraryRoot` to the directory containing the installed dependency folders.
Run these commands from the repository root. The existing upstream Git rules
ignore `build/`. Keep `build/om127-teststand` new: generated runtime assets must
stay together. Select a different new child of `build/` for another attempt;
do not reuse or delete an earlier run merely to repeat this recipe.

```powershell
$omRoot = 'C:/Program Files/OpenModelica1.27.0-64bit'
$libraryRoot = Join-Path $env:APPDATA '.openmodelica/libraries'
$env:OPENMODELICAHOME = $omRoot
$env:OPENMODELICALIBRARY = $libraryRoot
$env:PATH = "$omRoot/bin;$omRoot/tools/msys/ucrt64/bin;$env:PATH"
$packageFile = (Resolve-Path -LiteralPath './FCSys 0.2.6/package.mo').Path.Replace('\', '/')
$template = Get-Content -Raw -LiteralPath './openmodelica/Translate.mos.in'
New-Item -ItemType Directory -Path './build/om127-teststand' -ErrorAction Stop | Out-Null
[IO.File]::WriteAllText((Join-Path (Get-Location) 'build/om127-teststand/Translate.mos'), $template.Replace('@PACKAGE_FILE@', $packageFile), [Text.UTF8Encoding]::new($false))
Set-Location './build/om127-teststand'
& "$omRoot/bin/omc.exe" './Translate.mos'
# Require true after BEGIN_STAGE=translate, END_STAGE=translate, and no Error.
& "$omRoot/share/omc/scripts/Compile.bat" 'FCSys.Assemblies.Cells.Examples.TestStand' gcc ucrt64 parallel dynamic 4 0
if ($LASTEXITCODE -ne 0) { throw 'Native compilation failed; inspect the build output.' }
& './FCSys.Assemblies.Cells.Examples.TestStand.exe' '-s=ida' '-jacobian=coloredSymbolical' '-lv=LOG_STATS,LOG_SOLVER' '-r=TestStand_res.mat'
```

Keep the native experiment settings: nominal 0..36180 seconds, tolerance 1e-6.
The successful original trajectory terminates near 26593.842862 seconds when
cathode catalyst-layer oxygen reaches 12 Pa. Its termination message is
`There is no more O2`; this is the author-defined stop, not completion of 36180 s.
The retained reference has 379 finite samples and final voltage about 0.354121112 V.
Qualification uses separate bounds: translation 600 s including loading, stock
build 120 s, native trajectory 40 s wall time. The manual commands above do not
enforce those wall-clock limits automatically.

## Manual OMEdit result

The identical library ran in OMEdit with one manual setting:
Simulation Setup > Translation Flags > Additional Translation Flags:
`--generateDynamicJacobian=symbolic`. Solver settings: IDA / coloredSymbolical.
The compiler annotation alone was not effective in the retained editor workflow.
A fresh user-operated candidate run passed all eight numerical checks and
produced a byte-identical reference result. The submitted voltage plot and
TestStand diagram were inspected. A monitored repeat captured the actual runtime
and solver DLL paths under the pinned OpenModelica installation and passed the
same numerical checks. Complete icon/diagram fidelity is unqualified.

## Known limits

Load/check emits nitrogen-signal connector-balance and deprecated Real-equality
warnings. OMEdit unit parsing errors remain. Runtime logs report linear-solver
fallback and negative-pressure constraint diagnostics despite successful
initialization and simulation. See the qualification report for their scope.
Two legacy FCRes documentation links target unshipped `FCRes.pdf` and `index.html`.
All historical Python/Dymola resource scripts are retained as source resources,
without an OpenModelica execution claim. Other examples, parameter sweeps,
platforms, compiler versions, physical calibration and empirical agreement remain
unqualified. Later dry-phase, shear, entropy-continuation and stable-asinh changes
were deliberately not merged into this byte-identical wet baseline.

## Authorship and notices

FCSys 0.2.6 is the upstream work of its credited authors, Hawaii Natural Energy
Institute and Georgia Tech Research Corporation. This port is not an upstream
endorsement. Original notices and license text remain in `FCSys 0.2.6/package.mo`,
`FCSys 0.2.6/UsersGuide.mo`, `FCSys 0.2.6/Resources/Documentation/ModelicaLicense2.html` and
`FCSys 0.2.6/Resources/Source/Python/LICENSE.txt`, including their additional conditions.
`SOURCE_MANIFEST.json` records the 161 qualified library files, with raw-byte
hashes and an additional LF-normalized hash for identified text files. Git line-ending
conversion can change raw hashes; see QUALIFICATION.md before comparing a new
checkout with the raw manifest. Preserve notices when redistributing.

## Release gate

The staged and extracted source passed headless checks. Fresh manual OMEdit
execution, saved-result checks, submitted display evidence and actual GUI-process
DLL capture pass for the declared scope. Release archives are identified by the
named tag and checksum asset; no stable or full-library support is claimed.
This checkout matches the 161 raw qualified library file hashes. Its revised
Git-layout PowerShell recipe is statically checked; the entire recipe has not
been independently rerun from this checkout.
