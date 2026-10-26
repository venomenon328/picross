"""Measured unittest execution for CI2-B; fixtures and cleanups count as work."""
import contextlib
import functools
import io
import json
import platform
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

import production_contract as contract

ROOT = Path(__file__).resolve().parents[1]


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


class MeasuredResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []
        self.outcomes = {}

    def startTest(self, test):
        self.started = time.perf_counter()
        super().startTest(test)

    def addSuccess(self, test):
        self.outcomes.setdefault(test.id(), 'success')
        super().addSuccess(test)

    def addSkip(self, test, reason):
        self.outcomes[test.id()] = 'skipped'
        super().addSkip(test, reason)

    def addError(self, test, error):
        self.outcomes[test.id()] = 'error'
        super().addError(test, error)

    def addFailure(self, test, error):
        self.outcomes[test.id()] = 'failure'
        super().addFailure(test, error)

    def addSubTest(self, test, subtest, error):
        if error:
            self.outcomes[test.id()] = 'failure'
        super().addSubTest(test, subtest, error)

    def stopTest(self, test):
        self.rows.append({'id': test.id(), 'status': self.outcomes.get(test.id(), 'incomplete'),
                          'seconds': time.perf_counter() - self.started})
        super().stopTest(test)


class MeasuredSuite(unittest.TestSuite):
    """Keep unittest's class/module fixture semantics and measure them separately."""
    def __init__(self, tests):
        super().__init__(tests)
        self.fixtures = []

    def measure(self, kind, name, callback, *args):
        started = time.perf_counter()
        try:
            return callback(*args)
        finally:
            self.fixtures.append({'kind': kind, 'owner': name,
                                  'seconds': time.perf_counter() - started})

    def _handleClassSetUp(self, test, result):
        if test.__class__ != getattr(result, '_previousTestClass', None):
            return self.measure('class-setup', test.id().rsplit('.', 1)[0],
                                super()._handleClassSetUp, test, result)

    def _tearDownPreviousClass(self, test, result):
        previous = getattr(result, '_previousTestClass', None)
        if previous and (test is None or test.__class__ != previous):
            return self.measure('class-teardown', previous.__module__ + '.' + previous.__qualname__,
                                super()._tearDownPreviousClass, test, result)

    def _handleModuleFixture(self, test, result):
        previous = self._get_previous_module(result)
        if previous != test.__class__.__module__:
            # unittest tears the previous module down inside this method.
            # Charge that nested measured work only to the previous group.
            at = time.perf_counter(); index = len(self.fixtures)
            try:
                return super()._handleModuleFixture(test, result)
            finally:
                nested = sum(r['seconds'] for r in self.fixtures[index:])
                self.fixtures.append({'kind': 'module-setup', 'owner': test.__class__.__module__,
                                      'seconds': max(0, time.perf_counter() - at - nested)})

    def _handleModuleTearDown(self, result):
        previous = self._get_previous_module(result)
        if previous:
            return self.measure('module-teardown', previous, super()._handleModuleTearDown, result)


def run_tests(groups, directory):
    sys.path[:0] = [str(ROOT), str(ROOT / 'tests/puzzle_production')]
    counts = {}
    # Measure complete calls (including aliases imported by tests), without
    # changing behavior or suppressing source validation. No stored outcomes.
    from tools.puzzle_production import target_adapter, content_registry, images
    suite_started = time.perf_counter()
    with contextlib.ExitStack() as stack:
        for module, name in ((target_adapter, 'export'), (target_adapter, 'verify_export'),
                             (content_registry, 'registration'), (content_registry, 'check_checkout'),
                             (images, 'import_image')):
            original = getattr(module, name)
            def counted(*args, _function=original, _key=name, **kwargs):
                counts[_key] = counts.get(_key, 0) + 1
                return _function(*args, **kwargs)
            stack.enter_context(patch.object(module, name, functools.wraps(original)(counted)))
        expected = contract.expected_tests(ROOT, groups)
        modules = [name for g in groups for name in contract.MODULES[g]]
        loader = unittest.TestLoader()
        tests = list(flatten(loader.loadTestsFromNames(modules)))
        actual = [t.id() for t in tests]
        if loader.errors or sorted(actual) != sorted(expected):
            raise ValueError('Actual discovery differs from assigned tests: ' + str(loader.errors))
        suite = MeasuredSuite(tests)
        with (directory / 'tests.log').open('w', encoding='utf-8', newline='\n') as stream:
            result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=MeasuredResult).run(suite)
    elapsed = time.perf_counter() - suite_started
    for row in result.rows:
        row['group'] = expected[row['id']]
    module_groups = {name: g for g in groups for name in contract.MODULES[g]}
    for row in suite.fixtures:
        row['group'] = module_groups[row['owner'].split('.')[0]]
    group_rows = {g: {'tests': sum(r['group'] == g for r in result.rows),
                      'test_seconds': sum(r['seconds'] for r in result.rows if r['group'] == g),
                      'fixture_seconds': sum(r['seconds'] for r in suite.fixtures if r['group'] == g)} for g in groups}
    for row in group_rows.values():
        row['seconds'] = row['test_seconds'] + row['fixture_seconds']
    report = {'format': 'picross-production-tests-v1', 'accepted': result.wasSuccessful()
              and len(result.rows) == len(expected) and all(r['status'] == 'success' for r in result.rows),
              'groups': groups, 'seconds': elapsed, 'group_times': group_rows,
              'tests': result.rows, 'fixtures': suite.fixtures, 'calls': counts,
              'top10': sorted(result.rows, key=lambda r: (-r['seconds'], r['id']))[:10],
              'environment': {'platform': platform.platform(), 'python': sys.version,
                              'pillow': __import__('PIL').__version__,
                              'cache': 'fresh process; existing synthetic rating-input cache; fresh isolated fixture roots'}}
    (directory / 'tests.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report
