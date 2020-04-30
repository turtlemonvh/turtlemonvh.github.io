Title: Using python to transform and filter data in bash pipes
Date: 2020-04-30 09:30
Tags: bash, python, tools
Status: published

I've long been a fan of bash pipes and the unix philosophy of composability. The text stream interface is so simple to extend and build upon that once you create a simple command line tool that works over stdin and stdout you suddenly have interoperability with a tremendous number of tools and workflows.

I'm also a fan of python generators. Ever since watching [David Beazley's talks on generators](https://www.dabeaz.com/generators/) about 8 years ago, I have used generators extensively in my python code as a way to keep memory usage low and actions composable, using both [the explicit `yield` syntax](https://wiki.python.org/moin/Generators) as well as the more compact [list comprehension syntax](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions). Thinking about operations as a series of transforms feels natural and lends itself to fairly high re-usability, especially for data processing workloads (cf. [Apache Spark's data frame transformation](https://kb.databricks.com/data/chained-transformations.html)).

While working with some complex JSON data recently, I realized that the tools I had available for filtering and transforming that data were awkward. I wanted to stay in bash (vs an ipython shell or a standalone script just for this processing) because of all the other tools available in bash, but I wasn't very excited about parsing data with sed, awk, and xargs.

* I've already written [a tool to avoid complex sed expressions in the past](https://gist.github.com/turtlemonvh/0743a1c63d1d27df3f17), mostly to avoid all the escaping necessary with `sed`.
* I have written `awk` programs that are 10s of lines long, now I tend to just jump over to python when I want to do more complex processing.
* `xargs` is pretty awesome, but the syntax has a lot of gotchas once you start wanting to compose more complex expressions from a line of input.

Inspired in part by [ammonite (scala)](https://ammonite.io/) and [xon.sh (python)](https://xon.sh/), I wanted to be able to use a batteries-included programming language alongside bash to get things done. What I put together started out as ~50 lines of python and has since grown a bit to add more features (esp. multi-expression python and multiprocessing for parallel computation), but it is still small enough to live as [a single file gist](https://gist.github.com/turtlemonvh/4558b8bc4377b6758e289316c0141d15).

The tool is called `pype` (for python pipe). The name is, unsurprisingly, already used by a few projects, none of which are terribly active:

* [python-pype](https://pypi.org/project/python-pype/), similar to this project (bash + python)
* [pype](https://github.com/sup/pype), a pipe-like constructor for python operations
* [PyPE](https://pypi.org/project/PyPE/), an editor
* More on github: https://github.com/search?q=python-pype

The source code and docs are included below. I'll be using this and likely adding to it over time. If it becomes part of my workflow I'll move it from a gist to a normal github repo, and add some tests and some packaging.

Let me know what you think by commenting below or reaching out on Twitter!

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">A small <a href="https://twitter.com/hashtag/python?src=hash&amp;ref_src=twsrc%5Etfw">#python</a> script for filtering and transforming data in <a href="https://twitter.com/hashtag/bash?src=hash&amp;ref_src=twsrc%5Etfw">#bash</a> pipes with inline python<a href="https://t.co/D19LjkOGq5">https://t.co/D19LjkOGq5</a><br>Created because even though jq and awk are awesome python is just easier for some tasks. 😀</p>&mdash; Timothy Van Heest (@turtlemonvh) <a href="https://twitter.com/turtlemonvh/status/1255515592330805251?ref_src=twsrc%5Etfw">April 29, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

<script src="https://gist.github.com/turtlemonvh/4558b8bc4377b6758e289316c0141d15.js"></script>
