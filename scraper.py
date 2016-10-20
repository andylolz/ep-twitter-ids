#!/usr/bin/env python3
import itertools
import os
import time

# hack to override sqlite database filename
# see: https://help.morph.io/t/using-python-3-with-morph-scraperwiki-fork/148
os.environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'

import requests
import scraperwiki


# TODO: Use git to fetch the data repo
# (rather than lotsa of requests)

ep_root_url = 'https://cdn.rawgit.com/everypolitician/everypolitician-data/master/'

consumer_key = os.environ.get('MORPH_TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('MORPH_TWITTER_CONSUMER_SECRET')

def _get_token(consumer_key, consumer_secret):
    auth = requests.auth.HTTPBasicAuth(consumer_key, consumer_secret)
    auth_url = 'https://api.twitter.com/oauth2/token'
    auth_data = {'grant_type': 'client_credentials'}
    r = requests.post(url=auth_url, data=auth_data, auth=auth)
    j = r.json()
    return j['access_token']

def _run_query(payload):
    r = requests.post(
        'https://api.twitter.com/1.1/users/lookup.json',
        data=payload,
        headers=auth_header,
    )
    data = r.json()
    time.sleep(0.5)
    if r.status_code != 200:
        if data.get('errors'):
            for error in data['errors']:
                print("Error: {msg} ({code})".format(
                    msg=error['message'],
                    code=error['code'])
                )
        else:
            print("Error: Some unknown problem")
        return None
    return data

# get all the countries
countries = requests.get(ep_root_url + 'countries.json').json()

twitter_data = {}
# get the routes to all the popolo files
for country in countries:
    print(country['name'])
    for legislature in country['legislatures']:
        popolo_url = legislature['popolo_url']
        people = requests.get(popolo_url).json()['persons']
        time.sleep(0.5)
        # build a list of twitter handles for every legislature
        for person in people:
            twitter_handles = [contact_detail['value'] for contact_detail in person.get('contact_details', []) if contact_detail['type'] == 'twitter']
            twitter_ids = [identifier['identifier'] for identifier in person.get('identifiers', []) if identifier['scheme'] == 'twitter']
            for handle, id_ in itertools.zip_longest(twitter_handles, twitter_ids):
                twitter_data[handle.lower()] = {
                    'country_code': country['code'],
                    'legislature_slug': legislature['slug'],
                    'person_id': person['id'],
                    'handle': handle,
                    'twitter_id': id_,
                }

# auth stuff
token = _get_token(consumer_key, consumer_secret)
auth_header = {'Authorization': 'Bearer {token}'.format(token=token)}

# 1. If we have IDs, we want to check handles
handles_with_ids = [v['twitter_id'] for k, v in twitter_data.items() if v['twitter_id']]
for lower in range(0, len(handles_with_ids), 100):
    updates = {}
    print('{} to {}'.format(lower, lower + 100))
    user_ids = ','.join(handles_with_ids[lower:lower + 100])
    payload = {'user_id': user_ids}
    data = _run_query(payload)
    if not data:
        continue
    for x in data:
        handle_lookup = x['screen_name'].lower()
        updates[handle_lookup] = twitter_data[handle_lookup]
        updates[handle_lookup]['handle'] = x['screen_name']
    scraperwiki.sqlite.save(['twitter_id'], updates.values(), "data")

# 2. If we have handles, we want to find the IDs (and check handles!)
handles_without_ids = [v['handle'] for k, v in twitter_data.items() if not v['twitter_id']]
for lower in range(0, len(handles_without_ids), 100):
    updates = {}
    print('{} to {}'.format(lower, lower + 100))
    screen_names = ','.join(handles_without_ids[lower:lower + 100])
    payload = {'screen_name': screen_names}
    data = _run_query(payload)
    if not data:
        continue
    for x in data:
        handle_lookup = x['screen_name'].lower()
        updates[handle_lookup] = twitter_data[handle_lookup]
        updates[handle_lookup]['twitter_id'] = x['id']
        updates[handle_lookup]['handle'] = x['screen_name']
    scraperwiki.sqlite.save(['twitter_id'], updates.values(), "data")
