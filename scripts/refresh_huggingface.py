#!/usr/bin/env python3
"""Build a selected collection-based Releases snapshot from public Hugging Face APIs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import re
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

EXCLUDED = {
    'bofenghuang/whisper-large-v3-turbo-repl-enc',
    'bofenghuang/deprecated-whisper-large-v2-cv11-french-punct-plus',
    'bofenghuang/parakeet-tdt-0.6b-v3-hybrid',
    'bofenghuang/whisper-large-v3-distil-fr-exp',
    'bofenghuang/whisper-large-v3-distil-multi-exp',
}
# The v3.5 repository predates its public release; use the release date.
RELEASE_DATE_OVERRIDES = {'distil-whisper/distil-large-v3.5': '2025-03-19T00:00:00.000Z'}
# Replaced on the website by the merged Vigogne 2 collection; HF source remains unchanged.
OMITTED_COLLECTION_IDS = {'652917c0578679aac7a9fe19'}
SHARED_COLLECTIONS = [
    'distil-whisper/distil-large-v35',
    'doctolib-lab/doctobert-fr',
    'doctolib-lab/finemed-fr',
]


def read_json(url):
    request = Request(url, headers={'User-Agent': 'personal-site-releases/3.0', 'Accept': 'application/json'})
    with urlopen(request, timeout=30) as response:
        return json.load(response), response.headers.get('Link', '')


def paginated(url):
    result, seen = [], set()
    while url:
        if url in seen or urlparse(url).netloc != 'huggingface.co':
            raise ValueError('Invalid pagination URL')
        seen.add(url)
        page, links = read_json(url)
        if not isinstance(page, list):
            raise ValueError('Unexpected list response')
        result.extend(page)
        match = re.search(r'<([^>]+)>;\s*rel="next"', links)
        url = match.group(1) if match else None
    return result


def endpoint(kind, author):
    params = [('author', author), ('limit', '1000')]
    # Only the Vigogne/Vigostral members of this large namespace are selected.
    if author == 'TheBloke':
        params.append(('search', 'vig'))
    params.extend(('expand[]', f) for f in ['downloads', 'downloadsAllTime', 'createdAt'])
    return 'https://huggingface.co/api/' + ('models' if kind == 'model' else 'datasets') + '?' + urlencode(params)


def create_snapshot(author, collections, repositories, presentation):
    records = {}
    for kind, rows in repositories.items():
        for row in rows:
            records[kind + ':' + row['id']] = row
    entries, selected = [], {}
    for collection in collections:
        collection_id = collection['slug'].rsplit('-', 1)[-1]
        metadata = presentation['collections'].get(collection_id, {})
        excluded_resources = set(metadata.get('excluded_resources', []))
        keys, primary_dates, dates = [], [], []
        owner = collection['slug'].split('/')[0]
        for item in collection['items']:
            kind, resource_id = item.get('type'), item['id']
            if kind not in ('model', 'dataset') or resource_id in EXCLUDED:
                continue
            key = kind + ':' + resource_id
            if key in excluded_resources:
                continue
            row = records.get(key)
            if row is None:
                raise ValueError('Missing collection member: ' + key)
            if any(isinstance(row.get(f), bool) or not isinstance(row.get(f), int) or row[f] < 0 for f in ['downloads', 'downloadsAllTime']):
                raise ValueError('Invalid download metrics: ' + key)
            keys.append(key)
            selected[key] = row
            if not row.get('createdAt'):
                raise ValueError('Missing release date: ' + key)
            release_date = RELEASE_DATE_OVERRIDES.get(resource_id, row['createdAt'])
            dates.append(release_date)
            if resource_id.startswith(owner + '/'):
                primary_dates.append(release_date)
        keys = list(dict.fromkeys(keys))
        if not keys:
            continue
        first_release = min(primary_dates or dates)
        entries.append({
            'id': collection_id,
            'category': metadata.get('category', 'other'),
            'note': metadata.get('note', ''),
            'description': metadata.get('description') or collection.get('description') or 'A collection of model and dataset releases.',
            'title': metadata.get('title', collection['title']),
            'url': 'https://huggingface.co/collections/' + collection['slug'],
            'year': metadata.get('year', int(first_release[:4])), 'first_release': first_release,
            'order': metadata.get('order', 100),
            'resources': keys,
            'downloads_month': sum(records[k]['downloads'] for k in keys),
            'downloads_all_time': sum(records[k]['downloadsAllTime'] for k in keys),
        })
    entries.sort(key=lambda c: (c['order'], -c['year'], -datetime.fromisoformat(c['first_release'].replace('Z', '+00:00')).timestamp(), c['title']))
    groups = []
    categories = presentation['categories'] + [{'id': 'other', 'title': 'Other releases'}]
    for category in categories:
        members = [c for c in entries if c['category'] == category['id']]
        if members:
            groups.append({**category, 'collections': members})
    aggregates = {c['id']: c['resources'] for c in entries}
    aggregates['all'] = sorted(selected)
    namespaces = sorted({(k.split(':', 1)[0], row['id'].split('/')[0]) for k, row in selected.items()})
    return {
        'author': author, 'profile_url': 'https://huggingface.co/' + author + '/collections',
        'fetched_at': datetime.now(ZoneInfo('Europe/Paris')).isoformat(timespec='seconds'),
        'downloads_month': sum(r['downloads'] for r in selected.values()),
        'downloads_all_time': sum(r['downloadsAllTime'] for r in selected.values()),
        'groups': groups,
        'live': {'endpoints': [{'kind': kind, 'url': endpoint(kind, owner)} for kind, owner in namespaces],
                 'resources': sorted(selected), 'aggregates': aggregates},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--author', default='bofenghuang')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'data/huggingface.json')
    args = parser.parse_args()
    presentation = json.loads((Path(__file__).resolve().parents[1] / 'data/release_collections.json').read_text())
    sources = presentation.get('collection_sources', {})
    previews = paginated('https://huggingface.co/api/collections?' + urlencode({'owner': args.author, 'limit': 100}))
    slugs = list(dict.fromkeys([sources.get(c['slug'].rsplit('-', 1)[-1], c['slug']) for c in previews if c['slug'].rsplit('-', 1)[-1] not in OMITTED_COLLECTION_IDS] + SHARED_COLLECTIONS))
    with ThreadPoolExecutor(max_workers=6) as pool:
        collections = list(pool.map(lambda slug: read_json('https://huggingface.co/api/collections/' + slug)[0], slugs))
    jobs = sorted({(i['type'], i['id'].split('/')[0]) for c in collections for i in c['items'] if i.get('type') in ('model', 'dataset') and i['id'] not in EXCLUDED})
    repositories = {'model': [], 'dataset': []}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [(kind, pool.submit(paginated, endpoint(kind, owner))) for kind, owner in jobs]
        for kind, future in futures:
            repositories[kind].extend(future.result())
    snapshot = create_snapshot(args.author, collections, repositories, presentation)
    temporary = args.output.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(args.output)
    for group in snapshot['groups']:
        print(group['title'], ':', ', '.join(c['title'] for c in group['collections']))
    print(f"Downloads: {snapshot['downloads_month']:,} last 30 days; {snapshot['downloads_all_time']:,} all time (deduplicated).")


if __name__ == '__main__':
    main()
