Title: Elastic Beanstalk for personal projects: a quick experience report
Date: 2019-04-13 10:00
Tags: alexa, elasticbeanstalk, aws, biblescholar, pricing
Status: published

I have been running the backend of [the BibleScholar Alexa App](https://www.amazon.com/Timothy-Van-Heest-Bible-Scholar/dp/B01N4JOMQ3) on [Amazon's Elastic Beanstalk service](https://aws.amazon.com/elasticbeanstalk/) since late 2016. Now that I'm about to start up a couple other personal projects on AWS, I wanted to come back around and discuss what I liked or didn't like about running this application using this service.

## Good: low maintenance

After just a few issues (e.g. [with health checks](/basic-vs-enhanced-health-checks-on-aws-elb.html)), the application has worked very reliably. I do not have to spend any time on operations or management.

Granted, this is helped by the fact that the application is very simple, and load is small and steady.

## Good: batteries included

The Elastic Beanstalk service is packed with a lot of good default features, and some of these have been particularly helpful.

The managed TLS certificates feature via [AWS ACM](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html) is awesome.  You create certificates for domains in AWS ACM, and all certificates are rotated and managed for you. Public certificates are [completely free](https://aws.amazon.com/certificate-manager/pricing/) (you pay only for the resources protected by the certificates).  [Attaching a certificate to an Elastic Beanstalk load balancer](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-elb.html) is trivial.

Having quick and easy access to [application logs](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.logging.html) and [metrics](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environment-health-console.html) has also helped debugging the few times I have needed to do that.

The [zero downtime deployment features of Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.rolling-version-deploy.html) are nice since I have almost no concern about when I update the application.  The visualizations and feedback in the console showing the states the application is moving through and it updates are also pretty great. I usually have a strong preference for automation and cli applications, but for something I use so seldom, the confidence I get by seeing things working in a UI is pretty great.

## Bad: Cost

Elastic Beanstalk comes with batteries included, but that also means that you have to pay for all those batteries, even when you don't need them. When you are running a service with a small amount of load, the "constant factor" costs become a significant portion of the your total operational costs.

For example, here are the costs for running my application for March 2019. Any costs not listed here were a few cents or in the free tier. Note that you can find a similar breakdown for any service you are using at https://console.aws.amazon.com/billing/home.

<img src="/images/aws_ebs_201903_ec2_costs.png" alt="EC2 costs" style="width: 100%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

<img src="/images/aws_ebs_201903_config_costs.png" alt="Config costs" style="width: 100%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

The [AWS Elastic Beanstalk pricing page](https://aws.amazon.com/elasticbeanstalk/pricing/) links to calculators where you can work out your expected costs, but it is certainly not *obvious* that you will be paying $18/mo just for a load balancer, and $8 for configuration management (something I have never really used for anything).

The cost of running the actual compute load powering my service is very small compared to the cost of running the load balancing and configuration services for that application, esp. since I am running just a single `t2.micro` most of the time.

In practice these extra costs haven't been a tremendous problem for me since AWS has a nice stipend program for Alexa App developers.  Almost every month I get $100 in credits, so I haven't had a non-zero AWS bill in over a year.  But for side projects where I won't be getting these stipends, the cost of Elastic Beanstalk is hard to justify, esp. when compared to alternatives like the excellent combination of [AWS Lambda](https://aws.amazon.com/lambda/) and [API Gateway](https://aws.amazon.com/api-gateway/).

## Conclusion

For my next series of side projects, I will probably compose the web tier using AWS Lambda and API Gateway so I have a lower fixed cost. Even for [the Biblescholar project](https://github.com/turtlemonvh/biblescholar), I will probably refactor to this lower cost (and I *think* even lower maintenance) option.

However, if I do have a need to deploy a more traditional application that I expect to consume larger amounts of load, I won't hesitate to consider Elastic Beanstalk for future projects. If I am running larger pools of larger instances, those constant factors for cost matter a lot less, and nice built-in features like blue-green deployment automation means there is a decent amount of code I don't need to write.
