"""The selected mixed-catalog consumer guarantees also hold for Source v2."""
from copy import deepcopy
import shutil
import unittest

from tests.puzzle_production import test_background_consumers as consumers
from tests.puzzle_production.background_change_fixtures import create_work
from tools.puzzle_production import catalog_background_change as change
from tools.puzzle_production import background_request as requests, catalog_background as background
from tools.puzzle_production import catalog_analysis as analysis, catalog_added_history as dates
from tools.puzzle_production import catalog_method as method, catalog_reveal as reveal
from tools.puzzle_production.contract import InvalidInput, load_json, write_json
from tools.puzzle_production.za1_fixtures import difficulty_for_export


class BackgroundChangeConsumerTests(consumers.BackgroundConsumerTests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        owner = unittest.TestCase(); cls.addClassCleanup(owner.doCleanups)
        root = cls.background.case.root
        work = create_work(owner, cls.background.checkout, root, 'bg-consumer')
        bundle = root / 'consumer-background-plan'
        change.plan(cls.background.checkout, work.record_path, bundle)
        change.adopt(cls.background.checkout, bundle)

    # Explicit methods keep the contract's AST inventory equal to discovery;
    # the shared assertions run against this class's actual v2 checkout.
    def test_rating_added_method_and_sync_keep_background_and_bind_new_plan_generations(self):
        super().test_rating_added_method_and_sync_keep_background_and_bind_new_plan_generations()

    def test_legacy_raster_update_and_reveal_adoption_keep_background_bytes(self):
        super().test_legacy_raster_update_and_reveal_adoption_keep_background_bytes()

    def test_background_target_requires_authorized_current_bindings(self):
        super().test_background_target_requires_authorized_current_bindings()
        work = create_work(self, self.checkout, self.root, 'blocked-legacy-background')
        request = deepcopy(work.request)
        original_directory = requests.directory(request)
        request['puzzle_id'] = self.legacy_id
        request['target']['source']['file'] = background.path(self.legacy_id)
        directory = requests.directory(request)
        for stored in request['background'].values():
            if isinstance(stored, dict):
                stored['root'] = directory + stored['root'][len(original_directory):]
        shutil.copytree(self.checkout / original_directory, self.checkout / directory)
        write_json(self.checkout / requests.record_name(request), request)
        index = load_json(self.checkout / requests.INDEX)
        index['entries'].append(requests.index_row(request))
        write_json(self.checkout / requests.INDEX, index)
        before = consumers.snapshot(self.checkout)
        with self.assertRaisesRegex(InvalidInput, 'Legacy retrofit is unsupported'):
            change.plan(self.checkout, requests.record_name(request), self.root / 'blocked-legacy-plan')
        self.assertEqual(before, consumers.snapshot(self.checkout))

    def test_capability_byte_change_stales_each_new_saved_plan_before_writes(self):
        super().test_capability_byte_change_stales_each_new_saved_plan_before_writes()

    def test_saved_v2_reveal_plan_allows_false_capability_but_never_acquires_background_scope(self):
        super().test_saved_v2_reveal_plan_allows_false_capability_but_never_acquires_background_scope()

    def test_new_source_revision_stales_all_existing_metadata_and_legacy_reveal_plans(self):
        commit = self.git_commit()
        report = self.root / 'source-stale-rating'
        analysis.preview(self.checkout, report, 'source-stale-rating', commit, ids=[self.background_id],
                         checked_inputs={self.background_id: difficulty_for_export(self.background.export)})
        added = self.root / 'source-stale-added.json'
        write_json(added, dates.plan(self.checkout, 'source-stale-added', commit))
        activation = method.plan(self.checkout, method.OLD, method.NEW, method.method_hash(method.NEW))
        request, _ = self.request(self.legacy_id, 'source-stale-reveal')
        reveal_plan = self.root / 'source-stale-reveal-plan'
        reveal.plan(self.checkout, [self.legacy_id], request, reveal_plan)
        work = create_work(self, self.checkout, self.root, 'bg-consumer-next', 'none')
        background_plan = self.root / 'changed-background-plan'
        change.plan(self.checkout, work.record_path, background_plan)
        change.adopt(self.checkout, background_plan)
        before = consumers.snapshot(self.checkout)
        for action in (lambda: analysis.adopt(self.checkout, report, apply=True),
                       lambda: dates.adopt(self.checkout, added, apply=True),
                       lambda: method.adopt(self.checkout, activation),
                       lambda: reveal.adopt(self.checkout, reveal_plan)):
            with self.assertRaises(InvalidInput): action()
            self.assertEqual(before, consumers.snapshot(self.checkout))


if __name__ == '__main__': unittest.main()
