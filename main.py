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
SHOW_CHUNKS = False
stats = {}

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
    for idx, repo in enumerate(response['data']):
        # if idx > 2:
        #   break
        name = repo['name']
        print(f"Processing {name}...")
        manifest_url = f"https://git.door43.org/{owner}/{repo['name']}/raw/branch/master/manifest.json"
        manifest = get_json(manifest_url)
        lang = None
        resource = None
        book = None
        if manifest and 'package_version' in manifest and manifest['package_version'] >= 6:
          lang = manifest['target_language']['id']
          book = manifest['project']['id']
          resource = manifest['resource']['id']
        else:
          parts = name.split('_')
          if len(parts) == 4:
            lang = parts[0]
            book = parts[1]
            resource = parts[3]
        if lang not in stats:
          stats[lang] = {}
        if resource not in stats[lang]:
          stats[lang][resource] = {}
        if book not in stats[lang][resource]:
          stats[lang][resource][book] = {}
        if name not in stats[lang][resource][book]:
          stats[lang][resource][book][name] = {}
        for chunk in manifest['finished_chunks']:
            chapter, verse = chunk.split('-')[0:2]
            if chapter not in stats[lang][resource][book][name]:
                stats[lang][resource][book][name][chapter] = []
            stats[lang][resource][book][name][chapter].append(verse)

def display_stats():
  print(f"\nStats for {owner}:\n")
  print(f"Languages: {len(stats.keys())}")
  for lang in sorted(stats.keys()):
    print(f"  {lang}:")
    print(f"    Resources: {len(stats[lang].keys())}")
    for resource in sorted(stats[lang]):
      print(f"      {resource}:")
      print(f"        Books: {len(stats[lang][resource].keys())}")
      for book in sorted(stats[lang][resource]):
        print(f"          {book}:")
        for name in sorted(stats[lang][resource][book]):
          print(f"            {name}")
          done = stats[lang][resource][book][name].keys()
          num_done = len(done)
          if 'front' in done:
            num_done -= 1
          outof = ""
          if book.upper() in verses:
            outof = f" of {verses[book.upper()]['chapters']}"
          elif book.upper() == 'OBS':
            outof = " of 50"
          print(f"              Chapters: {len(stats[lang][resource][book][name].keys())}{outof}")
          print(f"                {', '.join(sorted(stats[lang][resource][book][name]))}")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        owner = input("DCS user or org to display stats for [burje_duro]: ")
        if not owner:
          owner = "burje_duro"
    else:
        owner = sys.argv[1]    
    get_stats()
    display_stats()
