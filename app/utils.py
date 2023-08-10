import functools
import os
import re

import requests


class Example:
    def __init__(self, url: str = ''):
        self.url = url.strip().strip('/')
        self.embed_type = ''
        self.html = ''
        self.error = ''

    def process(self):

        if not self.is_valid():
            return

        # Prepare the oembed url based on the input url.
        oembed_url_str = OEMBED[self.embed_type]['oembed']
        oembed_url = oembed_url_str.format(self.url)

        # Fetch the oembed data.
        self.html = fetch_embed(oembed_url)

        if not self.html:
            self.error = f'error fetching {self.embed_type} embed'

    def is_valid(self) -> bool:

        # Check if the url is empty.
        if not self.url:
            self.error = 'social embed URL is required'
            return False

        # Check that the URL is a valid social embed url.
        for embed_type, component in OEMBED.items():
            if re.search(component['pattern'], self.url):
                self.embed_type = embed_type
                return True

        self.error = 'invalid social embed URL'
        return False

    def output(self) -> str:
        s = PLACEHOLDER_1

        if self.html:
            s = '\n\n'.join([
                PLACEHOLDER_2.format(self.embed_type),
                self.html,
                PLACEHOLDER_3.format(self.embed_type)
            ])

        return OUTPUT.format(s)


# -------------------------------------------------------------------


@functools.cache
def fetch_embed(url):
    res = requests.get(url)
    if res.ok:
        return res.json()['html']
    return ''


FB_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')


OEMBED = {
    'instagram': {
        'pattern': r'https://(www.)?instagram.com/p/.+',
        'oembed': 'https://graph.facebook.com/v14.0/instagram_oembed?url={}&access_token=' + FB_TOKEN,
    },
    'youtube': {
        'pattern': r'https://(www.)?youtube.com/watch\?v=.+',
        'oembed': 'https://youtube.com/oembed?url={}',
    },
    'twitter': {
        'pattern': r'https://(www.)?twitter.com/.+/status/.+',
        'oembed': 'https://publish.twitter.com/oembed?url={}',
    },
}


OUTPUT = """<?xml version="1.0" encoding="ISO-8859-1" ?>
<rss version="2.0">
<channel>
  <title>Example Feed</title>
  <link>http://example.com</link>
  <description>Example Feed</description>
  <item>
    <title>Article example</title>
    <link>http://example.com/d583c/article</link>
    <description><![CDATA[
<p>Example article summary ...</p>

{}
    ]]>
    </description>
  </item>
</channel>
</rss>
"""

PLACEHOLDER_1 = "<!-- [[ YOUR SOCIAL EMBED HERE ]] -->"
PLACEHOLDER_2 = "<!-- [[ ⬇️ YOUR {} EMBED HERE ⬇️ ]] -->"
PLACEHOLDER_3 = "<!-- [[ ⬆️ YOUR {} EMBED HERE ⬆️ ]] -->"
