# EveryPolitician Twitter Updater

Politicians occasionally update their Twitter handles, usually when they’re up for election or their role has changed.

This script fetches every [Twitter](https://twitter.com) ID and handle in the [EveryPolitician](http://everypolitician.org) data, and queries the Twitter API for changes. It outputs a list of these changes, as well as ensuring the corresponding Twitter ID for every Twitter handle is stored.

### Details

For every Twitter ID in EveryPolitician, [the Twitter API is queried (_users/lookup_)](https://dev.twitter.com/rest/reference/get/users/lookup):

 * If nothing is returned by the API for a given Twitter ID, it means the Twitter account for that ID has been either removed or suspended. In this case, a record is added to the output, but with status `twitter id not found`.

 * If a Twitter handle is returned by the API, it is compared with the Twitter handle stored in EveryPolitician. If the handle has been updated, a record is added to the output that includes the old and new Twitter handles, with status `twitter handle updated`. If the handle hasn’t been updated, a record is added to the output, but with status `no change`.

For every Twitter handle in EveryPolitician that _doesn’t_ have a corresponding Twitter ID, [the Twitter API is queried (_users/lookup_)](https://dev.twitter.com/rest/reference/get/users/lookup):

 * If nothing is returned by the API for a given Twitter handle, it means the handle has changed, or the account has been removed or suspended. In this case, a record is added to the output, but with status `twitter handle not found`.

 * If a Twitter ID is returned by the API, a record is added to the output. If the Twitter handle is the same, the status will be `twitter id added`. If the Twitter handle has changed (i.e. case differences), the status will be `twitter id added; twitter handle updated`.

### Sample output

id | twitter_id | twitter_handle | old_twitter_handle | status
---|------------|----------------|--------------------|-------
96b684de-8474-4245-bdc3-3696e6e854f8 | 975596996 |  | bghattas | twitter id not found
d3889951-f3b1-42cc-a626-df9c620ef24c | 26279847 | ChrisCharlton00 | chrischarltonmp | twitter handle updated
d0e0f592-3578-49aa-aa20-41f73e3fb7ea | 117777690 | jeremycorbyn |  | no change
9f7a9b94-de99-406c-a45e-2f5524aec912 |  |  | Gumi_Kimtw | twitter handle not found
ead00127-d132-40df-a7f9-a134ac7bdad2 | 259148388 | JanePrentice_MP |  | twitter id added
e4c72516-f553-4b6a-9744-2abe4b08f773 | 109579534 | EliseStefanik | elisestefanik | twitter id added; twitter handle updated

### Installation

Requires python3 & SQLite.

<div class="highlight highlight-source-shell"><pre>
# fetch the repo
git clone https://github.com/andylolz/ep-twitter-ids.git
cd ep-twitter-ids

# create a virtualenv
pyvenv env
source env/bin/activate

# install requirements
pip install -r requirements.txt

# run it
python scraper.py
</pre></div>

### Data

This script [runs over here on Morph.io](https://morph.io/andylolz/ep-twitter-ids). You can fetch the output there.
