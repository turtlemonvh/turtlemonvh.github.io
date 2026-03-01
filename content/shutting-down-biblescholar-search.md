Title: Shutting down the BibleScholar Alexa application
Date: 2026-03-01 15:00
Tags: alexa, elasticbeanstalk, aws, biblescholar
Status: published

I decided to shut down this Biblescholar application. ( See other articles via [the "biblescholar" tag](https://turtlemonvh.github.io/tag/biblescholar.html))

## Rationale

The first reason: cost. When I put this application together back in 2016, this cost ~$5/mo. But AWS shifted to a much more expensive model for public IPs and ELBs a few years ago. Since then I have been paying >$30/mo for this application, which I ~never use.

Here is the bill for last month.

<img src="/images/biblescholar_aws_bill_2026-02.png" alt="aws bill 1" style="height: 280px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>
<img src="/images/biblescholar_aws_bill_2026-02-2.png" alt="aws bill 2" style="height: 200px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

Oof. That's >$16 for an idle ELB, >$13 for an idle IPv4 address. Then another $10 for the compute and local storage (EBS). Getting charged another $0.50 for the `biblescholar.vhtech.com` hosted zone, then another $60 for config specific to ElasticBeanstalk is also not something I'm fond of. I have better thinkgs to do with $40/mo, thank you very much.

The second reason : obsolecence. With modern LLMs, this skill is no longer needed.

I thought for a while about moving the skill to an AWS Lambda Function, which would make it nearly free to operate, and that's part of the reason I dragged by feet for so long. But honestly this app has served its purpose, and it's time for retirement.

## How

I started by getting access to AWS accounts. I launched this a long time ago in a root account, so it took a while to get access again.

Then I checked charged. Yuck. At least it will be satisfying to fix.

Next I went to ElasticBeanstalk. I switched to us-west-2 (thankfully AWS billing is broken out by region - I forgot why I had launched the app there) and found by app.

<img src="/images/biblescholar-env-decomm-2026-02.png" alt="aws elasticbeanstalk decomm" style="height: 250px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

AWS is not happy about this being up. So I went to "Actions > Terminate Environment".

Next : route53. It turned out I has 2 hosted zones in there.

<img src="/images/aws_routet53_hosted_zones-2026-02.png" alt="aws route53 hosted zones decomm" style="height: 250px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

When I tried to delete, `biblescholarsearch.info` went smootly, but I received an error about "non-required resource sets" for `biblescholarsearch.net`.

Checking it out, I saw I had a few mail related entries in there. I could delete everything buut the NS ans SOA records. Once everything but NS and SOA was deleted, I could delete the zone.

Next is VPC. I see a few resources there. The Elastic IP is the big one, but I'll aim to delete everything.

<img src="/images/aws_vpc_resources_uswest2-2026-02.png" alt="aws vpc decomm" style="height: 250px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

I did the following

* Elastic IP address > Release Elastic IP address
* VPC > Actions > Delete VPC

In both cases there was only 1 entry, so I was confident I was deleting the right thing.

When deleting the VPC, I was presented with this warning, which looks like is a special warning for default VPCs.

> Warning: If you delete this default VPC, you can't launch instances in this Region unless you specify a subnet in another VPC or create a new default VPC.

When I next come back to launching an app in `us-west-2` (possibly never...?) I can tackle this.

For now deleting the whole thing is easy.

I next checked AWS Config. I found some rules there. I had to delete these individually, and type "confirm" each time, which was a bit annoying.

<img src="/images/aws_config_2026-02.png" alt="aws vpc decomm" style="height: 250px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

_( I wasn't 100% sure this was the right service so I also checked AWS App Config, which is part of Systems Manager, and didn't see anything. )_

I think this service is free, but I also remembered to check the "AWS Certificate Manager", which I had used to set up for TLS certs. I did find 2 entries there, both for `biblescholarsearch.net`, and I deleted both.

For final checks (all in `us-west-2`) :

* I looked in "EC2 > Load balancers" and saw nothing listed, since Elasticbeanstalk cleaned up after itself.
* I looked in the EC2 dashboard and saw just 1 terminated instance. I selected to "Terminate (delete)" instance.
  * Maybe Elasticbeanstalk was going to clean this up, but I didn't want it sitting around just in case.
* Checked "EC2 > EBS Volumes" and didn't see anything.
 
Last, I went to the Alexa dev console at https://developer.amazon.com/alexa/console/ask# and I chose to remove my "Bible Scholar" skill.

<img src="/images/aws_alexa-dev-console_decomm-biblescholarsearch_2026-02.png" alt="aws vpc decomm" style="height: 250px; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

Once I clicked "Remove" I saw a new green banner message at the top of the page: 

> We’ve received your request to Remove amzn1.ask.skill.30c203ed-c0f7-432e-bcdb-23ee1ece38ab. Your skill will be removed within 2 hours.

## Conclusion

Hopefully this works and my AWS bill drops down to <$5. I still do have a few other apps doing work, but all are very efficient serverless apps that are nearly free to operate.

A few lessons learned

* As I wrote before, Elasticbeanstalk sounded great, but as the supporting services (public IPs, AWS config, etc) get more expensive it rapidly grew in price.
    * AWS subsidized this for a whole when my app was somewhat popular (even when the pre-month price went >$20, I didn't pay anything for >1 year), but in time it caught up with me.
    * I need to watch out for exposure to such price changes from platforms going forward.
* Just finding time to decommission an app can be hard.
    * I have known this was costing me $$ for a few years, and yet it sat there, doing ~nothing.
    * Today ripping out the whole app and writing this article this took me ~2 hours.
* I'm thankful for a few features in AWS Billing.
    * Granular reporting: It made it fairly easy for me to find what I am being charged for.
    * AWS Billing alerts: That's how I was alerted that prices were going up in the first place!
* Deploying into a separate region was a good idea.
    * Even with the details in billing, it would have been annoying to tell which services belonged to which app.
    * Doing per-app / per-account boundaries may be a good idea going forward, esp if I don't deploy the whole infra using something like Terraform.
* Re-hydrating old tech takes time.
    * Just getting this blog up and running again took ~20 minutes. I was working on a new laptop, so needed to set up a passkey with MFA, create a register SSH keys, clone repos, set up development environments, etc.
    * I am thankful I didn't run into any issues like deprecated python dependencies, and I am thankful I left good breadcrumbs for myself (i.e., documentation on how to set up the blog!)

I hope to have some good excuses to fiddle more with techology going forward as a I recently started a new role in at Visa leading Product for some next generation ML Platforms.