Title: Comparing Serverless Compute Options Across Cloud Providers
Date: 2016-12-31 10:00
Tags: alexa, elasticbeanstalk, aws, biblescholar
Status: draft


After putting together [a quick gist on pricing of compute options on AWS](https://gist.github.com/turtlemonvh/89ceb82d80bfee10c19db33f45f8a7b4) and then reading a few articles about GCP's new "Cloud Run" service, I wanted to look at the various "serverless" compute options across the major cloud providers.

Here the primary dimensions I want to compare them based on

* price
* use cases
* flexibility
    * ability to bring own libraries, handle compiles code, packaging formats
* semantics
    * how are they invokes and configured
* integration with rest of ecosystem (this is generally good, but we'll see)

After doing my quick survey of AWS' offerings, I felt I had a better feel for where the industry was moving. In general, services that are easier to string together, have more predictable pricing, and allow a richer set of functionality.

A partial motivation here is to understand what gaps the company I work for, Ionic Security, may have in our ability to help secure workloads on each of these platforms.






## Systems in scope

### AWS

#### Lambda

https://docs.aws.amazon.com/lambda/latest/dg/welcome.html

#### Fargate

https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_GetStarted.html

#### Batch

https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html

#### EMR

https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html

#### Glue

https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html

### GCP

#### Cloud functions

https://cloud.google.com/functions/

https://cloud.google.com/functions/docs/writing/
- handles node python and go
- "HTTP functions and background functions"
- the fact that you can process HTTP means you don't need silly things like this
    - https://github.com/slank/awsgi
- it also means that you can handle concurrent execution

#### Cloud Run

https://cloud.google.com/run/

https://read.acloud.guru/the-good-and-the-bad-of-google-cloud-run-34455e673ef5
- I disagree with this article
    - I think cloud run is awesome
    - Maybe kubernetes or something like it is awesome
- the environment is very nice
- I don't pay 100 ms per invocation (like lambda)
- I can benefit from concurrency
    - esp. for go, js, and python async
- I can package things into a container
- I'm less likely to have to worry about warm up (since a single server can handle concurrent requests)
    - see articles about this

https://docs.aws.amazon.com/apigateway/latest/developerguide/configure-api-gateway-lambda-authorization-with-console.html
- apparently the custom authorizer responses *are* cached without having to allocate extra space for the cache
- default is 5 min, but can go up to an hour for cache

https://twitter.com/kelseyhightower/status/1116055726953074688

#### Kubernetes engine

> Similar to Fargate

https://cloud.google.com/kubernetes-engine/pricing
- "Because GKE abstracts away the existence of the master, you are not charged for the master node."
- "GKE uses Google Compute Engine instances for nodes in the cluster. You are billed for each of those instances according to Compute Engine's pricing, until the nodes are deleted. Compute Engine resources are billed on a per-second basis with a 1 minute minimum usage cost."
https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler
- "Beginning with Kubernetes version 1.7, you can specify a minimum size of zero for your node pool. This allows your node pool to scale down completely if the instances within aren't required to run your workloads."
- "A node's deletion could be prevented if it contains a Pod with any of these conditions"
    - "The Pod has local storage"

https://cloud.google.com/kubernetes-engine/docs/tutorials/persistent-disk
- persistent disks tutorial


# Next battles

* AWS Api gateway vs Google Cloud Endpoints
    * https://cloud.google.com/endpoints/
* AWS SWS and Lambda step functions vs ???
    * https://cloud.google.com/free/docs/map-aws-google-cloud-platform
        * nothing maps to either of these
    * https://www.reddit.com/r/aws/comments/87c8ss/any_open_source_alternative_to_aws_step_functions/
        * no great recs here
    * https://fission.io/workflows/
        * this seems to be one, so I'm sure there are others
    * https://github.com/argoproj/argo
        * has workflows
        * implemented as a CRD (custom resource definition)
        * https://argoproj.github.io/docs/argo/demo.html
        * https://argoproj.github.io/docs/argo/examples/readme.html#artifacts
            * handles secrets too
        * powers kubeflow
            * https://www.youtube.com/watch?v=VXrGp5er1ZE&t=0s&index=135&list=PLj6h78yzYM2PZf9eA7bhWnIh_mK1vyOfU
            * which uses this for api gateway: https://www.getambassador.io/
        * questions
            * how is state managed in these state machines?
            * how can we check the progress of workflows independently?
        * https://argoproj.github.io/docs/argo/roadmap.html
            * they are planning on adding support for offloading state to persistence layer (db)
    * https://www.kubeflow.org/
        * uses argo, can also use pachyderm
    * airflow as a kubernetes operator
        * https://kubernetes.io/blog/2018/06/28/airflow-on-kubernetes-part-1-a-different-kind-of-operator/
        * https://hackernoon.com/meet-maat-alibabas-dag-based-distributed-task-scheduler-7c9cf0c83438
    * others
        * pachyderm and nomad (https://github.com/hashicorp/nomad/issues/419#issuecomment-468333207)
    * video
        * https://www.youtube.com/watch?v=M_rxPPLG8pU
* Kubernetes offerings
    * https://cloud.google.com/kubernetes-engine/
        * "Kubernetes Engine clusters are fully managed by Google Site Reliability Engineers (SREs), ensuring your cluster is available and up-to-date"
        * "Built-in dashboard"
    * which ones have dashboards, require managing state, have flexibility, etc
* Managed SQL
    * https://cloud.google.com/products/big-data/
        * BigQuery
    * Redshift
* Stream processing
    * Dataflow + Cloud PubSub
        * https://cloud.google.com/products/big-data/
        * https://cloud.google.com/dataflow/docs/concepts/beam-programming-model
    * Kinesis data analytics (Flink)
* Build tools
    * https://cloud.google.com/cloud-build/
        * easy to push to docker hub
        * generous free tier
* Container registries
* Log management
    * Amazon CloudWatch Logs
    * Stackdriver logs
    * Amazon's ELK + new timeseries database
