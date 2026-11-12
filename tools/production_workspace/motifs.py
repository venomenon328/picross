"""Metadata-only source relations and one view choice per puzzle identity."""
from collections import defaultdict

from .sources import git, check_commit

PHASES = {'brief_ready': 'Briefing', 'reveal_review': 'Abschlussbilder', 'motif_review': 'Motivvorlage',
          'motif_approved': 'Rasterproduktion', 'raster_review': 'Rasterentwurf', 'raster_ready': 'Rasterangebote',
          'background_review': 'Kontextzeichnungen', 'content_ready': 'Endabnahme',
          'editorially_approved': 'Integration', 'registered': 'Registriert'}


class Relations:
    """Walk commit headers, including real parents hidden by shallow boundaries.

    At most two selected tips per bounded reload (64 generations, blob:none),
    and 256 headers per comparison. Missing history stays unknown. Never asks
    the user's checkout to fetch or changes its shallow file/refs.
    """
    def __init__(self, repository):
        self.repository = repository
        self.parents = {}
        self.reloads = 2

    def ancestors(self, tip, target):
        todo, seen, complete = [tip], set(), True
        while todo and len(seen) < 256:
            sha = todo.pop()
            if sha in seen:
                continue
            seen.add(sha)
            if sha == target:
                return seen, False
            if sha not in self.parents:
                self.parents[sha] = None
                for source in (self.repository.local, self.repository.cached):
                    if source is None:
                        continue
                    try:
                        size = int(git(source.root, 'cat-file', '-s', sha))
                        if size > 128 * 1024:
                            continue
                        raw = git(source.root, 'cat-file', 'commit', sha)
                        headers = raw.split(b'\n\n', 1)[0].splitlines()
                        self.parents[sha] = [check_commit(line[7:].decode('ascii')) for line in headers if line.startswith(b'parent ')]
                        break
                    except (ValueError, OSError, UnicodeError):
                        continue
            parents = self.parents[sha]
            if parents is None:
                complete = False
            else:
                todo.extend(parents)
        return seen, complete and not todo

    def compare(self, left, right):
        if left == right:
            return 'equal'
        for source in (self.repository.local, self.repository.cached):
            if source is None:
                continue
            for ancestor, descendant, answer in ((right, left, 'ahead'), (left, right, 'behind')):
                try:
                    git(source.root, 'merge-base', '--is-ancestor', ancestor, descendant)
                    return answer
                except (ValueError, OSError):
                    pass  # Negative/shallow results do not prove divergence.
        for attempt in range(2):
            a, ac = self.ancestors(left, right)
            if right in a:
                return 'ahead'
            b, bc = self.ancestors(right, left)
            if left in b:
                return 'behind'
            if ac and bc:
                return 'divergent'
            if attempt or not self.reloads or not self.repository.remote_confirmed:
                break
            self.reloads -= 1
            try:
                # Only tips actually advertised into this private cache; a
                # local-only tip need not be accepted as a want by the remote.
                tips = set(git(self.repository.cached.root, 'for-each-ref', '--format=%(objectname)', 'refs/pw/').decode().splitlines())
                selected = [sha for sha in (left, right) if sha in tips]
                if selected:
                    self.repository.fetch(*selected, filtered=True, depth=64)
            except (ValueError, OSError):
                pass
            self.parents = {key: value for key, value in self.parents.items() if value is not None}
        return 'unknown'


def group(jobs, comparisons, *, confirmed, remote):
    def relation(a, b):
        if a == b:
            return 'equal'
        return comparisons.get(a + ':' + b, 'unknown')

    grouped = defaultdict(list)
    for job in jobs:
        grouped[job['puzzle_id']].append(job)
    result = []
    for puzzle_id, rows in grouped.items():
        versions = {}
        for row in rows:
            key = (row['revision'], row['binding'])
            version = versions.setdefault(key, {'revision': row['revision'], 'phase': row['phase'],
                'sources': [], 'current': False, 'binding': row['binding']})
            version['sources'].append(row['id'])
        local, other = [r for r in rows if r['source'] == 'local'], [r for r in rows if r['source'] == 'remote']
        conflicting = any(r.get('conflict') for r in rows)
        # Local/remote synchronization compares the same ref, not independent
        # main and production histories. Revisions within each ref share its tip.
        pairs = {relation(a['commit'], b['commit']) for a in local for b in other if a['ref'] == b['ref']}
        same_refs = {r['ref'] for r in local} == {r['ref'] for r in other}
        if not remote or not confirmed:
            status = 'Remote nicht aktuell bestätigt'
        elif conflicting or 'divergent' in pairs:
            status = 'Abweichende Stände'
        elif not local:
            status = 'Nur Remote vorhanden'
        elif not other:
            status = 'Nur lokal vorhanden'
        elif not same_refs or 'unknown' in pairs:
            status = 'Remote nicht aktuell bestätigt'
        elif pairs <= {'equal'} and pairs:
            status = 'Synchron'
        elif pairs <= {'equal', 'ahead'} and pairs:
            status = 'Lokal neuer'
        elif pairs <= {'equal', 'behind'} and pairs:
            status = 'Remote neuer'
        else:
            status = 'Abweichende Stände' if pairs else 'Remote nicht aktuell bestätigt'
        # Current pointers compete by actual ancestry, never by phase/revision.
        candidates = [r for r in rows if r.get('current_view')]
        tips = [r for r in rows if not any(relation(o['commit'], r['commit']) == 'ahead' for o in rows)]
        maximal = [r for r in candidates if not any(relation(o['commit'], r['commit']) == 'ahead' for o in rows)]
        choice = None
        if not conflicting and maximal and all(any(
                (c['source'], c['ref'], c['commit']) == (r['source'], r['ref'], r['commit']) for c in candidates) for r in tips):
            keys = {(r['revision'], r['binding']) for r in maximal}
            relations = {relation(a['commit'], b['commit']) for a in tips for b in tips}
            if len(keys) == 1 and relations <= {'equal', 'ahead', 'behind'}:
                choice = next(iter(keys))
        ordered = list(versions.items())
        ordered.sort(key=lambda item: item[0] != choice)  # Preserve alternatives as peers.
        for key, version in ordered:
            version['current'] = key == choice
            origins = {r['source'] for r in rows if r['id'] in version['sources']}
            version['source_label'] = 'Lokal und Remote' if len(origins) == 2 else 'Lokal' if 'local' in origins else 'Remote'
        selected = versions.get(choice)
        current_id = next((r['id'] for r in maximal if (r['revision'], r['binding']) == choice), None)
        if selected:
            selected['sources'].sort(key=lambda jid: jid != current_id)
        chosen = next((r for r in rows if r['id'] == current_id), rows[0])
        errors = list(dict.fromkeys(r['current_error'] for r in rows if r.get('current_error')))
        if local and other and not same_refs:
            errors.append('Lokaler oder Remote-Gegenref fehlt für dieses Motiv; Gesamtvergleich nicht bestätigt.')
        if 'unknown' in pairs:
            errors.append('Git-Abstammung nach begrenztem Metadatennachladen ungeklärt; Version bewusst wählen.')
        if not choice:
            errors.append('Aktuelle Übergabe nicht eindeutig. Version bewusst wählen oder aktuellen Ansichtsbezug veröffentlichen.')
        result.append({'puzzle_id': puzzle_id, 'title': chosen['title'], 'phase': chosen['phase'] if choice else 'Versionswahl nötig',
                       'status': status, 'current_job': current_id, 'versions': [v for _, v in ordered], 'notes': errors})
    for motif in result:
        motif['label'] = motif['title'] + ((' · ' + motif['puzzle_id']) if sum(m['title'] == motif['title'] for m in result) > 1 else '') + ' · ' + motif['phase']
    return result
