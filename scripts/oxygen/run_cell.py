"""Build, simulate and verify the selected complete cell. Windows qualification only."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from run_support import (accept_runtime, accept_translation, confined_new_output,
                         own_session, run_process, sha256, write_json)

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / 'qualification/oxygen/environment.json'


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def inputs():
    names = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard']).decode().split('\0')
    return [{'path': name, 'sha256': sha256(ROOT/name)} for name in sorted(set(names)-{''})]


def environment(home, library_root, lock):
    if sys.platform != 'win32':
        raise ValueError('This recipe is qualified only on Windows x64')
    home, library_root = home.resolve(strict=True), library_root.resolve(strict=True)
    tools = []
    for entry in lock['tools']:
        path = home/entry['path']
        if sha256(path) != entry['sha256']:
            raise ValueError('Unqualified tool identity: ' + str(path))
        tools.append({'path': str(path), 'sha256': entry['sha256']})
    libraries = []
    for entry in lock['libraries']:
        path = library_root/entry['path']
        if sha256(path) != entry['sha256']:
            raise ValueError('Unqualified library entry identity: ' + str(path))
        libraries.append({'name': entry['name'], 'version': entry['version'],
                          'sourceFile': path.as_posix(), 'sha256': entry['sha256']})
    for name, expected in lock['pythonPackages'].items():
        if version(name) != expected:
            raise ValueError(f'{name} {expected} required; found {version(name)}. Nothing was installed.')
    env = os.environ.copy()
    env['OPENMODELICAHOME'] = str(home)
    env['OPENMODELICALIBRARY'] = str(library_root)
    env['PATH'] = str(home/'bin')+os.pathsep+env.get('PATH', '')
    # Avoid redirecting Compile.bat to an unrelated developer toolchain.
    env.pop('OMDEV', None)
    return home, env, tools, libraries


def main():
    if not __debug__:
        raise RuntimeError('Run without -O; numerical assertions are required')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--omc-home', required=True, type=Path, help='Existing qualified OpenModelica installation')
    parser.add_argument('--modelica-library', required=True, type=Path, help='Existing installed Modelica library root')
    parser.add_argument('--output-dir', type=Path, help='New directory below this checkout/build; default is timestamped')
    parser.add_argument('--allow-dirty', action='store_true', help='Exploratory run only; exact dirty source hashes are recorded')
    args = parser.parse_args()
    lock = json.loads(LOCK.read_text())
    home, env, tools, libraries = environment(args.omc_home, args.modelica_library, lock)
    status = git('status', '--porcelain=v1')
    if status and not args.allow_dirty:
        raise ValueError('Commit or isolate source changes first; use --allow-dirty only for an explicit exploratory run')
    out = confined_new_output(ROOT, args.output_dir or ROOT/'build'/('cell-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')))
    head = git('rev-parse', 'HEAD')
    before = inputs()
    # Compiler-wide ownership across relocated clones. Never guess that an existing lock is stale.
    global_lock = Path(tempfile.gettempdir())/('fcsys-omc-'+tools[0]['sha256'][:20]+'.lock')
    description = {'repository': str(ROOT), 'output': str(out), 'head': head}
    with own_session(global_lock, description):
        with own_session(ROOT/'build/omc-owner.lock', description):
            out.mkdir(parents=True, exist_ok=False)
            record = {'status': 'RUNNING', 'model': 'OxygenCoupled.Cell', 'case': 'native1',
                      'repository': str(ROOT), 'sourceCommit': head, 'workingTreeStatus': status,
                      'exploratory': bool(status), 'sources': before, 'tools': tools,
                      'libraries': libraries, 'pythonVersion': sys.version,
                      'pythonPackages': lock['pythonPackages'], 'environmentLockSha256': sha256(LOCK),
                      'boundsSeconds': lock['boundsSeconds'], 'settings': lock['settings'],
                      'processEnvironment': {k: env[k] for k in ['OPENMODELICAHOME', 'OPENMODELICALIBRARY']}}
            write_json(out/'run.json', record, new=True)
            try:
                source_proc = run_process([sys.executable, '-B', str(ROOT/'scripts/verify_oxygen_extraction.py')], out, 'source-check', 30, env)
                source_proc.update(accepted=True, acceptance='Source integrity verifier passed')
                write_json(out/'source-check-process.json', source_proc)
                source_files = ['FCSys 0.2.6/package.mo', 'experimental/oxygen-paperten/KulikovskyDistributed.mo',
                                'experimental/oxygen-paperten/DCell.mo', 'experimental/oxygen-paperten/OxygenCoupled.mo']
                lines = ['getVersion();', 'loadModel(Modelica,{"3.2.3"});getErrorString();']
                lines += [f'loadFile({json.dumps((ROOT/p).as_posix())});getErrorString();' for p in source_files]
                lines += ['print("BEGIN_LIBRARIES\\n");', 'getLoadedLibraries();getErrorString();', 'print("END_LIBRARIES\\n");']
                observed = libraries+[{'name': 'FCSys', 'version': '0.2.6', 'sourceFile': (ROOT/source_files[0]).as_posix()}]
                for item in observed:
                    name = item['name']
                    lines += [f'print("BEGIN_VERSION_{name}\\n");', f'getVersion({name});getSourceFile({name});getErrorString();', f'print("END_VERSION_{name}\\n");']
                lines += ['print("BEGIN_STAGE=translate\\n");', 'translateModel(OxygenCoupled.Cell);getErrorString();', 'print("END_STAGE=translate\\n");']
                (out/'Run.mos').write_text('\n'.join(lines)+'\n', encoding='utf-8')
                proc = run_process([str(home/'bin/omc.exe'), 'Run.mos'], out, 'translate', lock['boundsSeconds']['translate'], env)
                audit = accept_translation(out, observed)
                proc.update(accepted=True, acceptance='Generated grid and ten regular bindings verified; warnings retained')
                write_json(out/'translate-process.json', proc)
                command = [str(Path(os.environ['SystemRoot'])/'System32/cmd.exe'), '/d', '/c',
                           str(home/'share/omc/scripts/Compile.bat'), 'OxygenCoupled.Cell', 'gcc', 'ucrt64', 'parallel', 'dynamic', '4', '0']
                proc = run_process(command, out, 'build', lock['boundsSeconds']['build'], env)
                executable = out/'OxygenCoupled.Cell.exe'
                if not executable.is_file() or not executable.stat().st_size:
                    raise ValueError('Compilation produced no executable')
                build_log = (out/'build-stdout.log').read_text()+(out/'build-stderr.log').read_text()
                if 'error:' in build_log.lower():
                    raise ValueError('C compilation error in log')
                proc.update(accepted=True, executableSha256=sha256(executable))
                write_json(out/'build-process.json', proc)
                command = [str(executable), '-stopTime=180', '-stepSize=0.36', '-s=ida', '-jacobian=coloredNumerical',
                           '-outputFormat=mat', '-lv=LOG_STATS,LOG_EVENTS', '-override=oxygenOrder=1', '-r=native1.mat']
                proc = run_process(command, out, 'simulate', lock['boundsSeconds']['simulate'], env)
                warnings = accept_runtime(out)
                mat = out/'native1.mat'
                proc.update(stage='native1', accepted=True, artifact=mat.name, mat_sha256=sha256(mat),
                            acceptance='Successful execution with reviewed startup warnings; numerical verification separate')
                write_json(out/'simulate-process.json', proc)
                command = [sys.executable, '-B', str(ROOT/'scripts/oxygen/verify_cell.py'), '--case', 'native1',
                           '--mat', str(mat), '--mat-sha256', proc['mat_sha256'], '--process-record', str(out/'simulate-process.json'),
                           '--evidence-kind', 'new-run', '--output', str(out/'verification.json')]
                verify_proc = run_process(command, out, 'verify', 60, env)
                verification = json.loads((out/'verification.json').read_text())
                if verification['status'] != 'PASS' or len(verification['gates']) != 19 or not all(verification['gates'].values()):
                    raise ValueError('Whole-cell numerical acceptance failed')
                verify_proc.update(accepted=True, acceptance='All 19 whole-cell numerical gates passed')
                write_json(out/'verify-process.json', verify_proc)
                if inputs() != before or git('rev-parse', 'HEAD') != head or git('status', '--porcelain=v1') != status:
                    raise ValueError('Repository inputs changed during the run')
                environment(args.omc_home, args.modelica_library, lock)
                write_json(out/'warnings.json', {'translation': audit['warnings'], 'runtime': warnings}, new=True)
                record.update(status='PASS', verification=verification, continuousStates=audit['continuousStates'],
                              gridXYZ=[1,10,1], liveOxygenBindings=10, translationWarnings=len(audit['warnings']),
                              runtimeWarnings=warnings['startupPressureWarnings'], matSha256=proc['mat_sha256'],
                              matchesRetainedMat=proc['mat_sha256']==lock['retainedNative1MatSha256'],
                              limits=lock['limits'])
                write_json(out/'run.json', record)
                manifest = [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in sorted(out.iterdir()) if p.is_file()]
                write_json(out/'artifacts.json', {'files': manifest}, new=True)
                print(json.dumps({'status': 'PASS', 'output': str(out), 'samples': verification['samples'],
                                  'horizon_s': verification['time_bounds_s'], 'current_A': verification['endpoint']['load_current_A'],
                                  'gatesPassed': len(verification['gates'])}), flush=True)
            except BaseException as error:
                record.update(status='FAIL', failure=str(error))
                write_json(out/'run.json', record)
                raise


if __name__ == '__main__':
    try:
        # The local ownership file needs its ignored parent, even on a clean clone.
        (ROOT/'build').mkdir(exist_ok=True)
        main()
    except Exception as error:
        print(f'FCSys cell run failed: {error}', file=sys.stderr)
        sys.exit(1)
