import json

data = json.load(open('data/langs.json'));

allLangs = { }
totalLines = 0

for entity in data:
    for org in entity['orgs']:
        for repo in entity['orgs'][org]['repos']:
            for lang in repo['langs']:
                if not lang['name'] in allLangs:
                    allLangs[lang['name']] = { 'name': lang['name'], 'lines': 0, 'repos': [ ] }
                allLangs[lang['name']]['lines'] += lang['lines']
                allLangs[lang['name']]['repos'] += [ repo['url'] ]
                totalLines += lang['lines']

for lang in allLangs:
    allLangs[lang]['pct'] = allLangs[lang]['lines'] / totalLines

langsByOrder = sorted(allLangs, key=lambda lang: allLangs[lang]['lines'], reverse=True)

sortedLangs = [ ]
for lang in langsByOrder:
    sortedLangs.append(allLangs[lang])

byLang = open('data/by-lang.json', 'w');
byLang.write(json.dumps(sortedLangs, sort_keys=False, indent=2))
byLang.close()
