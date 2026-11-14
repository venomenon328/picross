"""Deterministically reproduce the existing runner's stdout/CLI JSON race.

No source edits or weakened assertions. The actual run_tests heartbeat runs;
only its wait is synchronized with a small synthetic CLI capture.
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import patch

from tools import production_tests as runner

capture_started=threading.Event()
activity_printed=threading.Event()
original_print=print


def observed_print(*args,**kwargs):
    original_print(*args,**kwargs)
    if args and str(args[0]).startswith('PRODUCTION ACTIVITY '): activity_printed.set()


class ControlledEvent:
    def __init__(self): self.stop=threading.Event(); self.first=True
    def set(self): self.stop.set()
    def wait(self,seconds):
        if self.first:
            self.first=False
            if not capture_started.wait(10): raise AssertionError('Missing capture')
            return False
        return self.stop.wait(10)


class CliCapture(unittest.TestCase):
    def test_cli_json(self):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):
            capture_started.set()
            self.assertTrue(activity_printed.wait(10))
            print(json.dumps({'status':'expected-cli-json'}))
        self.assertIn('PRODUCTION ACTIVITY ',stream.getvalue())
        json.loads(stream.getvalue())


def main():
    home=Path(__file__).resolve().parent
    output=home/'heartbeat-repro';output.mkdir()
    module=types.ModuleType('m2_heartbeat_probe'); module.CliCapture=CliCapture
    CliCapture.__module__=module.__name__;sys.modules[module.__name__]=module
    expected={module.__name__+'.CliCapture.test_cli_json':'catalog'}
    api=types.SimpleNamespace(Event=ControlledEvent,Thread=threading.Thread)
    with patch.object(runner,'threading',api),patch('builtins.print',observed_print), \
         patch.object(runner.contract,'MODULES',{'catalog':(module.__name__,)}), \
         patch.object(runner.contract,'expected_tests',return_value=expected):
        report=runner.run_tests(['catalog'],output)
    assert not report['accepted'] and report['tests'][0]['status']=='error'
    log=(output/'tests.log').read_text(encoding='utf-8')
    assert 'json.decoder.JSONDecodeError' in log and 'Expecting value' in log
    original_print(log)
    original_print('REPRODUCED: actual unchanged production runner heartbeat contaminates captured CLI stdout JSON')


if __name__=='__main__': main()
