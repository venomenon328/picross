"""Bind fresh CI EXE/PCK downloads to native Windows HN original evidence."""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

import hf149_windows_probe
import p1_preflight as toolchain
from vs2_windows_probe import direct_start


def run(head: str, run_id: str, engine: Path, cache: Path, output: Path) -> dict:
    bound = hf149_windows_probe.run(head, run_id, engine, cache, output)
    native = output / 'hn192'
    native.mkdir()
    env = toolchain.isolated_environment(output / 'hn-profile', 'Windows')
    env['HN192_OUTPUT'] = str(native)
    script = hf149_windows_probe.ROOT / 'game/tests/hn192_probe.gd'
    command = [str(engine), '--main-pack', str(output / 'package/picross-p1.pck'),
               '--script', str(script), '--rendering-driver', 'opengl3',
               '--audio-driver', 'Dummy', '--', '--p1-capture']
    result = subprocess.run(command, env=env, cwd=output / 'package',
                            capture_output=True, timeout=300)
    log = result.stdout + result.stderr
    (output / 'logs/hn192-pck.log').write_bytes(log)
    if result.returncode or b'HN192_NATIVE_OK' not in log or b'ERROR:' in log:
        raise ValueError('HN PCK probe failed; original log retained')
    measurements = json.loads((native / 'hn-native.json').read_text(encoding='utf-8'))
    if measurements['os'] != 'Windows' or measurements['failures']:
        raise ValueError('Successful native Windows measurements required')
    starts = []
    for name in ('picross-p1.exe', 'picross-p1.console.exe'):
        starts.append(direct_start(output / 'package' / name, env, output,
                                   'hn-direct-' + name))
    bound.update(windows_hn=measurements, direct_starts=starts,
                 hn_probe_sha256=toolchain.sha256_file(script),
                 hn_original_files={p.name: toolchain.sha256_file(p) for p in sorted(native.iterdir())},
                 owner_acceptance='HN-M01 open; automation is not owner acceptance',
                 independent_review='HN-R01 open')
    (output / 'hn-windows-proof.json').write_text(json.dumps(bound, indent=2)+'\n', encoding='utf-8')
    return bound


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('head', 'run'): parser.add_argument('--'+name, required=True)
    for name in ('engine', 'cache-dir', 'output-dir'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.head, args.run, args.engine.resolve(),
                         args.cache_dir.resolve(), args.output_dir.resolve()), indent=2))
