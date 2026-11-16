"""Revision-scoped retirement of merged reveal work; no package reconstruction."""
import hashlib
import os
import re
import stat
import subprocess

from . import catalog_io as io, catalog_transaction as tx, reveal_source as source
from .authoring_package import require
from .contract import exact_keys, write_json

INDEX = 'content/authoring/index.json'
LIMIT = 8 * 1024 * 1024


def selection(identifier, revision):
    require(isinstance(identifier, str) and re.fullmatch(r'pz-[a-z0-9][a-z0-9-]{0,59}', identifier),
            'Invalid authoring puzzle ID')
    require(isinstance(revision, str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,31}', revision),
            'Invalid authoring revision')
    return f'content/authoring/{identifier}/{revision}'


def index_rows(value):
    exact_keys(value, {'format', 'entries'})
    require(value['format'] == 'picross-authoring-index-v1' and isinstance(value['entries'], list),
            'Invalid authoring index')
    result = {}
    folded = set()
    for row in value['entries']:
        exact_keys(row, {'puzzle_id', 'revision', 'record'})
        directory = selection(row['puzzle_id'], row['revision'])
        require(row['record'] == directory + '/record.json' and directory.casefold() not in folded,
                'Duplicate/noncanonical authoring index entry')
        folded.add(directory.casefold())
        result[directory] = row
    return result


def blob_id(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def tree_files(root, directory):
    base = io.safe(root, directory)
    if not base.exists():
        return set()
    require(base.is_dir(), 'Authoring revision is not a directory')
    result = set()
    for child in base.rglob('*'):
        name = child.relative_to(root).as_posix()
        child = io.safe(root, name)
        if child.is_file():
            result.add(name)
        else:
            require(any(child.iterdir()), 'Foreign empty authoring directory: ' + name)
    return result



def retire(root,revisions,integrated_commit):
    from .integrated_content import retire as current
    identifiers=sorted({pair[0] for pair in revisions})
    return current(root,identifiers,integrated_commit,completed_revisions=revisions)
