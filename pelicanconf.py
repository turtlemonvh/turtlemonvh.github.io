#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import json

# See docs.getpelican.com/en/stable/settings.html

AUTHOR = u'turtlemonvh'
SITENAME = u'Systems Doing'
SITETITLE = SITENAME
SITESUBTITLE = 'Looking for beauty in the complex and the simple.'
SITEDESCRIPTION = 'Thoughts and writings'
SITEURL = 'http://turtlemonvh.github.io/'
#SITEURL = 'http://localhost:8081/'
SITELOGO = '//s.gravatar.com/avatar/fdb8ce54c398b1aa794833a601507361?s=120'

# https://github.com/getpelican/pelican-themes
# http://www.pelicanthemes.com/
THEME = 'pelican-themes/Flex'

DEFAULT_CATEGORY = 'Articles'
DEFAULT_METADATA = {
    'status': 'draft',
}

PATH = 'content'
STATIC_PATHS = ['images', 'pdfs']

TIMEZONE = 'America/New_York'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ('Ionic blog', 'https://www.ionic.com/blog/'),
    ('My old blog', 'http://turtle-philosophy.blogspot.com/'),
    ('about.me', 'https://about.me/turtlemonvh'),
)

# Social widget
SOCIAL = (
    ('twitter', 'https://twitter.com/turtlemonvh'),
    ('github', 'https://github.com/turtlemonvh'),
    ('linkedin', 'https://www.linkedin.com/in/vanheetm'),
    ('bitbucket', 'https://bitbucket.org/turtlemonvh/'),
    ('stack-overflow', 'http://stackoverflow.com/users/790075/turtlemonvh'),
)

TWITTER_USERNAME = 'turtlemonvh'

DEFAULT_PAGINATION = 10

# http://docs.getpelican.com/en/stable/settings.html#reading-only-modified-content
LOAD_CONTENT_CACHE = True
CHECK_MODIFIED_METHOD = 'mtime'


## Load credentials from json file that is NOT checked in
with open("credentials.json") as f:
    creds = json.load(f)

## Plugins

PLUGIN_PATHS = ["pelican-plugins"]
PLUGINS = [u"disqus_static"]
#PLUGINS += [u"thumbnailer"]

# https://disqus.com/admin/
# https://turtlemonvh-github-io.disqus.com/admin/
# https://disqus.com/api/applications/
DISQUS_SITENAME = creds['disqus']['sitename']
DISQUS_SECRET_KEY = creds['disqus']['secret_key']
DISQUS_PUBLIC_KEY = creds['disqus']['public_key']

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
DISABLE_URL_HASH = True
