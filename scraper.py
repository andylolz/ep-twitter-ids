#!/usr/bin/env python3
import csv
import os
os.environ['SCRAPERWIKI_DATABASE_NAME'] = 'sqlite:///data.sqlite'
from io import StringIO
import time

import requests
import scraperwiki
from twitter import Twitter, OAuth


base_url = 'https://raw.githubusercontent.com/everypolitician/everypolitician-data'
url = base_url + '/master/countries.json'
j = requests.get(url).json()

tmpl = base_url + '/{sha}/{path}'
for country in j:
    print(country['name'])
    for legislature in country['legislatures']:
        leg_handles = {}
        for period in legislature['legislative_periods']:
            data = requests.get(tmpl.format(
                sha=legislature['sha'],
                path=period['csv'])).text
            time.sleep(0.5)
            reader = csv.DictReader(StringIO(data))
            for x in reader:
                if x['twitter'] == '':
                    continue
                leg_handles[x['id']] = {
                    'person_id': x['id'],
                    'country_code': country['code'],
                    'legislature_slug': legislature['slug'],
                    'twitter_handle': x['twitter'],
                }
        if leg_handles:
            scraperwiki.sqlite.save(["person_id", "country_code", "legislature_slug"], leg_handles.values(), "data")

consumer_key = os.environ.get('MORPH_TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('MORPH_TWITTER_CONSUMER_SECRET')
access_token = os.environ.get('MORPH_TWITTER_ACCESS_TOKEN')
access_token_secret = os.environ.get('MORPH_TWITTER_ACCESS_TOKEN_SECRET')

t = Twitter(auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret))

# leg_handles = scraperwiki.sqlite.select('* from data')
handles = [x['twitter_handle'] for x in leg_handles.values()]
ids = [x['id'] for x in t.users.lookup(screen_name=','.join(handles[:100]), _timeout=1)]
