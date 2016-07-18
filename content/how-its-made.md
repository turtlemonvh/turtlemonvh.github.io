Title: Using pelican and github user pages to setup a blog
Date: 2015-12-27 17:00
Tags: meta
Status: published

This post explains how I set up this blog.

I wrote this partly for myself to make sure I had a well documented way to configure development, and partly for my sister [@woah_caitlyn](https://twitter.com/woah_caitlyn) so she could copy any useful parts to make sites for herself and for friends.

## Create repository

First, I followed the instructions at: [https://pages.github.com/](https://pages.github.com/) and created a new github repo to hold the blog code. 

My site is: [turtlemonvh.github.io](turtlemonvh.github.io) (source code: [https://github.com/turtlemonvh/turtlemonvh.github.io](https://github.com/turtlemonvh/turtlemonvh.github.io))

Then I cloned the site down locally so I could work on it and checked out a branch named `source`.  (See the note below on "Github pages branch names" to see why I used a difference branch than `master`)

## Pelican setup

I followed the instructions [in the quickstart](http://docs.getpelican.com/en/stable/quickstart.html) to set up pelican.  One change is that I ran `pip install pelican markdown ghp-import` to get the `ghp-import` package too.

Next I ran `pelican-quickstart` to generate the initial content. Here are the values I used at the prompts.

    > Where do you want to create your new web site? [.]
    > What will be the title of this web site? Systems Doing
    > Who will be the author of this web site? turtlemonvh
    > What will be the default language of this web site? [en]
    > Do you want to specify a URL prefix? e.g., http://example.com   (Y/n) Y
    > What is your URL prefix? (see above example; no trailing slash) http://turtlemonvh.github.io/
    > Do you want to enable article pagination? (Y/n) Y
    > How many articles per page do you want? [10]
    > What is your time zone? [Europe/Paris] America/New_York
    > Do you want to generate a Fabfile/Makefile to automate generation and publishing? (Y/n) n
    > Do you want an auto-reload & simpleHTTP script to assist with theme and site development? (Y/n) Y
    Done. Your new project is available at /Users/timothy/Projects/turtlemonvh.github.io


I also edited the settings file (`pelicanconf.py`).  You can see my current settings [on github](https://github.com/turtlemonvh/turtlemonvh.github.io/blob/source/pelicanconf.py).  You can also see more docs on settings options [in the pelican docs](http://docs.getpelican.com/en/latest/settings.html).

## Publishing

Next, I started the pelican development server to watch for changes and serve the site locally.

    ./develop_server.sh start

After this you can preview your site at: [http://localhost:8000/](http://localhost:8000/)

Then I created my first bit of content in the `content` directory.  See more docs on writing content [here](http://docs.getpelican.com/en/latest/content.html).  I used [markdown](https://en.wikipedia.org/wiki/Markdown) since I'm familiar with it from a lot of other applications.  You may know it from [github READMEs](https://help.github.com/articles/github-flavored-markdown/).

Lastly I needed to publish the generated content (in the `output` directory) to the `master` branch so the content would be found by github.

```bash

# Add a commit with new generated output
ghp-import -b master output

# Switch branches and push
git checkout master
git push origin master

# OR

# Pushes for you automatically so you don't have to switch branches
ghp-import -b master -p output

```

See more options for the `ghp-import` command [in the project' README](https://github.com/davisp/ghp-import).

After that I could see all my content at: [http://turtlemonvh.github.io/](http://turtlemonvh.github.io/)

## Notes

### Github pages branch names

The documentation on where to put generated content for githib pages was kind of conflicting.  Most docs say to put it on a `gh-pages` branch (e.g. [pelican docs](http://docs.getpelican.com/en/stable/tips.html#publishing-to-github), [github docs showing how to use jekyll](https://help.github.com/articles/using-jekyll-with-pages/)), but [the docs for githib pages](https://pages.github.com/) implies that the `master` branch should be used.

If you are generating a static site for a single repo, you still want to use the `gh-pages` branch.  For example, for my [traffic monitor project](https://github.com/turtlemonvh/traffic-monitor) I created [a site to visualize data with javascript](http://turtlemonvh.github.io/traffic-monitor/) using [a `gh-pages` branch](https://github.com/turtlemonvh/traffic-monitor/tree/gh-pages).

But for user and organization sites github handles things differently and it looks for contant on the `master` branch.  That means that you need to put the source for your articles, your configuration, etc. on a non-master branch.

My solution to this was to move all my source code over to `source` and then use `gh-import` to dump generated content onto the `master` branch.

### More things to do

Here are some things that I didn't do, but you may want to explore.

#### Custom themes

Cloned this repository into `~/pelican-themes`: [https://github.com/getpelican/pelican-themes](https://github.com/getpelican/pelican-themes)

#### Custom domain name

You can follow these directions if you want a custom domain name (like myspecialblog.com): [https://help.github.com/articles/setting-up-a-custom-domain-with-github-pages/](https://help.github.com/articles/setting-up-a-custom-domain-with-github-pages/))

#### Disqus comments

I [don't think this is too hard](https://github.com/getpelican/pelican-plugins/tree/master/disqus_static), but I leave that for later.  For now if you have any questions, find me on twitter.

