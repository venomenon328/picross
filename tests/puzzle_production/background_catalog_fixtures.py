"""Real, small test-only v6 production for HP-I1b1 catalog tests."""
from types import SimpleNamespace

from tests.puzzle_production.test_background_export import BackgroundExportTests
from tools.puzzle_production import catalog_background as background
from tools.puzzle_production.contract import write_json
from tools.puzzle_production.za1_fixtures import isolated_checkout, rated_registration


def prepare(testcase, choice="selected", *, registered=False):
    case = BackgroundExportTests()
    case.setUp()
    testcase.addCleanup(case.doCleanups)
    source, fixture, handoff, archive, approval = case.early(choice)
    export, manifest = case.export(archive, approval)
    checkout = isolated_checkout(case.root / "checkout")
    write_json(checkout / background.CAPABILITY, {"format": background.CAPABILITY_FORMAT,
        "runtime_format": background.RUNTIME_FORMAT, "profile_id": "picross-background-png2304-v1", "enabled": True})
    result = SimpleNamespace(case=case, source=source, fixture=fixture, handoff=handoff, archive=archive,
                             approval=approval, export=export, manifest=manifest, checkout=checkout)
    if registered:
        result.registration = rated_registration(export, checkout, apply=True)
    return result
