Title: Introducing the BibleScholar Alexa application
Date: 2016-12-31 10:00
Tags: alexa, elasticbeanstalk, aws, bible
Status: published

When I went to the [AWS Re:Invent conference](https://reinvent.awsevents.com/) this November, every attendee got an [Echo Dot](https://www.amazon.com/All-New-Amazon-Echo-Dot-Add-Alexa-To-Any-Room/dp/B01DFKC2SO/).  Since then I've been looking for something useful to do with it.  So far I've been just asking Alexa about the weather, traffic, and (very corny) jokes.

Several of my long term side projects are in the area of [information retrieval](http://nlp.stanford.edu/IR-book/), so I thought that developing a simple search application would be a good way to get a little more experience in this area and develop something I would actually use.

The idea of BibleScholar is that the user will be able to ask the application where in the Bible a certain phrase exists, and it will find that phrase and return the best matching verse.  I may add some more functionality later, but right now that's all it does.  To make that work, I had to follow theses steps.

-----

## 1. Get the full text of a few Bible translations

I needed multiple translations because when you ask for a phrase you will often have heard that verse mentioned a specific way, but it may have come from 1 of many possible translations.

On a more technical level, instead of [stemming](https://en.wikipedia.org/wiki/Stemming) the input text or using a more complex method like [LDA](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation) or [PLSA](https://en.wikipedia.org/wiki/Probabilistic_latent_semantic_analysis) to model the search phrase and actual Bible content as a set of topics, I opted for a more straightforward phrase search over the input text.  This has the advantage of also usually mapping to a single translation, so when you search for a phrase you also find out what translation it came from.

I wrote [some python scripts](https://github.com/turtlemonvh/biblescholar/tree/master/scrape) to crawl [Bible Gateway's site](https://www.biblegateway.com) for this content from the ESV, KJV, NIV, and HCSB translations.

## 2. Index the text

I've been wanting to play around with the [go](https://golang.org/) [bleve search](http://www.blevesearch.com/) library for a while, so I chose to use that.  I wrote [my own code to do the indexing from tsv files](https://github.com/turtlemonvh/biblescholar/blob/master/search/index.go), but I found out later that there is a nice [indexing utility built into the `bleve` command line tool](https://github.com/blevesearch/bleve/blob/master/cmd/bleve/cmd/index.go).  Oh well.  I did find that indexing with bleve was very fast when using large batch sizes.

Once I had it indexed, I could search on the command line using the [`bleve search`](https://github.com/blevesearch/bleve/blob/master/cmd/bleve/cmd/query.go) tool.  Here's what that looks like:

```bash
$ bleve query verses.bleve/ 'for God so loved the world'
11409 matches, showing 1 through 10, took 74.698161ms
    1. John-3-16-KJV (0.725904)
        Text
                For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.
    2. John-3-16-NIV (0.717970)
        Text
                For God so loved  the world that he gave  his one and only Son,  that whoever believes  in him shall not perish but have eternal life.
    3. John-3-16-HCSB (0.710291)
        Text
                “For God loved  the world in this way:  He gave His One and Only  Son,  so that everyone who believes in Him will not perish but have eternal life.
    4. John-13-1-HCSB (0.596986)
        Text
                Before the Passover Festival, Jesus knew that His hour had come to depart from this world to the Father.  Having loved His own who were in the world,  He loved them to the end.
    5. John-13-1-NIV (0.584676)
        Text
                It was just before the Passover Festival.  Jesus knew that the hour had come  for him to leave this world and go to the Father.  Having loved his own who were in the world, he loved them to the end.
```

## 3. Add an Alexa-compatible search endpoint

My 2 favorite libraries for quickly putting together go HTTP services have been [gabs](https://github.com/Jeffail/gabs) (for working with JSON) and [gin](https://github.com/gin-gonic/gin) (for the actual HTTP server).  Using those 2 libraries made this step easy.  The most complicated part was makign sure the endpoint exactly followed [the spec](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/alexa-skills-kit-interface-reference).

## 4. Host it

This was a bit of an adventure.  After doing a lot of research, I decided to go with [AWS ElasticBeanstalk](https://aws.amazon.com/documentation/elastic-beanstalk/) because

* It has [autoscaling](https://aws.amazon.com/autoscaling/), health checks, and [ELB](https://aws.amazon.com/elasticloadbalancing/) integration
* It has easy integrations with [CloudWatch](https://aws.amazon.com/cloudwatch/) Metrics, CloudWatch Logs, and other things that make monitoring easier
* I wanted to play around with it at some point anyway

I found [this YouTube demo video](https://www.youtube.com/watch?v=xhc1boyBkJw&t=292s) pretty helpful for getting started.  But I still ran into a few hiccups.

First, the [`eb` command line tool](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html) couldn't pick up my configuration from `~/.aws/credentials` when I set the [`AWS_DEFAULT_PROFILE` environment variable](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-environment).  Passing in the `--profile` flag directly worked, but I knew I would probably forget to do this at some point when running commands, and I didn't want to use my company account by accident, so I just set all the environment variables I needed (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`) directly when using that tool.

Second, bleve was panicing when I tried to attach the index file as a volume to a running docker container.  At first I thought that this was related to me [cross compiling the linux binary on my mac](https://github.com/turtlemonvh/biblescholar/blob/master/search/Makefile#L43), but when I made [another Docker container that did the build on linux](https://github.com/turtlemonvh/biblescholar/blob/master/search/Dockerfile.build) the panic still occured.

I think this may be related to how [boltdb](https://github.com/boltdb/bolt) (the kv store that bleve uses by default) uses OS-level locking to ensure only 1 process opens the db at a time and the weird way the volumes are working in my setup (I was using [docker-machine](https://docs.docker.com/machine/get-started/) on OSX for these tests), but I'm not really sure.  I still need to come back around and try to see how general this is.  If I can get it panicing reliably I'll submit a bug report.  For now I opted to [just copy the whole index into the container on build](https://github.com/turtlemonvh/biblescholar/blob/master/search/Dockerfile#L22) instead.

Third, I had to set up SSL since [Amazon requires SSL for custom skills](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/testing-an-alexa-skill#h2_sslcert).  This was actually not too bad once I knew what to do.  These are the most helpful pages I found for this:

* [http://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl](http://stackoverflow.com/questions/10175812/how-to-create-a-self-signed-certificate-with-openssl)
    * Gives an example command for generating a self signed cert
    * Note that [AWS ACM](https://aws.amazon.com/certificate-manager/) only supports certain sizes of certs, so I changed `4096` to `2048` in that command
* [https://docs.aws.amazon.com/acm/latest/userguide/import-certificate.html#import-certificate-troubleshooting](https://docs.aws.amazon.com/acm/latest/userguide/import-certificate.html#import-certificate-troubleshooting)
    * That `pem` file you created in the previous step is encrypted with a pass phrase
    * This link tells you how to decrypt it so the private key can be uploaded to AWS ACM
* [http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-elb.html](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-elb.html)
    * Explains how to assign a certificate from AWS ACM to the ELB used by an ElasticBeanstalk app
    * This allows you to configure your ElasticBeanstalk assigned url (e.g. [https://biblescholar-env.us-west-2.elasticbeanstalk.com/](https://biblescholar-env.us-west-2.elasticbeanstalk.com/)) to use HTTPS as well as (or instead of HTTP)

After this all I had to do was open up HTTPS services on port 443 for my app (under `Configuration > Load Balancing` on the web console) and I could hit my app over HTTPs.

## 5. Submit it for review

I has already designed the voice API for the application earlier on [the Alexa skills submission portal](https://developer.amazon.com/edw/home.html#/skills/list).  Now I pointed my configuration back to the HTTPS endpoint of my application and uploaded my self-signed certificate file to the portal and I could test my application.  Hooray!

Right now I'm stuck on the last step because [self signed certs are allowed for testing only](https://forums.developer.amazon.com/questions/51926/submit-for-certification-button-is-not-clickable-d.html) and [my DNS registrar](https://www.1and1.com/) doesn't allow CNAMES for top level domain values (subdomains only) so I need to figure out how to attach an [Elastic IP](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html) to my ElasticBeanstalk app's ELB so I have an address.  Then I can use the [free certificates provided by AWS ACM](https://aws.amazon.com/certificate-manager/pricing/) to secure the application.

When I get that working I'll come back and update this step.

-----

For now, I leave you with [a demo video](https://www.youtube.com/watch?v=Aq0IjjArOyo) of the application working.
