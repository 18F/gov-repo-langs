import os
import sys
import requests
import base64
import yaml
import time
from functools import reduce
import json

def getAuthFragment():
    clientID = os.environ.get('OAUTH_CLIENT_ID');
    clientSecret = os.environ.get('OAUTH_CLIENT_SECRET');
    return 'client_id={0}&client_secret={1}'.format(clientID, clientSecret);

def get_gov_orgs():
    time.sleep(1)
    return yaml.safe_load(base64.b64decode(requests.get('https://api.github.com/repos/github/government.github.com/contents/_data/governments.yml?{0}'.format(getAuthFragment())).json()['content']))

def get_repos_in_org(org, page=1):
    if page == 1:
        print('Getting repos for {0}...'.format(org))
    time.sleep(1)
    response = requests.get('https://api.github.com/orgs/{0}/repos?{2}&page={1}'.format(org, page, getAuthFragment()))

    if page == 1:
        fullList = response.json()
        if 'link' in response.headers and 'rel="next"' in response.headers['link']:
            print('...page {0}'.format(page));
            nextPage = page + 1
            repos, more = get_repos_in_org(org, nextPage)
            fullList = fullList + repos
            while more:
                nextPage += 1
                repos, more = get_repos_in_org(org, nextPage)
                fullList = fullList + repos
        return fullList
    else:
        print('...page {0}'.format(page));
        return response.json(), ('rel="next"' in response.headers['link'])

def get_langs_in_repo(org, repo):
    print('  -> Getting languages for {0}/{1}'.format(org, repo))
    time.sleep(1)
    return requests.get('https://api.github.com/repos/{0}/{1}/languages?{2}'.format(org, repo, getAuthFragment())).json()

def main():
    entities = [
        { 'name': 'US federal government', 'sections': [ 'U.S. Federal', 'U.S. Military and Intelligence' ] },
        { 'name': 'US states', 'sections': [ 'U.S. States' ] },
        { 'name': 'US counties and cities', 'sections': [ 'U.S. County', 'U.S. City' ] },
        { 'name': 'US tribal nations', 'sections': [ 'U.S. Tribal Nations' ] }
    ]

    gov_orgs = get_gov_orgs()

    for level in entities:
        level['orgs'] = { }
        for section in level['sections']:
            for org in gov_orgs[section]:
                level['orgs'][org] = { 'repos': [ ] }

    for org in entities[0]['orgs']:
        repos = get_repos_in_org(org)
        print('--- Got {0} repos for {1}'.format(len(repos), org))
        entities[0]['orgs'][org]['repos'] = [{ 'name': repo['name'], 'desc': repo['description'], 'url': repo['html_url'], 'langs': get_langs_in_repo(org, repo['name']) } for repo in repos]

        for repo in entities[0]['orgs'][org]['repos']:
            if bool(repo['langs']):
                total = reduce((lambda x, y: x + y), [repo['langs'][lang] for lang in repo['langs']])
                repo['langs'] = [{ 'name': lang, 'lines': repo['langs'][lang], 'pct': round(repo['langs'][lang] / total, 3) } for lang in repo['langs']]
            else:
                repo['langs'] = [ ]

    outFile = open('data/langs.json', 'w');
    outFile.write(json.dumps(entities, sort_keys=True, indent=2))
    outFile.close()

if __name__ == '__main__':
    main()
