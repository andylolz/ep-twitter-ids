# EveryPolitician Twitter Updater

Politicians occasionally update the Twitter handles, usually when they’re up for election or their role has changed.

This script fetches every [Twitter](https://twitter.com) ID and handle in the [EveryPolitician](http://everypolitician.org) data, and queries the Twitter API for changes. It outputs a list of these changes.

### Details

For every Twitter ID in EveryPolitician, [the Twitter API is queried (_users/lookup_)](https://dev.twitter.com/rest/reference/get/users/lookup):

 * If nothing is returned by the API for a given Twitter ID, it means the Twitter account for that ID has been either removed or suspended. In this case, the EveryPolitician ID is added to the output, but without a Twitter ID or handle.

 * If a Twitter handle is returned by the API, it is compared with the Twitter handle stored in EveryPolitician. If the handle has been updated, the EveryPolitician ID is added to the output along with the Twitter ID and new handle.

For every Twitter handle in EveryPolitician that _doesn’t_ have a corresponding Twitter ID, [the Twitter API is queried (_users/lookup_)](https://dev.twitter.com/rest/reference/get/users/lookup):

 * If nothing is returned by the API for a given Twitter handle, it means the handle has changed, or the account has been removed or suspended. In this case, the EveryPolitician ID is added to the output, but without a Twitter ID or handle.

 * If a Twitter ID is returned by the API, the EveryPolitician ID is added to the output along with the Twitter ID and existing handle.

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

This script [runs over here on Morph.io](https://morph.io/andylolz/ep-Twitter-ids). You can fetch the output there.
