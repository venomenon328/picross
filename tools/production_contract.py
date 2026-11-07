"""CI2-B: explicit Fachtest ownership, shared by selection, runner and gate.

No production catalog is inspected. Source consumers are audited against Python
imports by the fast tool tests. Unknown paths retain conservative full coverage.
"""
import ast
import json
from pathlib import Path

GROUPS = ('solver', 'images', 'adapter', 'catalog')
MODULES = {
    'solver': ('test_analysis', 'test_benchmark', 'test_cli', 'test_color_cli',
               'test_color_core', 'test_color_lines', 'test_core', 'test_diagnosis',
               'test_difficulty_rating', 'test_lines', 'test_paired',
               'test_sd2_analysis', 'test_sd2_rating'),
    'images': ('test_images', 'test_paired_production', 'test_repair', 'test_rp6'),
    'adapter': ('test_accepted_raster_adapter', 'test_approved_color_adapter',
                'test_color_derivation_adapter', 'test_edited_import_adapter',
                'test_manual_adapter', 'test_stalled_color_adapter', 'test_target_adapter'),
    'catalog': ('test_catalog_added', 'test_catalog_integration', 'test_catalog_reveal',
                'test_catalog_review', 'test_categories_adapter', 'test_content_update',
                'test_integrated_content', 'test_ke_recovery', 'test_reveal_recovery',
                'test_sd2_catalog', 'test_registration_budgets', 'test_registration_verification'),
}
REFERENCES = ('bars-40', 'bars-100', 'sparse-100', 'color-woven-40',
              'color-woven-100', 'color-sparse-100')


def parse_groups(value):
    groups = value.split(',') if isinstance(value, str) else value
    if (not isinstance(groups, list) or not groups or
            any(g not in GROUPS for g in groups) or len(set(groups)) != len(groups)):
        raise ValueError('Missing, duplicate or unknown production groups')
    return [g for g in GROUPS if g in groups]


def coverage(groups):
    return {g: {'modules': list(MODULES[g]),
                'integrations': list(REFERENCES) if g == 'solver' else
                                ['za1-replay'] if g == 'adapter' else []} for g in groups}


def expected_tests(root, groups):
    """Read source declarations without importing/executing test or product code.

    The runner separately compares actual unittest discovery with this inventory.
    New modules and unsupported generated/inherited cases require explicit routing.
    """
    directory = root / 'tests/puzzle_production'
    declared = [name for names in MODULES.values() for name in names]
    if len(set(declared)) != len(declared) or set(declared) != {p.stem for p in directory.glob('test_*.py')}:
        raise ValueError('Unassigned/missing/duplicate production test module')
    result = {}
    for group in groups:
        for module in MODULES[group]:
            tree = ast.parse((directory / (module + '.py')).read_text(encoding='utf-8'))
            identifiers = [module + '.' + cls.name + '.' + method.name
                           for cls in tree.body if isinstance(cls, ast.ClassDef)
                           for method in cls.body if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')]
            if not identifiers or len(identifiers) != len(set(identifiers)):
                raise ValueError('Empty/duplicate production test declarations: ' + module)
            for identifier in identifiers:
                result[identifier] = group
    return result


def audited_consumers(root):
    """Development-only import audit; not run in sparse/content selection.

    Includes local/function imports, CLI module strings and test fixture readers.
    Non-Python inputs deliberately use explicit audited assignments below.
    """
    production = root / 'tools/puzzle_production'
    tests = root / 'tests/puzzle_production'
    files = {p.stem: p for p in production.glob('*.py')}
    files.update({p.stem: p for p in tests.glob('*.py') if p.stem != '__init__'})
    edges = {}
    for module, path in files.items():
        deps = set()
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.ImportFrom):
                name = node.module or ''
                if node.level or name.startswith(('tools.puzzle_production', 'tests.puzzle_production')) or name in files:
                    deps.add(name.rsplit('.', 1)[-1])
                    deps.update(alias.name for alias in node.names if alias.name in files)
            elif isinstance(node, ast.Import):
                deps.update(a.name.rsplit('.', 1)[-1] for a in node.names
                            if a.name.startswith(('tools.puzzle_production.', 'tests.puzzle_production.')))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value.startswith('tools.puzzle_production.') and node.value.rsplit('.', 1)[-1] in files:
                    deps.add(node.value.rsplit('.', 1)[-1])
        edges[module] = deps & files.keys()
    consumers = {name: set() for name in files}
    for group, modules in MODULES.items():
        pending = list(modules)
        # Group-level integrations are genuine additional consumers.
        pending += ['benchmark'] if group == 'solver' else ['za1_fixtures'] if group == 'adapter' else []
        visited = set()
        while pending:
            module = pending.pop()
            if module in visited:
                continue
            visited.add(module)
            consumers[module].add(group)
            pending.extend(edges[module] - visited)
    return {str(path.relative_to(root)).replace('\\', '/'): tuple(g for g in GROUPS if g in consumers[name]) or GROUPS
            for name, path in sorted(files.items())}


# Filled from the reviewed import graph; the fast tool audit rejects drift.
SOURCE_GROUPS = {'tests/puzzle_production/catalog_fixtures.py': ('catalog',),
 'tests/puzzle_production/oracle.py': ('solver',),
 'tests/puzzle_production/ri_a_measurement.py': ('solver', 'images', 'adapter', 'catalog'),
 'tests/puzzle_production/test_accepted_raster_adapter.py': ('adapter',),
 'tests/puzzle_production/test_analysis.py': ('solver',),
 'tests/puzzle_production/test_approved_color_adapter.py': ('images', 'adapter'),
 'tests/puzzle_production/test_benchmark.py': ('solver',),
 'tests/puzzle_production/test_catalog_added.py': ('catalog',),
 'tests/puzzle_production/test_catalog_integration.py': ('catalog',),
 'tests/puzzle_production/test_catalog_reveal.py': ('catalog',),
 'tests/puzzle_production/test_catalog_review.py': ('catalog',),
 'tests/puzzle_production/test_categories_adapter.py': ('catalog',),
 'tests/puzzle_production/test_cli.py': ('solver',),
 'tests/puzzle_production/test_color_cli.py': ('solver',),
 'tests/puzzle_production/test_color_core.py': ('solver',),
 'tests/puzzle_production/test_color_derivation_adapter.py': ('images', 'adapter'),
 'tests/puzzle_production/test_color_lines.py': ('solver',),
 'tests/puzzle_production/test_content_update.py': ('catalog',),
 'tests/puzzle_production/test_core.py': ('solver',),
 'tests/puzzle_production/test_diagnosis.py': ('solver',),
 'tests/puzzle_production/test_difficulty_rating.py': ('solver',),
 'tests/puzzle_production/test_edited_import_adapter.py': ('images', 'adapter'),
 'tests/puzzle_production/test_images.py': ('images',),
 'tests/puzzle_production/test_integrated_content.py': ('catalog',),
 'tests/puzzle_production/test_ke_recovery.py': ('catalog',),
 'tests/puzzle_production/test_lines.py': ('solver',),
 'tests/puzzle_production/test_manual_adapter.py': ('images', 'adapter'),
 'tests/puzzle_production/test_paired.py': ('solver', 'images', 'catalog'),
 'tests/puzzle_production/test_paired_production.py': ('images',),
 'tests/puzzle_production/test_registration_budgets.py': ('catalog',),
 'tests/puzzle_production/test_registration_verification.py': ('catalog',),
 'tests/puzzle_production/test_repair.py': ('images',),
 'tests/puzzle_production/test_reveal_recovery.py': ('catalog',),
 'tests/puzzle_production/test_rp6.py': ('images',),
 'tests/puzzle_production/test_sd2_analysis.py': ('solver',),
 'tests/puzzle_production/test_sd2_catalog.py': ('catalog',),
 'tests/puzzle_production/test_sd2_rating.py': ('solver',),
 'tests/puzzle_production/test_stalled_color_adapter.py': ('adapter',),
 'tests/puzzle_production/test_target_adapter.py': ('adapter',),
 'tools/puzzle_production/__init__.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/__main__.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/accepted_raster.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/analysis.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/analysis_cli.py': ('solver', 'images'),
 'tools/puzzle_production/analysis_contract.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/analysis_io.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/analysis_rules.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/analysis_verifier.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/authoring_package.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/benchmark.py': ('solver',),
 'tools/puzzle_production/catalog_added.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_added_history.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_analysis.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_difficulty.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_integration.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_io.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_method.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_publication.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_rating.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_reveal.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/catalog_transaction.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/categories.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/certification.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/cli.py': ('solver', 'images'),
 'tools/puzzle_production/color_derivation.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/content_registry.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/content_update.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/contract.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/diagnosis.py': ('solver', 'images'),
 'tools/puzzle_production/diagnosis_cli.py': ('solver', 'images'),
 'tools/puzzle_production/diagnosis_verifier.py': ('solver', 'images'),
 'tools/puzzle_production/difficulty_identity.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/difficulty_rating.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/image_cli.py': ('solver', 'images'),
 'tools/puzzle_production/images.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/integrated_content.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/manual_derivation.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/operation_diagnostics.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/registration_verification.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/p1_export.py': ('solver', 'images'),
 'tools/puzzle_production/paired_solver.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/paired_verifier.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/quality.py': ('solver', 'images'),
 'tools/puzzle_production/repair.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/reveal_retirement.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/reveal_source.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_analysis.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_catalog_rating.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_cli.py': ('solver',),
 'tools/puzzle_production/sd2_contract.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_io.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_profiles.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_rating.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_rating_cli.py': ('solver',),
 'tools/puzzle_production/sd2_rating_freeze.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_rating_identity.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_rating_io.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_reference_checks.py': ('solver',),
 'tools/puzzle_production/sd2_rules.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/sd2_verifier.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/solver.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/target_adapter.py': ('images', 'adapter', 'catalog'),
 'tools/puzzle_production/verifier.py': ('solver', 'images', 'adapter', 'catalog'),
 'tools/puzzle_production/za1_fixtures.py': ('images', 'adapter', 'catalog')}
DATA_GROUPS = {
    **{'tools/puzzle_production/' + name: GROUPS for name in (
        'difficulty_method_0_3.json', 'difficulty_calibration_0_3.json', 'difficulty_references_0_3.json',
        'sd2_method_0_4.json', 'sd2_references_0_4.json', 'sd2_calibration_0_4.json',
        'sd2_validation_0_4.json', 'sd2_comparison_0_4.json')},
}


def select_groups(reasons):
    selected = set()
    for reason in reasons:
        path = reason.removeprefix('audited analysis/solver/rating: ')
        selected.update(SOURCE_GROUPS.get(path, DATA_GROUPS.get(path, GROUPS)))
    return [g for g in GROUPS if g in selected]


def output(groups):
    return json.dumps(groups, separators=(',', ':'))
