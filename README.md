# turtlemonvh.github.io

Personal website for [@turtlemonvh](https://twitter.com/turtlemonvh)

This branch contains the source code for the site.  For docs on how this was set up, see [this blog post](http://turtlemonvh.github.io/using-pelican-and-github-user-pages-to-setup-a-blog.html).

## Usage

Run develop sever.  Visit site at: http://localhost:8000/

    bash develop_server.sh start
    bash develop_server.sh start 8081 # start on a different port

    # To reload / stop
    bash develop_server.sh restart 8080
    bash develop_server.sh stop

Publishing

    # Publish output
    ghp-import -b master -p output

    # Commit source
    git add .
    git commit -m "Added another blog post"
    git push origin source

## Setup

```
git submodule update --init --recursive

# Create credentials.json file
cat > credentials.json <<EOF
{
    "disqus": {
        "sitename": "turtlemonvh-github-io",
        "secret_key": "XX",
        "public_key": "XX"
    }
}
EOF

# Make directory for rendering
mkdir output

# Install python deps
pip install pelican
pip install disqus
pip install markdown

# Startup
bash develop_server.sh start

```