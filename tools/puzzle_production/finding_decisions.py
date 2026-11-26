"""Concrete observations and human decisions on the current content only."""
from copy import deepcopy
from datetime import datetime
import re

from .authoring_package import require, sha, string, timestamp
from . import raster_parameters
from .contract import digest, exact_keys, integer

LOCAL = 'picross-authoring-draft-v3'
PUBLISHED = 'picross-authoring-current-v3'
FORMATS = (LOCAL, PUBLISHED)
COMBINATION = '@selection'
DEFAULT = 'Unverändert beibehalten'

# Only these editorial subrules have a discretionary path. Technical frame
# and colour-pair failures still go through the independent exception checks.
EDITORIAL = {
    'Q-B01': ('secondary-detail',), 'Q-B02': ('illustration-detail',), 'Q-B03': ('edge-quality',),
    'Q-M01': ('secondary-detail',), 'Q-M02': ('area-use',), 'Q-M03': ('colour-role',),
    'Q-R01': ('secondary-detail',), 'Q-R02': ('shape-detail',), 'Q-R03': ('area-use',),
    'Q-R04': ('visual-distinction',), 'Q-H01': ('cell-contrast',),
    'Q-H02': ('hint-contrast', 'hint-colour-assignment'), 'Q-H03': ('clue-structure',),
    'Q-HG02': ('pencil-style',), 'Q-HG03': ('visual-balance',), 'Q-HG04': ('stroke-quality',),
}
SEMANTICS = ('criterion', 'rule', 'properties', 'context', 'effect', 'extent', 'result')
OBSERVATION = {'id', *SEMANTICS, 'description', 'method', 'actor', 'timestamp_utc'}
NEGATIVE = ('Warnung', 'nicht erfüllt')


CRITERIA = {'reveal': {'Q-B01','Q-B02','Q-B03'}, 'motif': {'Q-M01','Q-M02','Q-M03'},
            'background': {'Q-HG01','Q-HG02','Q-HG03','Q-HG04','H-07'},
            'raster': {'Q-R01','Q-R02','Q-R03','Q-R04','Q-H01','Q-H02','Q-H03'}}
OPTION = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z')


def validate_parameters(parameters):
    exact_keys(parameters, {'proposed','approved'})
    for role, values in parameters.items():
        require(isinstance(values,list) and len(values)<=8, 'Invalid parameters')
        for value in values:
            require(isinstance(value,dict), 'Invalid parameter object')
            if value.get('format') == raster_parameters.FORMAT:
                raster_parameters.validate(value)
            else:
                keys = {'width','height','foreground_colors','size_constraint','foreground_color_constraint'}
                exact_keys(value, keys | ({'mode'} if role == 'approved' or 'mode' in value else set()))
                for axis in ('width','height'): integer(value[axis],1,50,axis)
                require(value['size_constraint'] in ('exact','approximate') and
                           value['foreground_color_constraint'] in ('exact','approximate'), 'Invalid raster parameters')
                mode = value.get('mode')
                if (mode is None and role == 'proposed' and value['foreground_color_constraint'] == 'exact'
                        and value['foreground_colors'] == 1):
                    mode = 'mono'
                raster_parameters.require_color_count(mode, value['foreground_colors'])


def matching_modes(parameters, definition, colours):
    actual = {'width': definition['width'], 'height': definition['height'], 'foreground_colors': colours}
    modes = set()
    for option in parameters:
        if 'constraints' in option:
            if all(raster_parameters.accepts(option['constraints'][key], v) for key, v in actual.items()):
                modes.add(option['imports'][0]['mode'])
        elif (all(option['size_constraint'] != 'exact' or option[axis] == actual[axis] for axis in ('width', 'height'))
              and (option['foreground_color_constraint'] != 'exact' or option['foreground_colors'] == colours)):
            modes.add(option['mode'])
    return modes


def check_summaries(value, criteria):
    require(isinstance(value,dict) and set(value)<=criteria, 'Unknown visual criterion')
    for criterion, finding in value.items():
        exact_keys(finding, {'result','accepted','reason','method','actor','timestamp_utc'})
        require(finding['result'] in ('erfüllt','Warnung','nicht erfüllt','nicht geprüft') and type(finding['accepted']) is bool, 'Invalid visual result')
        for key in ('reason','method','actor'):
            string(finding[key], key)
            require('\0' not in finding[key], 'NUL in ' + key)
        if finding['timestamp_utc'] is not None: timestamp(finding['timestamp_utc'])


def subjects(job):
    return {item['id']: item for item in [*job['assets'], *job['rasters']]}


def identity(job, target):
    items = subjects(job)
    if target == COMBINATION:
        selected = job['selected']
        require(all(selected[k] is not None for k in ('reveal', 'background')) and
                (job['operation'] == 'background' or all(selected.values())), 'Incomplete final combination')
        return digest({'job': job['puzzle_id'], 'selection': {
            k: identity(job, v) if v in items else v for k, v in selected.items()},
            'target': None if not job['target'] else job['target']['definition']['sha256'],
            'prepared': (items.get(selected['background'], {}).get('prepared') or {}).get('file', {}).get('sha256'),
            'parameters': job['parameters']['approved']})
    require(target in items, 'Finding candidate missing')
    item = items[target]
    return digest({'job': job['puzzle_id'], 'id': target, 'role': item.get('role', 'raster'),
                   'sha256': (item.get('file') or item['definition'])['sha256'], 'profile': item.get('profile')})


def binding(row):
    return digest({k: v for k, v in row.items() if k != 'decision'})


def eligible(row):
    return row['result'] in NEGATIVE and row['rule'] in EDITORIAL.get(row['criterion'], ())


def effective(row):
    return eligible(row) and row['decision'] is not None and row['decision']['action'] == 'accept'


def check_row(row, target, content, criteria):
    exact_keys(row, OBSERVATION | {'target', 'content', 'decision'})
    require(row['target'] == target and row['content'] == content, 'Stale finding content')
    require(isinstance(row['id'], str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', row['id']),
            'Invalid finding identifier')
    require(isinstance(row['criterion'], str) and row['criterion'] in criteria and row['result'] in (*NEGATIVE, 'nicht geprüft'),
            'Invalid concrete finding')
    require(isinstance(row['rule'], str), 'Invalid finding subrule')
    for key in ('rule', 'properties', 'context', 'effect', 'extent', 'description', 'method', 'actor'):
        string(row[key], key, 4096)
    timestamp(row['timestamp_utc'])
    d = row['decision']
    if d is None:
        return
    exact_keys(d, {'binding', 'action', 'treatment', 'actor', 'timestamp_utc', 'statement', 'source'})
    # Keep earlier records readable. A formerly accepted undifferentiated
    # illustration finding stays visible and can no longer qualify a candidate.
    historical = row['criterion'] == 'Q-B02' and row['rule'] == 'illustration'
    require((eligible(row) or historical) and d['binding'] == binding(row) and d['action'] in ('accept', 'revoke'),
            'Unavailable or stale finding decision')
    for key in ('actor', 'statement', 'treatment'):
        string(d[key], key, 4096)
    timestamp(d['timestamp_utc'])
    if d['source'] is not None:
        exact_keys(d['source'], {'target', 'binding'})
        string(d['source']['target'], 'correction base', 64)
        sha(d['source']['binding'])
        require(d['action'] == 'accept', 'Only an effective acceptance can carry forward')


def validate(job, criteria):
    rows = job['findings']
    require(isinstance(rows, list) and len(rows) <= 512, 'Invalid findings list')
    items = subjects(job)
    instructions = job['instructions']
    require(isinstance(instructions, dict) and set(instructions) <= set(items), 'Invalid treatment targets')
    for values in instructions.values():
        require(isinstance(values, list) and len(values) <= 128, 'Invalid ongoing treatments')
        for value in values:
            string(value, 'Ongoing production treatment')
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('target'), str), 'Invalid finding target')
        target = row['target']
        content = identity(job, target)
        allowed = set.union(*criteria.values()) if target == COMBINATION else criteria.get(items[target].get('role', 'raster'), set())
        check_row(row, target, content, allowed)
        key = (target, row['id'])
        require(key not in seen, 'Duplicate concrete finding')
        seen.add(key)
    for item in items.values():
        # Criterion summaries record coverage. They cannot grant acceptance or
        # conceal an unassessed/negative component.
        relevant = [r for r in rows if r['target'] == item['id']]
        for criterion, summary in item['review'].items():
            require(not summary['accepted'], 'Use a bound finding decision')
            results = [r['result'] for r in relevant if r['criterion'] == criterion]
            worst = next((s for s in ('nicht geprüft', 'nicht erfüllt', 'Warnung') if s in results), 'erfüllt')
            require(summary['result'] == worst or not results and summary['result'] == 'nicht geprüft',
                    'Criterion summary differs from concrete findings')
        require(all(r['criterion'] in item['review'] for r in relevant), 'Finding lacks criterion assessment')


def carry(previous, job, source, target, *, continuing=()):
    """Run on a freshly assessed successor of the specified immediate base."""
    check_base(previous, job, source, target)
    # The actor identifies which instructions still apply even if the observed
    # defect has disappeared. Never recreate a finding just to retain its text.
    available = set(previous['instructions'].get(source, [])) | {
        r['decision']['treatment'] for r in previous['findings'] if r['target'] == source and effective(r)}
    require(all(t in available for t in continuing), 'Unknown continuing treatment')
    if continuing:
        job['instructions'][target] = list(dict.fromkeys(continuing))
    for row in job['findings']:
        if row['target'] != target or row['decision'] is not None:
            continue
        row['decision'] = covered_decision(previous, job, source, row)


def check_base(previous, job, source, target):
    require(previous['puzzle_id'] == job['puzzle_id'] and previous['format'] in FORMATS, 'Invalid correction base')
    old_items, new_items = subjects(previous), subjects(job)
    require(source in old_items and target in new_items and
            old_items[source].get('role') == new_items[target].get('role'), 'Correction base has another role')
    require(target not in old_items or identity(previous, target) != identity(job, target),
            'Cannot transfer to an existing sibling')


def covered_decision(previous, job, source, row):
    def matching(rows, target):
        return [r for r in rows if r['target'] == target and all(r[k] == row[k] for k in SEMANTICS)]
    matches = matching(previous['findings'], source)
    if len(matches) != 1 or not effective(matches[0]) or len(matching(job['findings'], row['target'])) != 1:
        return None
    parent = matches[0]
    return {**deepcopy(parent['decision']), 'binding': binding(row),
            'source': {'target': source, 'binding': binding(parent)}}


def transition(previous, job):
    if previous and previous['format'] in FORMATS:
        require(job['format'] in FORMATS, 'Cannot discard structured decision format')
    if job['format'] not in FORMATS:
        return
    old = previous['findings'] if previous and previous['format'] in FORMATS else []
    revoked = {binding(r): r['decision'] for r in old if r['decision'] and r['decision']['action'] == 'revoke'}
    sources = {}
    for row in job['findings']:
        d = row['decision']
        prior = revoked.get(binding(row))
        if prior and effective(row):
            require(d['source'] is None and datetime.fromisoformat(d['timestamp_utc']) > datetime.fromisoformat(prior['timestamp_utc']),
                    'Reactivation after revocation needs a new actual declaration')
        if d and d['source']:
            require(sources.setdefault(row['target'], d['source']['target']) == d['source']['target'],
                    'A successor has one immediate correction base')
        if not d or not d['source'] or row in old:
            continue
        require(previous and old, 'Missing immediate correction source')
        source = d['source']['target']
        check_base(previous, job, source, row['target'])
        require(d == covered_decision(previous, job, source, row), 'Acceptance not covered by immediate correction source')


def declare(row, *, expected, action, treatment, actor, timestamp_utc, statement):
    """Apply a submitted declaration to the exact observation in the actor's draft."""
    require(binding(row) == expected and eligible(row), 'Finding changed or cannot be accepted')
    require(action in ('accept', 'revoke'), 'Unknown finding action')
    for value in (actor, statement, treatment):
        string(value, 'Submitted declaration')
    timestamp(timestamp_utc)
    row['decision'] = {'binding': expected, 'action': action, 'treatment': treatment,
                       'actor': actor, 'timestamp_utc': timestamp_utc, 'statement': statement, 'source': None}


def selected_review(job):
    """Keep the selected assessments and their declarations in the temporary RI input."""
    items = subjects(job)
    components = {}
    for role, key in job['selected'].items():
        if role == 'background' and key in ('standard', 'none'):
            components[role] = key
            continue
        item = items[key]
        components[role] = {'id': key, 'sha256': (item.get('file') or item['definition'])['sha256'],
                            'review': item['review']}
        if role == 'background':
            components[role]['profile'] = item['profile']
            components[role]['prepared_sha256'] = item['prepared']['file']['sha256']
    return {'instructions': {k:v for k,v in job['instructions'].items() if k in job['selected'].values()},
            'brief': job['brief'], 'components': components, 'parameters': job['parameters']['approved'],
            'findings': [r for r in job['findings'] if r['target'] in (*job['selected'].values(), COMBINATION)]}


def check_selected(review_data, manifest):
    exact_keys(review_data, {'brief', 'instructions', 'components', 'parameters', 'findings', 'actor', 'timestamp_utc', 'statement'})
    string(review_data['brief'], 'Current production instructions', 16384)
    components = exact_keys(review_data['components'], {'reveal', 'motif', 'raster', 'background'})
    job = {'puzzle_id': manifest['entry']['id'], 'operation': 'production', 'target': None, 'assets': [],
           'rasters': [], 'instructions': review_data['instructions'], 'selected': {}, 'parameters': {'approved': review_data['parameters']}, 'findings': review_data['findings']}
    validate_parameters({'proposed': [], 'approved': review_data['parameters']})
    require(review_data['parameters'], 'Selected parameter alternative required')
    expected = {'reveal': manifest['reveal']['asset'], 'raster': manifest['definition']}
    background = manifest['background']
    if background['status'] == 'selected':
        expected['background'] = background['image']['asset']
    for role, value in components.items():
        if role == 'background' and background['status'] != 'selected':
            require(value == background['status'], 'Different background preference in review')
            job['selected'][role] = value
            continue
        exact_keys(value, {'id', 'sha256', 'review'} | ({'profile', 'prepared_sha256'} if role == 'background' else set()))
        require(isinstance(value['id'], str) and OPTION.fullmatch(value['id']) and value['id'] not in ('none','standard'), 'Invalid selected candidate')
        require(value['id'] not in job['selected'].values(), 'Duplicate selected candidate')
        sha(value['sha256'])
        require(role not in expected or expected[role]['sha256'] == value.get('prepared_sha256', value['sha256']), 'Different selected content in review')
        job['selected'][role] = value['id']
        item = {'id': value['id'], 'review': value['review']}
        if role == 'raster':
            item['definition'] = {'sha256': value['sha256']}
            job['rasters'].append(item)
        else:
            item.update(role=role, file={'sha256': value['sha256']})
            if role == 'background':
                from .background_contract import PROFILES
                require(value['profile'] in PROFILES, 'Unknown selected profile')
                item['profile'] = value['profile']
                item['prepared'] = {'file': {'sha256': value['prepared_sha256']}}
            job['assets'].append(item)
        check_summaries(item['review'], CRITERIA[role])
        require(set(item['review']) == CRITERIA[role] and
                all(v['result'] != 'nicht geprüft' for v in item['review'].values()), 'Incomplete selected assessment')
    validate(job, CRITERIA)
    require(all(effective(r) for r in job['findings']), 'Open selected finding')
