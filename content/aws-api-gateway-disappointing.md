Title: AWS API Gateway: first impressions are disappointing
Date: 2018-02-27 17:00
Tags: aws, apigateway, rest
Status: published

When I started working with Amazon's [API Gateway service](https://aws.amazon.com/api-gateway/) earlier today, this is not the title I expected the article would have.

If you read through documentation and blog articles by Amazon, it sounds like API Gateway is an awesome solution for serverless integrations with [S3](https://docs.aws.amazon.com/apigateway/latest/developerguide/integrating-api-with-aws-services-s3.html), [DynamoDB](https://aws.amazon.com/blogs/compute/using-amazon-api-gateway-as-a-proxy-for-dynamodb/), [Kinesis](https://docs.aws.amazon.com/apigateway/latest/developerguide/integrating-api-with-aws-services-kinesis.html), and even [SQS](https://medium.com/@gayanhewa/api-gateway-and-service-proxy-with-sqs-2699c6960690).

However, when I started work on some simple integrations I quickly hit significant roadblocks.

## What was I trying to build

I was working on an example integration of API Gateway with S3.

I wanted to create a REST API where users would be able to read and write from paths in a bucket with a prefix based on their username.  In the demo, I was pulling the user's username from a request parameter, but I was planning on changing that over to use an authenticated Google username via [AWS Cognito federated identities](https://docs.aws.amazon.com/cognito/latest/developerguide/google.html).

There was a bit more to the plan than that, but that's all I was starting with. Read and write at a path relative to a prefix. Return either a JSON list of objects or an object itself.  Nothing fancy, so I assumed this would be a very simple integration.

## Problem 1: Lack of support for XML parsing

Many of the AWS endpoints return XML responses.  API Gateway deals almost excusively with JSON, and provides no facilities for working with XML except for passing XML response through unmodified.

Handling XML may be on the product team's roadmap, but [it doesn't seem to be a high priority issue](https://stackoverflow.com/questions/40325005/how-do-i-convert-xml-to-json-aws-api-gateway).  Without XML support, integrating with S3 to produce an API that can list objects in a bucket and return a JSON representation of that list is not possible without resorting to a lambda function to glue things together.

## Problem 2: Inability to template anything except for the request body

Many APIs require passing parameters outside the request body to get things done.  For example, the AWS S3 REST API [only accepts query parameters](https://docs.aws.amazon.com/AmazonS3/latest/API/v2-RESTBucketGET.html) uses only query parameters to list items.

However, API Gateway does not provice any way to set headers or query parameters in a request except for 

* copying fields 1:1 from headers, query parameters, or path components in the request body
* setting a constant string

There is no form of templating supported, so even simple changes to a query parameter ([like adding a prefix](https://stackoverflow.com/questions/49016313/how-to-append-a-prefix-to-a-querystring-parameter-in-aws-api-gateway)) are not supported.

## Problem 3: Painful changes to API design

> I can give AWS a bit of a break here since they seem to be [pushing users toward Swagger definitions for APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-swagger-extensions.html), and using Swagger and batch importing an API definition as it changes may have helped avoid some of these issues.  However, I find that often when just exploring a new technology the UI often helps me discover the best patterns for using a tool, so I wanted to give the web console for as many actions as possible.

I wanted to rename an api resource from `{folder}` to `{item}`. [The `{`s are needed to capture parameters from the url path](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-method-settings-method-request.html#setup-method-resources).  There was nothing on the web console that allowed me to rename a resource (a pretty common operation when working on an API design!).

After a bit of Googling around, I found [other people complaining about the same thing](https://forums.aws.amazon.com/thread.jspa?threadID=215649), then a reference to [a fix using the cli](https://forums.aws.amazon.com/thread.jspa?messageID=731761&#731761).  Awesome!  I mean, maybe a rename button would be nice but I'm fine with a CLI.

However, when I went to run the command to make the change, I ran into issues.  First, running the command requires passing a series of patches with the fields `op`, `path`, `value`, and `from`.  The documentation for what these mean is [sparse](https://docs.aws.amazon.com/cli/latest/reference/apigateway/update-resource.html).  Thankfully one of the examples was demonstrating exactly what I wanted to do, so I was able to use that as a starting point.  Secondly, I ran into an issue getting the command to run.  I'll let my command history speak for itself.

    #!bash
    ## >> In these examples, the API and Resource IDs have been changed to XXXXXXX and YYYYY.

    # I do want to rename it to `{item}`, but I kept getting errors about the brackets.
    # I tried quoting with single quotes and double quotes and got the same error.
    $ aws apigateway update-resource --rest-api-id XXXXXXX --resource-id YYYYY --patch-operations op=replace,path=/pathPart,value={item}

    Error parsing parameter '--patch-operations': Expected: '=', received: '}' for input:
    op=replace,path=/pathPart,value={item}
                                         ^
    # I tried w/o brackets, it works!
    is-mbp-timothy:lambda timothy$ aws apigateway update-resource --rest-api-id XXXXXXX --resource-id YYYYY --patch-operations op=replace,path=/pathPart,value=item
    {
        "parentId": "XXXXXXX",
        "resourceMethods": {
            "GET": {},
            "PUT": {}
        },
        "id": "YYYYY",
        "pathPart": "item",
        "path": "/item"
    }

    # So I figured maybe it was a parsing error (e.g. they add the value into a json string without wrapping it first)
    # Thankfully they provided another api where you can do the formatting yourself
    # My payload is as follows (constructed using the `--generate-cli-skeleton` flag)
    $ cat tmp.json
    {
        "restApiId": "XXXXXXX",
        "resourceId": "YYYYY",
        "patchOperations": [
            {
                "op": "replace",
                "path": "/pathPart",
                "value": "{item}"
            }
        ]
    }
    # Success!
    $ aws apigateway update-resource --cli-input-json "$(cat tmp.json)"
    {
        "resourceMethods": {
            "PUT": {},
            "GET": {}
        },
        "pathPart": "{item}",
        "parentId": "XXXXXXX",
        "path": "/{item}",
        "id": "YYYYY"
    }

The fact that such a simple change requires so many steps is a strong indicator of a lack of maturity in API Gateway.

## Problem 5: Testing

Testing was both kind of awesome and not quite as awesome as I hoped.

When you click down to any method on a resource, there is an option to test.  When you click on "test", you are taken to [a page where you can fill in request parameters and run a test request](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-test-method.html).  This was invaluable for testing my GET methods and working through authorization issues.

However, there were 2 limitations I hit quickly.

* Even though [you can send binary data to API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-payload-encodings-configure-with-console.html), you cannot send binary data in a test request in the console.  You have to send a body that you can paste into a text box.  Considering how common it is to add an option to upload a file to test something, this seems like a pretty strange oversight.
* Request headers are trimmed.  I mean, the WHOLE PURPOSE is debugging.  Throwing away a large chunk of important request data is a strange design choice.

## Conclusion

Overall, I was frustrated by how difficult it was to build out an API with API Gateway.  I came into this with high expectations, thinking that my simple example was something I would be able to throw together in a couple hours.  In reality I spent most of a day working on something which still doesn't work yet.

I will probably still try to use API Gateway going forward.  The integration with DynamoDB looks to be a little stronger, and I think that putting authentication into API Gateway will make some of the solutions I am working on easier to assemble.  Now, however, I think my expectations are a bit lower.  I expect that I will need to move most non-trivial logic into lambda functions, and just lean on API Gateway for a small part of its feature set.

As I continue working with API Gateway, I'll come back here to add additional posts about any useful patterns or techniques I learn, features that solve some of these problems or other problems, or just interesting use cases.
