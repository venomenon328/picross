"""Passive, exclusive wall-time accounting for real synchronous Playwright calls.

Installed only by the test CLI. No waits, assertions or product timings change.
Nested calls are charged once; counts and state-transfer bytes remain visible.
"""
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
import json
import time


class Meter:
    def __init__(self):
        self.rows = defaultdict(lambda: dict(calls=0, seconds=0.0, bytes=0))
        self.stack = []
        self.started = time.perf_counter()

    @contextmanager
    def measure(self, category):
        frame = [time.perf_counter(), 0.0, category]
        self.stack.append(frame)
        try:
            yield
        finally:
            elapsed = time.perf_counter() - frame[0]
            self.stack.pop()
            if self.stack:
                self.stack[-1][1] += elapsed
            row = self.rows[category]
            row['calls'] += 1
            row['seconds'] += elapsed - frame[1]

    def checkpoint(self, label):
        result = dict(scenario=label, seconds=round(time.perf_counter()-self.started, 6),
                      operations={k: {**v, 'seconds': round(v['seconds'], 6)}
                                  for k, v in sorted(self.rows.items())})
        self.rows.clear()
        self.started = time.perf_counter()
        return result


CURRENT = Meter()


def measured(category):
    def decorate(function):
        @wraps(function)
        def run(*args, **kwargs):
            # Attribute the actual Playwright roundtrip to the semantic caller,
            # not just the Python wrapper overhead. Other nested times remain
            # exclusive (never count the same interval twice).
            if (CURRENT.stack and CURRENT.stack[-1][2] in ('state', 'save_confirmation')
                    and category in ('query', 'wait')):
                return function(*args, **kwargs)
            with CURRENT.measure(category):
                result = function(*args, **kwargs)
            if category == 'state':
                CURRENT.rows[category]['bytes'] += len(json.dumps(result).encode('utf-8'))
            return result
        return run
    return decorate


def install():
    from playwright.sync_api import Page, Mouse, Keyboard, Locator, BrowserType, BrowserContext
    for cls, names, category in (
        (Page, ('evaluate',), 'query'),
        (Page, ('goto', 'reload'), 'navigation'),
        (Page, ('wait_for_function', 'wait_for_timeout'), 'wait'),
        (Page, ('screenshot',), 'screenshot'),
        (Page, ('set_viewport_size',), 'viewport'),
        (Mouse, ('move', 'down', 'up', 'click', 'wheel'), 'input'),
        (Keyboard, ('press',), 'input'),
        (Locator, ('click', 'focus'), 'input'),
        (BrowserType, ('launch_persistent_context',), 'start'),
        (BrowserContext, ('close',), 'shutdown'),
    ):
        for name in names:
            function = getattr(cls, name)
            if not getattr(function, '_picross_timed', False):
                wrapper = measured(category)(function)
                wrapper._picross_timed = True
                setattr(cls, name, wrapper)
