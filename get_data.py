import requests
import time
import pandas
import json
from pathlib import Path

# -----------------------------------------------------------------------------
# lib
# -----------------------------------------------------------------------------
class Cache:
    def get(self, key):
        content = ''

        path = Path(key)

        if path.is_file():
            with open(key, 'r') as file_content:
                content = json.load(file_content)

        return content

    def set(self, key, value):
        with open(key, 'w') as file_content:
            json.dump(value, file_content)


def get(entity, method, params = {}):
    _url = 'https://api.steampowered.com/' + entity + '/' + method + '/v001'
    _params = {'key': config['token']}

    if len(params):
        _params.update(params)

    return requests.get(_url, params = _params).json()

def get_heroes():
    response = get('IEconDOTA2_570', 'GetHeroes')
    heroes = {}

    if 'result' in response:
        if 'heroes' in response['result']:
            heroes = response['result']['heroes']

    return heroes

def get_matches(params = {}):
    _params = {}
    matches = {}    

    if len(params):
        _params.update(params)

    response = get('IDOTA2Match_570', 'GetMatchHistory', _params)

    if 'result' in response:
        if 'matches' in response['result']:
            matches = response['result']['matches']

    return matches

def get_match_details(params = {}):
    _params = {}
    details = {}

    if len(params):
        _params.update(params)

    response = get('IDOTA2Match_570', 'GetMatchDetails', _params)

    if 'result' in response:
        details = response['result']

    return details

# -----------------------------------------------------------------------------
# application
# -----------------------------------------------------------------------------
cache = Cache()

config = cache.get('config.json')

heroes = cache.get(config['file_heroes'])

if not heroes:
    heroes = get_heroes()
    cache.set(config['file_heroes'], heroes)

for hero in heroes:

    _data_frames = []
    _match_details = []

    # get limited matches for current hero
    matches = get_matches({
        'hero_id': hero['id'],
        'matches_requested': config['match_limit']
    })

    for match in matches:
        # get all match info
        match_details = get_match_details({'match_id': match['match_id']})

        if len(match_details):
            _match_details.append(match_details);
        else:
            continue

        time.sleep(config['sleep_match_details'])

    time.sleep(config['sleep_matches'])

    _data_frames.append(pandas.DataFrame(_match_details))

    if len(_data_frames) == 0:
        print('no dataframes')
    else:
        _data_frame_str = pandas.concat(_data_frames)
        _data_frame_str.to_json(config['match_details_path'] + str(hero['id']) + '.json', orient='records', indent=4)