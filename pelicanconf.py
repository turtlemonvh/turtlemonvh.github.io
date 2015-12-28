#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# See docs.getpelican.com/en/stable/settings.html

SITESUBTITLE = 'Looking for beauty in the complex and the simple.'

AUTHOR = u'turtlemonvh'
SITENAME = u'Systems Doing'
SITEURL = ''

# https://github.com/getpelican/pelican-themes
# http://www.pelicanthemes.com/
THEME = 'notmyidea'

DEFAULT_CATEGORY = 'misc'

PATH = 'content'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Ionic blog', 'https://www.ionic.com/blog/'),
         ('My old blog', 'http://turtle-philosophy.blogspot.com/'),)

# Social widget
SOCIAL = (('twitter', 'https://twitter.com/turtlemonvh'),
          ('about.me', 'https://about.me/turtlemonvh'),
          ('github', 'https://github.com/turtlemonvh'),
          ('linkedin', 'https://www.linkedin.com/in/vanheetm'),
          ('bitbucket', 'https://bitbucket.org/turtlemonvh/'),
          )

TWITTER_USERNAME = 'turtlemonvh'

DEFAULT_PAGINATION = 10

# http://docs.getpelican.com/en/stable/settings.html#reading-only-modified-content
LOAD_CONTENT_CACHE = True
CHECK_MODIFIED_METHOD = 'mtime'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
