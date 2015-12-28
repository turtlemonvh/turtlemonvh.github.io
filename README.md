# turtlemonvh.github.io

Personal website

This branch contains the source code for the site.


To build the output

    # Checkout the branch with the code
    git checkout source

    # Start up a development server on localhost:8000
    # This will also watch for changes and rebuild into the `output` folder
    ./develop_server.sh start

    # Overwrite all content on the master branch
    ghp-import -b master
