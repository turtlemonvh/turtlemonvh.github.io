Title: Projects
Date: 2016-01-02 09:30
Author: Timothy Van Heest
Slug: projects
Status: published

A list of open-sourced things I have worked on recently.

# Large projects

These are projects that are either very long term and complex or just provide useful end-to-end functionality.

## [BibleScholar](https://github.com/turtlemonvh/biblescholar) (started 2016)

A tool for providing search of the Bible via an [Alexa](https://developer.amazon.com/alexa) compatible api.

I have some articles about building that under the [`biblescholar` tag](/tag/biblescholar.html).

## [Blanket](https://github.com/turtlemonvh/blanket-api) (started 2015)

A tool for wrapping long running processes in a REST API (blanket = RESTy wrapper, get it?).  I use this every day at work, but it's still a bit too raw for general use.  There is a UI component that isn't bundled into the main application yet.

<img src="/images/blanket-ui-screenshot.png" alt="Blanket UI" style="height: 300px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

## [traffic-monitor](https://github.com/turtlemonvh/traffic-monitor) (started 2014)

A python application for scraping traffic information off Google maps on a schedule. You enter a route for going and coming, and the tool starts to collect Google's estimates on how long it will take to travel that route.  I used it when looking for houses to find a place in Atlanta where traffic wouldn't be terrible.  I also put together [a companion visualization tool](http://turtlemonvh.github.io/traffic-monitor/).

<img src="/images/traffic-timer-plots.png" alt="Traffic Timer Plots" style="height: 300px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

# Smaller Utilities

These are smaller components that are generally used to meet a very specific need for library code.  I also add a lot of [gists on github](https://gist.github.com/turtlemonvh) that fill this same purpose.

## [tnnlr](https://github.com/turtlemonvh/tnnlr) (started 2017)

A tool for managing ssh tunnels for projects. Originally developed to make it easy to port-forward admin interfaces for various monitoring tools.

## [gin-wraphh](https://github.com/turtlemonvh/gin-wraphh) (started 2016)

A small utility for wrapping some types of middlewares for use in the go gin web framework.

## [prometheus_python_roller](https://github.com/turtlemonvh/prometheus_python_roller) (started 2016)

A python tool for rolling [prometheus](https://prometheus.io/) metrics into time-windowed moving averages.  Makes it easy to use the [prometheus python library](https://github.com/prometheus/client_python) to collect metrics for monitoring an application but still provide those metrics to a system like Nagio's [checkmk](http://mathias-kettner.com/check_mk.html) that doesn't deal with infinitely growing metrics so well.

## [altscanner](https://github.com/turtlemonvh/altscanner) (started 2016)

A not very efficient but very easy to use alternative to go's [bufio.Scanner](https://golang.org/pkg/bufio/#Scanner) that works for lines of any length.

## [dns-zero-ttl](https://github.com/turtlemonvh/dns-zero-ttl) (started 2016)

A series of experiments testing how various languages and systems behave when you run DNS with a time to live of 0, which is common when using something like consul for service discovery.