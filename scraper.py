#!/usr/bin/env python3
import itertools
import os
import time

from everypolitician import EveryPolitician
import requests
import scraperwiki


ep = EveryPolitician()

consumer_key = os.environ.get('MORPH_TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('MORPH_TWITTER_CONSUMER_SECRET')

# get a bearer token from twitter
def _get_token(consumer_key, consumer_secret):
    auth = requests.auth.HTTPBasicAuth(consumer_key, consumer_secret)
    auth_url = 'https://api.twitter.com/oauth2/token'
    auth_data = {'grant_type': 'client_credentials'}
    r = requests.post(url=auth_url, data=auth_data, auth=auth)
    j = r.json()
    return j['access_token']

# Run twitter API query
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

# auth stuff
token = _get_token(consumer_key, consumer_secret)
auth_header = {'Authorization': 'Bearer {token}'.format(token=token)}

ep = EveryPolitician()

ep_twitter_data = []
# get the routes to all the popolo files
for country in ep.countries():
    print('Fetching EP data for {country_name} ...'.format(country_name=country.name))
    for legislature in country.legislatures():
        popolo_url = legislature.popolo_url
        people = requests.get(popolo_url).json()['persons']
        time.sleep(0.5)
        # build a list of all the twitter on EP
        for person in people:
            twitter_handles = [contact_detail['value'] for contact_detail in person.get('contact_details', []) if contact_detail['type'] == 'twitter']
            twitter_ids = [identifier['identifier'] for identifier in person.get('identifiers', []) if identifier['scheme'] == 'twitter']
            for handle, id_ in itertools.zip_longest(twitter_handles, twitter_ids):
                ep_twitter_data.append({
                    # 'country_code': country.code,
                    # 'legislature_slug': legislature.slug,
                    'person_id': person['id'],
                    'handle': handle,
                    'twitter_id': id_,
                })

updates = []

# 1. If we have IDs, we want to check handles
ep_data_with_ids = {v['twitter_id']: v for v in ep_twitter_data if v['twitter_id']}
ids_to_check = list(ep_data_with_ids.keys())
api_response_data = {}
for lower in range(0, len(ids_to_check), 100):
    print('Fetching twitter data: {lower:,} to {upper:,} of {len:,} IDs ...'.format(
        lower=lower + 1, upper=lower + 100, len=len(ids_to_check)
    ))
    user_ids = ','.join(ids_to_check[lower:lower + 100])
    payload = {'user_id': user_ids}
    api_response_data_partial = _run_query(payload)
    if not api_response_data_partial:
        continue
    api_response_data.update({x['id']: x for x in api_response_data_partial})

for x in ep_data_with_ids.values():
    if x['twitter_id'] not in api_response_data:
        # hmm - this account may have been deleted.
        # Remove the twitter ID and handle
        print('{person_id}: Twitter ID {id_} (@{handle}) not found.'.format(
            person_id=x['person_id'],
            id_=x['twitter_id'],
            handle=x['handle'],
        ))
        updates.append({
            'id': x['person_id'],
        })
    else:
        new_handle = api_response_data[x['twitter_id']]['screen_name']
        if x['handle'] != new_handle:
            print('{person_id}: Handle changed from @{old} to @{new}'.format(
                person_id=x['person_id'],
                old=x['handle'],
                new=new_handle,
            ))
        updates.append({
            'id': x['person_id'],
            'identifier__twitter': x['twitter_id'],
            'contact_detail__twitter': new_handle,
            'link__twitter': 'https://twitter.com/{handle}'.format(handle=new_handle),
        })

# 2. If we have handles, we want to find the IDs (and check handles!)
ep_data_without_ids = {v['handle']: v for v in ep_twitter_data if not v['twitter_id']}
ids_to_find = list(ep_data_without_ids.keys())
api_response_data = {}
for lower in range(0, len(ids_to_find), 100):
    print('Fetching twitter data: {lower:,} to {upper:,} of {len:,} handles ...'.format(
        lower=lower + 1, upper=lower + 100, len=len(ids_to_find)
    ))
    screen_names = ','.join(ids_to_find[lower:lower + 100])
    payload = {'screen_name': screen_names}
    api_response_data_partial = _run_query(payload)
    if not api_response_data_partial:
        continue
    api_response_data.update({
        x['screen_name'].lower(): x for x in api_response_data_partial
    })

for x in ep_data_without_ids.values():
    if x['handle'].lower() not in api_response_data:
        # hmm - this account may have been deleted.
        # Remove the twitter ID and handle
        print('{person_id}: Twitter handle @{handle} not found.'.format(
            person_id=x['person_id'],
            handle=x['handle'],
        ))
        updates.append({
            'id': x['person_id'],
        })
    else:
        current_twitter_user = api_response_data[x['handle'].lower()]
        new_handle = current_twitter_user['screen_name']
        new_twitter_id = current_twitter_user['id']
        if x['handle'] != new_handle:
            print('{person_id}: Handle changed from @{old} to @{new}'.format(
                person_id=x['person_id'],
                old=x['handle'],
                new=new_handle,
            ))
        print('{person_id}: Twitter ID {id_} added (@{new})'.format(
            person_id=x['person_id'],
            id_=new_twitter_id,
            new=new_handle,
        ))
        updates.append({
            'id': x['person_id'],
            'identifier__twitter': new_twitter_id,
            'contact_detail__twitter': new_handle,
            'link__twitter': 'https://twitter.com/{handle}'.format(handle=new_handle),
        })

scraperwiki.sqlite.save(['id'], updates, "data")
