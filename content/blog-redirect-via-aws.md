Title: HTTP redirects via AWS API Gateway and Lambda
Date: 2019-05-25 18:00
Tags: api, dns, aws-api-gateway, aws-lambda, this-blog
Status: published

> This article is a bit messy since I'm experimenting with less editing to get content out a little faster for smaller projects. Feedback on the value of this format would be helpful, e.g. if it is too messy to be coherent / useful.

Instead of purchasing a new custom domains for each of my side projects, I decided to start hosting more resources under 1 common domain name.  I purchased `vhtech.net` for this purpose.

I wanted to make `blog.vhtech.net` redirect to `turtlemonvh.github.io`.  My first attempt was adding a CNAME record, but this didn't work because of cross resource / virtual host issues with the way github serves their pages.  I know that [github pages supports custom domains](https://help.github.com/en/articles/using-a-custom-domain-with-github-pages), but I still want to keep the `turtlemonvh.github.io` address, so I decided to set up a simple http redirect instead.

Also, I figured this would be a nice way to learn a bit more about AWS Lambda functions and API Gateway.  My Lambda function looks like this (which is a port of [this nodejs version](https://gist.github.com/DavidWells/99216c20cdb3df334d5b98ff19644fa2) with a little extra path handling):

```python
import json

def lambda_handler(event, context):
    # https://docs.aws.amazon.com/lambda/latest/dg/with-on-demand-https.html
    path = event['path']
    return {
        'statusCode': 301,
        'headers': {
            'Location': 'http://turtlemonvh.github.io/' + path.lstrip("/"),
            'Access-Control-Allow-Origin': "*"
        }
    }
```

I first tried to set up the API Gateway connection via the Lambda dashboard, but ran into a few issues. API Gateway created a resource like this: `https://s9jkfvzuq2.execute-api.us-east-1.amazonaws.com/default/`

One problem was the `default` in this uri. I wanted to add the Lambda function url (actually the API Gateway url, which calls the Lambda in proxy mode) as a dns entry, so I need the root of the api to be an empty path.

Thankfully AWS has a solution for this via [custom domains](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-regional-api-custom-domain-create.html). (As usual, I stumbled across this option via [a StackOverflow post](https://stackoverflow.com/questions/39523150/aws-api-gateway-remove-stage-name-from-uri)) The process I followed to make this work was the following.

### 1. Create Lambda function

See the description above.

### 2. Create API Gateway integration

As I mentioned above, I started out by setting up the API via AWS Lambda, which ensured the relevant IAM policies and roles were created.  This is nice since I have found that IAM roles and policies are usually the thing that I'm most likely to mess up when gluing services together in AWS.

### 3. Get rid of the "default" API resource

When creating the API via Lambda, a resource is created for you under the API root. We want to get rid of that.

Instead, add a new resource of type `proxy` directly under the root.  The path component should look like: `/{proxy+}`. Don't forget to deploy the changes to the API after making your changes.

### 4. Make sure this works by visiting the API Gateway url

The url should look something like: `https://s9jkfvzuq2.execute-api.us-east-1.amazonaws.com/default/`

While testing, I received the error `missing auth token` several times, and each time it was due to me not correctly capturing the path. Usually this was because I made changes to the API definition but forgot to deploy.  See this discussion for more information: https://forums.aws.amazon.com/thread.jspa?threadID=192977

### 5. Create a custom domain

To start, I had to create a DNS record for `blog.vhtech.net`.  I just created a CNAME record to point to `https://s9jkfvzuq2.execute-api.us-east-1.amazonaws.com` (the base of my API Gatway url). After adding this record, requests like `http://blog.vhtech.net/default` redirected properly.

Next, I had to request an ACM certificate. Because `vhtech.net` is managed by AWS via Route 53, this was easy. I just had to create a DNS TXT record, and there was even a conveinent option to let ACM create the Route 53 resources for me just by clicking a button on the ACM request submission page. After creating the TXT record, it will be a few minutes (2-5) until ACM marks your certificate request with a `Status` of `Issued`.

Once the certificate request is `Issued`, you can create the custom domain for API Gateway. I created a "regional endpoint" using the ACM cert I just created.  Once I created this, API Gateway showed some DNS information I needed to update.  I went back to Route 53 and changed the CNAME record for `blog.vhtech.net` to an A record that is an `alias` pointing to the url provided by API Gateway. At first I had created this as a CNAME record instead of an A record.  This would have worked [according to the docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-regional-api-custom-domain-create.html), but the A name record was nice because after entering the url in the A record alias box, Route 53 shows you the hosted zone of the url you are referencing, which you can confirm lines up with the hosted zone API Gateway reports. Note that you never have to enter the hosted zone id anywhere, but seeing it show up in both places is a nice confirmation that you're on the right track.

### 6. Add base path mapping to custom domain

To route requests from `/` to the `default` stage, I had to create something called a ["base path mapping" for the custom domain](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-regional-api-custom-domain-create.html#create-regional-domain-using-console).

I left the `path` field empty (so everything under `/` is captured), selected my api as `destination`, and selected stage `default`.

After I finished this, the following redirects work as expected:

* `https://blog.vhtech.net` -> `http://turtlemonvh.github.io`
* `https://blog.vhtech.net/` -> `http://turtlemonvh.github.io/`
* `https://blog.vhtech.net/pages/home.html` -> `http://turtlemonvh.github.io/pages/home.html`

In the end, this took about an hour, I have `blog.vhtech.net` redirecting to `turtlemonvh.github.io`, and I learned a bit more about Route 53 and API Gatway in the process, so I'll call the experiment a success.

## Update: 2019/05/26

I had more or less ignored the fact that `blog.vhtech.net` only responds to `https` requests while `turtlemonvh.github.io` only works with `http` requests. This means link 1 works fine and link 2 gives you a mysterious error.

* https://blog.vhtech.net/http-redirects-via-aws-api-gateway-and-lambda.html
* http://blog.vhtech.net/http-redirects-via-aws-api-gateway-and-lambda.html

<img src="/images/blog-redirect-via-aws/blog_vhtech_net_over_http.png" alt="mysterious error" style="width: 50%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

I did a little more research on this topic today, and found that API Gateway does not support http, or even http to https redirects.

<img src="/images/blog-redirect-via-aws/Amazon_API_Gateway_https_only.png" alt="mysterious error" style="width: 100%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

While it would be possible to [handle the redirect via CloudFront](https://stackoverflow.com/a/47373353/790075), I decided to take the first step to make this site work with TLS/https.

It turns out this is quite simple, and it is [actually the default behavior for newer repos](https://help.github.com/en/articles/securing-your-github-pages-site-with-https#enforcing-https-for-your-github-pages-site).

I just had to go into settings for [the github repo hosting this blog](https://github.com/turtlemonvh/turtlemonvh.github.io) and flip the following switch.

<img src="/images/blog-redirect-via-aws/enforce_tls.png" alt="mysterious error" style="width: 75%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

I also had to change my [pelican](https://blog.getpelican.com/) settings in `pelicanconf.py` to use `https://turtlemonvh.github.io/` as the `SITEURL` instead of `http://turtlemonvh.github.io/`.

Now I'm all `https`.  Github pages *does* handle the http to https redirect for me, so at least that bit works as expected.