#!/usr/bin/env python3
#
#  Copyright (c) 2021 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <rich.mahn@unfoldingword.org>
"""
This script generates the stats on a user or org with ts projects
"""
import sys
import json
import urllib.parse
import urllib.request
from usfm_verses import verses
from contextlib import closing

owner = None
stats = {'langs': {'count': 0, 'items': {}}}


def get_json(url):
    response = None
    try:
        with closing(urllib.request.urlopen(url)) as request:
            response = request.read()
        return json.loads(response)
    except:
        return None


def get_stats():
    repos_url = f"https://git.door43.org/api/v1/repos/search?owner={urllib.parse.quote_plus(owner)}"
    response = get_json(repos_url)
    if not response or not len(response['data']):
        print("No repositories found. Exiting.")
        exit(1)
    repo_total = len(response['data'])
    for idx, repo in enumerate(response['data']):
        # if idx > 2:
        #   break
        project = repo['name']
        print(f"Processing {project} ({idx+1}/{repo_total})...")
        manifest_url = f"https://git.door43.org/{owner}/{project}/raw/branch/master/manifest.json"
        manifest = get_json(manifest_url)
        lang = None
        resource = None
        book = None
        if manifest and 'package_version' in manifest and manifest[
                'package_version'] >= 6:
            lang = manifest['target_language']['id']
            book = manifest['project']['id']
            resource = manifest['resource']['id']
        else:
            parts = project.split('_')
            if len(parts) == 4:
                lang = parts[0]
                book = parts[1]
                resource = parts[3]
        if lang not in stats['langs']['items']:
            stats['langs']['items'][lang] = {'resources': {'count': 0, 'items': {}}}
            stats['langs']['count'] += 1
        if resource not in stats['langs']['items'][lang]['resources']['items']:
            stats['langs']['items'][lang]['resources']['items'][resource] = {'books': {'count': 0, 'items': {}}}
            stats['langs']['items'][lang]['resources']['count'] += 1
        if book not in stats['langs']['items'][lang]['resources']['items'][resource]['books']['items']:
            stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book] = {'projects': {'count': 0, 'items': {}}}
            stats['langs']['items'][lang]['resources']['items'][resource]['books']['count'] += 1
        if project not in stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items']:
            if book.upper() in verses:
                total = verses[book.upper()]['chapters']
            elif book.upper() == 'OBS':
                total = 50
            stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items'][project] = {'chapters': {'count': 0, 'total': total, 'items': {}}}
            stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['count'] += 1
        if 'finished_chunks' in manifest and manifest['finished_chunks']:
            for chunk in manifest['finished_chunks']:
                chapter, verse = chunk.split('-')[0:2]
                if chapter not in stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items'][project]['chapters']['items']:
                    stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items'][project]['chapters']['items'][chapter] = {'chunks': {'count': 0, 'items': []}}
                    if chapter != 'front':
                        stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items'][project]['chapters']['count'] += 1
                stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items'][project]['chapters']['items'][chapter]['chunks']['items'].append(verse)
                stats['langs']['items'][lang]['resources']['items'][resource]['books']['items'][book]['projects']['items'][project]['chapters']['items'][chapter]['chunks']['count'] += 1


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        owner = input("DCS user or org to display stats for [burje_duro]: ")
        if not owner:
            owner = "burje_duro"
    else:
        owner = sys.argv[1]
    get_stats()
    print(json.dumps(stats, indent=2, sort_keys=True))
