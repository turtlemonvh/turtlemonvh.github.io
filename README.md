# turtlemonvh.github.io

Personal website for [@turtlemonvh](https://twitter.com/turtlemonvh)

This branch contains the source code for the site. For docs on how this was set up, see [this blog post](http://turtlemonvh.github.io/using-pelican-and-github-user-pages-to-setup-a-blog.html).

## Usage

Run develop sever. Visit site at: http://localhost:8000/

```bash
# Build
pelican

# Build, serve on port 8000, listen for changes
pelican --listen
```

Publishing

```bash
# Publish output
ghp-import -b master -p output

# Commit source
git add .
git commit -m "Added another blog post"
git push origin source
```

## Setup

```bash
# Install with all submodules loaded
git submodule update --init --recursive

# Make directory for storing rendered html
mkdir output

# Create credentials.json file
# Grab credentials from: https://disqus.com/api/applications/
# Login with Google account
cat > credentials.json <<EOF
{
    "disqus": {
        "sitename": "turtlemonvh-github-io",
        "secret_key": "XX",
        "public_key": "XX"
    }
}
EOF

# Create isolated env
conda create -n blog python==3.10
conda activate blog

# Install python deps
pip install pelican
pip install ghp-import
pip install disqus
pip install disqus-python
pip install markdown

## Update theme
( cd pelican-themes/Flex && git checkout master && git pull )

# Startup dev server
pelican --listen

```

## Custom settings

* https://github.com/alexandrevicenzi/Flex/wiki/Custom-Settings
    * general
* JSON-LD
    * https://github.com/alexandrevicenzi/Flex/blob/master/templates/partial/jsonld_article.html
    * https://github.com/alexandrevicenzi/Flex/blob/master/templates/partial/jsonld.html
* Article metadata
    * https://docs.getpelican.com/en/stable/content.html

## Misc Notes

* Dropbox resume "raw" link: https://www.dropboxforum.com/t5/Create-upload-and-share/Shared-pdf-link-from-dropbox/td-p/501899
* Change to `SITEURL = 'http://localhost:8000/'` when developing locally so css, fonts, etc are served correctly
