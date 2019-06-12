Title: HTTP redirects via AWS API Gateway and Lambda
Date: 2019-05-25 18:00
Modified: 2019-05-27 10:00
Tags: api, dns, aws-api-gateway, aws-lambda, this-blog
Status: published

> This article is a bit messy since I'm experimenting with less editing to get content out a little faster for smaller projects. Feedback on the value of this format would be helpful, e.g. if it is too messy to be coherent / useful.

Instead of purchasing new custom domains for each of my side projects, I decided to start hosting more resources under 1 common domain name.  I purchased `vhtech.net` for this purpose.

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

> **UPDATE 20190526**: I ended up using CloudFront in front of my API so I could get `http -> https` redirects working, which meant that I didn't need the API Gateway custom domain. If you want to handle `http` in addition to `https` (either as a redirect or actually serving `http` requests), I recommend skipping the custom domain steps (5 and 6) and going straight to CloudFront (see the update section from 2019/05/26, below).
>
> You will still need the [ACM certificate](https://aws.amazon.com/certificate-manager/) either way (assuming you want to serve requests for your domain over https), so you should still complete that setup step.
>
> If you don't need to handle http and https, however, custom domains are a good option that allow you avoid having to pay for API Gateway *and* CloudFront.

### 1. Create Lambda function

See the description above.

### 2. Create API Gateway integration

As I mentioned above, I started out by setting up the API via AWS Lambda, which ensured the relevant IAM policies and roles were created.  This is nice since I have found that IAM roles and policies are usually the thing that I'm most likely to mess up when gluing services together in AWS.

### 3. Get rid of the "default" API resource

When creating the API via Lambda, a resource is created for you under the API root. We want to get rid of that.

Instead, add a new resource of type `proxy` directly under the root.  The path component should look like: `/{proxy+}`. Don't forget to deploy the changes to the API after making your changes.

> **UPDATE 20190526**: I later realized that I also should have created an `ANY` method on the `/` resource (in addition to the `proxy` resource) to handle redirects in the case of no path. So make sure you add the methods on `/` if you want to handle zero-length paths.

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

<img src="/images/blog-redirect-via-aws/Amazon_API_Gateway_https_only.png" alt="API Gateway is HTTPS only" style="width: 100%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

While it would be possible to [handle the redirect via CloudFront](https://stackoverflow.com/a/47373353/790075), I decided to take the first step to make this site work with TLS/https.

It turns out this is quite simple, and it is [actually the default behavior for newer repos](https://help.github.com/en/articles/securing-your-github-pages-site-with-https#enforcing-https-for-your-github-pages-site).

I just had to go into settings for [the github repo hosting this blog](https://github.com/turtlemonvh/turtlemonvh.github.io) and flip the following switch.

<img src="/images/blog-redirect-via-aws/enforce_tls.png" alt="enforce tls" style="width: 75%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

I also had to change my [pelican](https://blog.getpelican.com/) settings in `pelicanconf.py` to use `https://turtlemonvh.github.io/` as the `SITEURL` instead of `http://turtlemonvh.github.io/`.

Now I'm all `https`.  Github pages *does* handle the http to https redirect for me, so at least that bit works as expected even though `blog.vhtech.net` doesn't respond to `http` requests.

## Update: 2019/05/26 (v2)

After adding that last update I checked [the pricing page for CloudFront](https://aws.amazon.com/cloudfront/pricing/) and saw that the free tier includes 2 million requests per month.

Since I haven't messed with CloudFront yet and I'm starting to spend time gearing up to take the [AWS Certified Solutions Architect](https://aws.amazon.com/certification/certified-solutions-architect-associate/) exam this July, I figured this is a great excuse to learn a little about this service.

So picking up with [that StackOverflow post I mentioned in the previous update](https://stackoverflow.com/a/47373353/790075), I visited CloudFront in the console and clicked the button to `Create Distribution`. I selected the default distribution of type `Web` then clicked the `Get Started` button, which dumped me in a large `Create Distribution` form.  In that form, I set the following values:

> After I did this myself, I found this article from AWS describing how to set up CloudFront and API Gateway, which may be useful for other people trying this in the future:
> https://aws.amazon.com/premiumsupport/knowledge-center/api-gateway-cloudfront-distribution/

* Grabbed the API Gateway invoke url from the `Default` stage view in the console and entered that in the settings page in the `Origin Domain Name` and `Origin Path` boxes
* Updated `Origin Protocol Policy` to `https` (since that is all that API Gateway supports)
* Updated `Allowed HTTP Methods` to include `Options` in addition to `Head` and `Get`
* Set `Cache Based on Selected Request Headers` to `None` since the headers sent by the client should never influnce the response (only the `path` matters)
* Set `Object Caching` to `Use Origin Cache Headers`; this means I can set [`Cache-Control` headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control) in my lambda function or API Gateway to customize cachine behavior
* Set `Default TTL` to `86400` (1 day); this is what will be used if no `Cache-Control` headers are send by my origin
* Set `Forward Cookies` to `None` since I don't need to authenicate requests
* Set `Query String Forwarding and Caching` to `None` since pages on my blog are not defined by query params (only the path)
* Set `Compress Objects Automatically` to `No` since I am not planning on actually serving files via CloudFront (just returning redirects)
* Left `Price Class` set to `All` since there is no extra charge for using more locations; the total request count is aggregated across all locations for the free tier
* Added `blog.vhtech.net` to `Alternate Domain Names`
* Set `SSL Certificate` to use the certificate I created in ACM for `blog.vhtech.net`
* Kept `Custom SSL Client Support` and `Security Policy` (TLS settings) at their default values (e.g. SNI only)
* Left `Default Root Object` empty, and left logging turned off

Here is what that giant form looked like in the AWS console.

<img src="/images/blog-redirect-via-aws/AWS_CloudFront_Management_Console_1.png" alt="CloudFront Management Console 1" style="width: 75%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>
<img src="/images/blog-redirect-via-aws/AWS_CloudFront_Management_Console_2.png" alt="CloudFront Management Console 2" style="width: 75%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

Once I updated those settings, I clicked the `Create Distribution` button on the bottom of the form. That took me to a status page where I could check on the status of my new distribution.

I waited until the CloudFront distribution showed `Status` of `Deployed` (this [took >15 minutes](https://forums.aws.amazon.com/thread.jspa?threadID=237248)), then I updated the `DNS` `A` record I created for `blog.vhtech.net` to point to API Gateway to point to the CloudFront distribution url (the record type is still a `A` record alias).

I thought that, since I added a CNAME of `blog.vhtech.net` when creating the CloudFront distribution, CloudFront would add the DNS records for me, but this was not the case. The `A` record was there unchanged after the CloudFront distribution launched, and I had to update it manually.

... but even after I did all above I ran into *another* issue.

My CloudFront distribition url, `d7v7skc7xxa1j.cloudfront.net`, still returned `missing authentication token` when I hit `http://d7v7skc7xxa1j.cloudfront.net` (which did properly redirect to `https`). Going to `http://d7v7skc7xxa1j.cloudfront.net/a` did properly redirect to `https://turtlemonvh.github.io/a`. I thought this may be because of how API Gateway handles the `stage` portion of its urls, or because I didn't set `Default Root Object` in my CloudFront configuration, but when I looked more into the documentation, neither of these theories panned out.

Here are the redirect chains I was seeing for `curl -LI http://blog.vhtech.net/a`.

```
HTTP/1.1 301 Moved Permanently
Server: CloudFront
Date: Sun, 26 May 2019 20:57:35 GMT
Content-Type: text/html
Content-Length: 183
Connection: keep-alive
Location: https://blog.vhtech.net/a
X-Cache: Redirect from cloudfront
Via: 1.1 4eb6db543899d63048055031c3411b01.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 9zT3MdPoKJ4vhyiSd5n3W8v6WfYcoDmGVQG2-k0etg7UthnMrvbelw==

HTTP/1.1 301 Moved Permanently
Content-Type: application/json
Content-Length: 0
Connection: keep-alive
Date: Sun, 26 May 2019 20:56:02 GMT
x-amzn-RequestId: ac053546-7ff8-11e9-8c14-63ee0d562e8e
Access-Control-Allow-Origin: *
x-amz-apigw-id: aTyHaHHuIAMFiKw=
Location: http://turtlemonvh.github.io/a
X-Amzn-Trace-Id: Root=1-5ceafd62-b41390d052c8716845179af8;Sampled=0
Age: 93
X-Cache: Hit from cloudfront
Via: 1.1 1c1b89f1f3c38ed1685254901bc8fb2d.cloudfront.net (CloudFront)
X-Amz-Cf-Id: XUPJC2iPgcM36P8jzWj49s3sC0KVceusch-vJEJ6PYq6Io7j4Xx4Eg==

HTTP/1.1 301 Moved Permanently
Server: GitHub.com
Content-Type: text/html
Location: https://turtlemonvh.github.io/a
X-GitHub-Request-Id: 7D64:097A:227A7A1:2CF784A:5CEAFD5C
Content-Length: 178
Accept-Ranges: bytes
Date: Sun, 26 May 2019 20:57:35 GMT
Via: 1.1 varnish
Age: 93
Connection: keep-alive
X-Served-By: cache-fty21334-FTY
X-Cache: HIT
X-Cache-Hits: 1
X-Timer: S1558904256.598708,VS0,VE0
Vary: Accept-Encoding
X-Fastly-Request-ID: 7bc012ee4bdcbc6a04bb43a60a854ca2e09491c6

HTTP/1.1 404 Not Found
Server: GitHub.com
Content-Type: text/html; charset=utf-8
ETag: "5cc0aee0-247b"
Access-Control-Allow-Origin: *
Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'; img-src data:; connect-src 'self'
X-GitHub-Request-Id: 7012:50DA:200D22B:29F3365:5CEAFD60
Content-Length: 9339
Accept-Ranges: bytes
Date: Sun, 26 May 2019 20:57:35 GMT
Via: 1.1 varnish
Age: 93
Connection: keep-alive
X-Served-By: cache-fty21350-FTY
X-Cache: HIT
X-Cache-Hits: 1
X-Timer: S1558904256.846499,VS0,VE0
Vary: Accept-Encoding
X-Fastly-Request-ID: 2d7005d30627ba7d9b953c37aee457d6ec6a3048
```

Contrast that with what we see when we do `curl -LI http://blog.vhtech.net/`.

```
HTTP/1.1 301 Moved Permanently
Server: CloudFront
Date: Sun, 26 May 2019 22:46:23 GMT
Content-Type: text/html
Content-Length: 183
Connection: keep-alive
Location: https://blog.vhtech.net/
X-Cache: Redirect from cloudfront
Via: 1.1 2049bafbdd2d1f88e039f5995c93088a.cloudfront.net (CloudFront)
X-Amz-Cf-Id: NIVeaHPk_0vDc-lmCygVoLvdwl_8bPV7M34ZAegocGzJRc0V7GQuUQ==

HTTP/1.1 403 Forbidden
Content-Type: application/json
Content-Length: 0
Connection: keep-alive
Date: Sun, 26 May 2019 22:46:23 GMT
x-amzn-RequestId: 1664cfb9-8008-11e9-ab15-6b983bb47f65
x-amzn-ErrorType: MissingAuthenticationTokenException
x-amz-apigw-id: aUCR7Fy1IAMFpBQ=
X-Cache: Error from cloudfront
Via: 1.1 77b355e48e983a9f568a89f4dbebf383.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 411tPFqGdyHOFjJb7YWas8OCssEXNiak6CPl_Y2A020t9F7EEyZyWw==
```

After more digging, I noticed this on text on page that API Gateway shows in the console when attempting to create a new resource.

> To handle requests to /, add a new ANY method on the / resource.

<img src="/images/blog-redirect-via-aws/API_Gateway_ANY_method_root.png" alt="ANY method on /" style="width: 75%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

After adding `ANY` and `OPTIONS` methods to the `/` resource and deploying the changes to the API, I see the following for `curl -LI http://blog.vhtech.net/`.

```
HTTP/1.1 301 Moved Permanently
Content-Type: application/json
Content-Length: 0
Connection: keep-alive
Date: Sun, 26 May 2019 23:30:48 GMT
x-amzn-RequestId: 4b08402c-800e-11e9-93fb-37487883e1b4
Access-Control-Allow-Origin: *
x-amz-apigw-id: aUIyYGsyoAMFgzA=
Location: http://turtlemonvh.github.io/
X-Amzn-Trace-Id: Root=1-5ceb21a8-d2af9bc886fa43bc4f42971b;Sampled=0
Age: 161
X-Cache: Hit from cloudfront
Via: 1.1 0a576c2dd3353021ea1e162ded4d3a7d.cloudfront.net (CloudFront)
X-Amz-Cf-Id: 2tcrphTEEMvM71W-48mVX3db_6NI5FM8vNvsy0hiYo3LmjyNiVCYTg==

HTTP/1.1 301 Moved Permanently
Server: GitHub.com
Content-Type: text/html
Location: https://turtlemonvh.github.io/
X-GitHub-Request-Id: B968:0FB6:60B7C1:7F24DE:5CEB2192
Content-Length: 178
Accept-Ranges: bytes
Date: Sun, 26 May 2019 23:33:29 GMT
Via: 1.1 varnish
Age: 176
Connection: keep-alive
X-Served-By: cache-atl6221-ATL
X-Cache: HIT
X-Cache-Hits: 1
X-Timer: S1558913610.918408,VS0,VE0
Vary: Accept-Encoding
X-Fastly-Request-ID: b6a3eb53b8ceeed706fdd6a4e014727d29343fe5

HTTP/1.1 200 OK
Server: GitHub.com
Content-Type: text/html; charset=utf-8
Last-Modified: Sun, 26 May 2019 19:31:17 GMT
ETag: "5ceae985-4071"
Access-Control-Allow-Origin: *
Expires: Sun, 26 May 2019 23:40:34 GMT
Cache-Control: max-age=600
X-GitHub-Request-Id: 83B2:33ED:10C3628:1569AA0:5CEB2195
Content-Length: 16497
Accept-Ranges: bytes
Date: Sun, 26 May 2019 23:33:29 GMT
Via: 1.1 varnish
Age: 176
Connection: keep-alive
X-Served-By: cache-atl6233-ATL
X-Cache: HIT
X-Cache-Hits: 2
X-Timer: S1558913610.992689,VS0,VE0
Vary: Accept-Encoding
X-Fastly-Request-ID: dd197651fb8823a9113cb41c2479dedc7ecf026a
```

This is the `http://blog.vhtech.net -> https://blog.vhtech.net -> https://turtlemonvh.github.io` chain we're looking for!

I think I had missed this a few times earlier in my testing because my original distribution *did* include the appropriate resources on the root object, and [I *think* my browser was caching the 301 responses I was sending](https://stackoverflow.com/questions/9130422/how-long-do-browsers-cache-http-301s), so browser testing looked fine when requesting with path `/` even though using `curl` gave a different result (e.g. `403` vs `200`). So a note for those who follow (including my future self!): watch out for caching when setting up these resources.

Also, the API Gateway custom domain ended up being completely unnecessary after setting up CloudFront, so I deleted that once I confirmed CloudFront was returning responses as expected.

So, now with total time closer to 3 hours and using 4 different services (ACM, API Gateway, CloudFront, and Lambda), I have accomplished a very simple task. `blog.vhtech.net` redirects to `turtlemonvh.github.io`, handling both `http` and `https`.

However, I did get to learn more about each of these services along the way, so I'll chaulk this one up as a partial win. <span>&#128512;</span>

### Pricing

Some quick notes on pricing I put together while waiting for CloudFront to deploy. These are the services I used:

* https://aws.amazon.com/api-gateway/pricing/
* https://aws.amazon.com/cloudfront/pricing/
* https://aws.amazon.com/lambda/pricing/
* https://aws.amazon.com/certificate-manager/pricing/

Some notes on each

* API Gateway, CloudFront, and Lambda are all in the free tier when there are <1M requests per month.
* ACM is free for public certs. Given the simple integration with AWS services and the fact that AWS handles annoying details like [cert renewal](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html) for you automatically, I strongly recommend using the service.
    * See [this article](/setting-up-ssl-for-an-elasticbeanstalk-application.html) for more notes on my previous experience with ACM and Elastic Beanstalk.
* CloudFront costs <$0.01 per 10K requests when out of the free tier, but per request price about doubled when requests are https vs http. Data costs are negligible for the small responses I am sending. I am not making active cache invalidation requests, so I don't expect any charges there.
* API Gateway costs ~$3.5/M requests, or about 1/3rd the cost of each CloudFront request. This price difference was a bit surprising to me, since I expected CloudFront to be cheaper. I am not using API Gateway caching, so I don't have to deal with that part of pricing.
* Lambda per-request costs are $0.20/M, so significantly less than API Gateway and CloudFront. However you also pay for gb-seconds for the lambda runtime. I am using [the smallest available size (128 mb)](https://docs.aws.amazon.com/lambda/latest/dg/limits.html) and doing minumum computation, so I do not expect to exceed the fre tier of 400,000 GB-s.

