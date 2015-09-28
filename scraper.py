#!/usr/bin/env python3
import csv
from io import StringIO
import time

import requests
import scraperwiki


url = 'https://raw.githubusercontent.com/everypolitician/viewer-sinatra/master/DATASOURCE'
countries_url = requests.get(url).text
j = requests.get(countries_url).json()

tmpl = 'https://raw.githubusercontent.com/everypolitician/everypolitician-data/{sha}/{path}'
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
