"""Fresh CI player/technical download, native EXE/PCK and HS pixel evidence."""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

import hf149_windows_probe
import hs186_verify
import p1_preflight as toolchain


def run(head: str, run_id: str, engine: Path, cache: Path, output: Path) -> dict:
    # Existing exact-head download verifies GitHub digests, every retained
    # evidence hash, head/base/checkout/run, EXE/PCK, both actual Windows starts
    # and the HF source/PCK geometry/tooltip/save/restore regression.
    bound = hf149_windows_probe.run(head,run_id,engine,cache,output)
    ci_hs = hs186_verify.verify(output/'technical/selected/hs186')
    native = output/'hs186'
    native.mkdir()
    env = toolchain.isolated_environment(output/'hs-profile','Windows')
    env['HS186_OUTPUT'] = str(native)
    script = hf149_windows_probe.ROOT/'game/tests/hs186_capture.gd'
    command = [str(engine),'--main-pack',str(output/'package/picross-p1.pck'),
               '--script',str(script),'--rendering-driver','opengl3','--audio-driver','Dummy']
    result = subprocess.run(command,env=env,cwd=output/'package',capture_output=True,timeout=300)
    log = result.stdout+result.stderr
    (output/'logs/hs186-pck.log').write_bytes(log)
    text = log.decode('utf-8',errors='replace')
    if result.returncode or 'HS186_NATIVE_OK' not in text or 'ERROR:' in text:
        raise ValueError('HS native PCK probe failed; retained log: '+str(output/'logs/hs186-pck.log'))
    windows_hs = hs186_verify.verify(native)
    measurements = json.loads((native/'hs-native.json').read_text(encoding='utf-8'))
    bound.update(ci_hs=ci_hs,windows_hs=windows_hs,
                 hs_display={k:measurements[k] for k in ('dpi','screen_scale','screen','renderer','font_sha256')},
                 hs_probe_sha256=toolchain.sha256_file(script),
                 hs_original_files={p.name:toolchain.sha256_file(p) for p in sorted(native.iterdir())},
                 owner_acceptance='HS-M01 OPEN',independent_review='HS-R01 OPEN')
    (output/'hs-windows-proof.json').write_text(json.dumps(bound,indent=2)+'\n',encoding='utf-8')
    return bound


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('head','run'): parser.add_argument('--'+name,required=True)
    for name in ('engine','cache-dir','output-dir'): parser.add_argument('--'+name,required=True,type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.head,args.run,args.engine.resolve(),args.cache_dir.resolve(),args.output_dir.resolve()),indent=2))
