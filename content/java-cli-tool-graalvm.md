Title: Java CLI tools with GraalVM: An experience report
Date: 2020-05-07 23:00
Tags: jvm, cli, graalvm
Status: published

Over the last few years I have used several CLI tools written in java.  Usually these have been utility tools packaged with JVM applications, like kafka. The slow startup time from the JVM (and general bloatiness) of these tools has made me wholly uninterested in the JVM as a tool for CLI applications.

But a few years ago I heard about [the graalvm project](https://www.graalvm.org/) and its efforts to produce native images from JVM bytecode. Since then, I've been looking for an excuse to play around with the project.  This week I finally found one when we were discussing packaging for a java-based CLI tool developed at Ionic: [the cloud copy tool](https://github.com/IonicDev/ionic-cloud-copy-tool).

To get started, first I downloaded the tarballs for java8 and java11 from [the graalvm github releases page](https://github.com/graalvm/graalvm-ce-builds/releases/tag/vm-20.0.0).


```bash
# I took a more manual approach, but this may be a simpler approach to install if you are less concerned with homebrew mucking with your Java settings
# https://github.com/graalvm/homebrew-tap
# https://github.com/graalvm/homebrew-tap/blob/master/Casks/graalvm-ce-java8.rb

# Installation
cd /tmp/
tar xzvf ~/Downloads/graalvm-ce-java11-20.0.0.tar.gz
tar xzvf ~/Downloads/graalvm-ce-java8-20.0.0.tar.gz
sudo mv graalvm-ce-java11-20.0.0 /Library/Java/JavaVirtualMachines/
sudo mv graalvm-ce-java8-20.0.0 /Library/Java/JavaVirtualMachines/

# Run this to make sure the installation worked
# See: https://www.graalvm.org/docs/getting-started/macos
/usr/libexec/java_home -V

# NOTE: Binaries associated with the release can be found in
# /Library/Java/JavaVirtualMachines/graalvm-ce-java8-20.0.0/Contents/Home/bin/
# /Library/Java/JavaVirtualMachines/graalvm-ce-java8-20.0.0/Contents/Home/jre/bin/

# Install the native-image tool
/Library/Java/JavaVirtualMachines/graalvm-ce-java8-20.0.0/Contents/Home/bin/gu install native-image
```

Next I had to set up tools to build this java project (see: https://github.com/IonicDev/ionic-cloud-copy-tool), which is just Java 7+ and Maven 3+. I didn't have to install any Java versions (aside from the GraalVM versions above) since I already had those set up, but I didn't have maven set up.

```bash
# Install maven

# I was going to use brew (https://formulae.brew.sh/formula/maven), but it seemed to just hang
# while trying to download jdk 13 (which was marked as a prerequisite for maven).
# Downloaded from here instead: https://maven.apache.org/download.cgi

# After downloading
cd /tmp/
tar -xzvf ~/Downloads/apache-maven-3.6.3-bin.tar.gz
rm apache-maven-3.6.3/bin/*.cmd
mv apache-maven-3.6.3 /usr/local/share/

# Add this to ~/.bashrc
export PATH=$PATH:/usr/local/share/apache-maven-3.6.3/bin

# Then update env
source ~/.bashrc
```

Now we can build and make sure the jar seems to behave.

```bash
# Build
$ mvn package
# Seems to work
$ java -jar target/IonicCloudCopyTool-* -h
<source> <destination> [-a 'attribute1:val1:val2,attribute2:val3']
  Data from the source is copied to the destination and protected with IDTCS if the destination is remote.
Sources:
  file/system/path
  string:'Text of choice.'
  s3://s3bucket/path/to/object
  gs://gcsbucket/path/to/object
  az:azureContainer/path/to/blob
Destinations:
  file/system/path
  stdout:
  s3://s3bucket/path/to/object
  gs://gcsbucket/path/to/object
  az:azureContainer/path/to/blob
-a only valid for local or string sources
Single Argument Commands:
  version
  config
```

That worked just fine. Next, we'll take a naïve attempt with native-image, based off this documentation: https://www.graalvm.org/getting-started/#native-images

```bash
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java8-20.0.0/Contents/Home/bin/native-image -jar target/IonicCloudCopyTool-0.4.0.jar
Build on Server(pid: 98134, port: 57087)*
[IonicCloudCopyTool-0.4.0:98134]    classlist:   8,286.05 ms,  2.37 GB
[IonicCloudCopyTool-0.4.0:98134]        (cap):  12,580.93 ms,  2.37 GB
[IonicCloudCopyTool-0.4.0:98134]        setup:  14,451.20 ms,  2.37 GB
[IonicCloudCopyTool-0.4.0:98134]     analysis:  31,406.37 ms,  3.22 GB
Warning: Aborting stand-alone image build due to unsupported features
Warning: Use -H:+ReportExceptionStackTraces to print stacktrace of underlying exception
Build on Server(pid: 98134, port: 57087)
[IonicCloudCopyTool-0.4.0:98134]    classlist:     324.46 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]        (cap):   4,411.47 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]        setup:   4,927.63 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]   (typeflow):   2,215.90 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]    (objects):   2,236.84 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]   (features):     105.45 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]     analysis:   4,638.15 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]     (clinit):     162.38 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]     universe:     448.31 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]      (parse):     741.14 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]     (inline):     845.56 ms,  3.19 GB
[IonicCloudCopyTool-0.4.0:98134]    (compile):   5,246.06 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]      compile:   7,273.67 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]        image:     644.32 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]        write:   1,652.36 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]      [total]:  22,116.66 ms,  3.48 GB
Warning: Image 'IonicCloudCopyTool-0.4.0' is a fallback image that requires a JDK for execution (use --no-fallback to suppress fallback image generation and to print more detailed information why a fallback image was necessary).
```

So that didn't work.  So I tried again, with more flags (being lazy here).

```bash
is-mbp-timothy4:ionic-cloud-copy-tool timothy$ /Library/Java/JavaVirtualMachines/graalvm-ce-java8-20.0.0/Contents/Home/bin/native-image -jar target/IonicCloudCopyTool-0.4.0.jar --no-fallback --enable-http --enable-https
Build on Server(pid: 98134, port: 57087)
[IonicCloudCopyTool-0.4.0:98134]    classlist:   6,813.34 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]        (cap):   1,862.89 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]        setup:   2,358.20 ms,  3.48 GB
[IonicCloudCopyTool-0.4.0:98134]   (typeflow):  13,434.38 ms,  3.31 GB
[IonicCloudCopyTool-0.4.0:98134]    (objects):   9,944.64 ms,  3.31 GB
[IonicCloudCopyTool-0.4.0:98134]   (features):   1,129.41 ms,  3.31 GB
[IonicCloudCopyTool-0.4.0:98134]     analysis:  25,899.30 ms,  3.31 GB
Error: Unsupported features in 3 methods
Detailed message:
Error: com.oracle.graal.pointsto.constraints.UnresolvedElementException: Discovered unresolved method during parsing: com.fasterxml.jackson.dataformat.cbor.CBORGenerator.getOutputContext(). To diagnose the issue you can use the --allow-incomplete-classpath option. The missing method is then reported at run time when it is accessed the first time.
Trace:
	at parsing com.fasterxml.jackson.dataformat.cbor.CBORGenerator.close(CBORGenerator.java:903)
Call path from entry point to com.fasterxml.jackson.dataformat.cbor.CBORGenerator.close():
	at com.fasterxml.jackson.dataformat.cbor.CBORGenerator.close(CBORGenerator.java:900)
	at java.io.FileDescriptor.closeAll(FileDescriptor.java:202)
	at java.io.FileInputStream.close(FileInputStream.java:334)
<more>
Error: com.oracle.graal.pointsto.constraints.UnresolvedElementException: Discovered unresolved type during parsing: com.google.appengine.api.urlfetch.HTTPMethod. To diagnose the issue you can use the --allow-incomplete-classpath option. The missing type is then reported at run time when it is accessed the first time.
Trace:
	at parsing com.google.api.client.extensions.appengine.http.UrlFetchTransport.buildRequest(UrlFetchTransport.java:116)
Call path from entry point to com.google.api.client.extensions.appengine.http.UrlFetchTransport.buildRequest(String, String):
	at com.google.api.client.extensions.appengine.http.UrlFetchTransport.buildRequest(UrlFetchTransport.java:113)
	at com.google.api.client.extensions.appengine.http.UrlFetchTransport.buildRequest(UrlFetchTransport.java:50)
<more>

Error: com.oracle.graal.pointsto.constraints.UnresolvedElementException: Discovered unresolved type during parsing: org.slf4j.impl.StaticLoggerBinder. To diagnose the issue you can use the --allow-incomplete-classpath option. The missing type is then reported at run time when it is accessed the first time.
Trace:
	at parsing org.slf4j.LoggerFactory.getILoggerFactory(LoggerFactory.java:335)
Call path from entry point to org.slf4j.LoggerFactory.getILoggerFactory():
	at org.slf4j.LoggerFactory.getILoggerFactory(LoggerFactory.java:329)
	at org.slf4j.LoggerFactory.getLogger(LoggerFactory.java:283)
<more>

Error: Use -H:+ReportExceptionStackTraces to print stacktrace of underlying exception
Error: Image build request failed with exit status 1
```

So that was helpful, and gave me something to search for. Checking some Github issues, I see some comments about Java 11 behaving better than Java 8. I also saw some recommendations for common flags to add for debugging / fixing missing dependencies. I started by switching over to the java 11 version of `native-image`.

```bash
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/gu install native-image
Downloading: Component catalog from www.graalvm.org
Processing Component: Native Image
Downloading: Component native-image: Native Image  from github.com
Installing new component: Native Image (org.graalvm.native-image, version 20.0.0)
```

Then added some of those flags and tried again.

```bash
is-mbp-timothy4:ionic-cloud-copy-tool timothy$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/native-image -ea -jar target/IonicCloudCopyTool-0.4.0.jar --no-fallback --enable-http --enable-https --allow-incomplete-classpath
Build on Server(pid: 98406, port: 57338)
[IonicCloudCopyTool-0.4.0:98406]    classlist:   3,609.96 ms,  1.00 GB
[IonicCloudCopyTool-0.4.0:98406]        (cap):   3,678.79 ms,  1.00 GB
[IonicCloudCopyTool-0.4.0:98406]        setup:   4,003.14 ms,  1.00 GB
[IonicCloudCopyTool-0.4.0:98406]   (typeflow):  17,992.57 ms,  5.17 GB
[IonicCloudCopyTool-0.4.0:98406]    (objects):  17,787.74 ms,  5.17 GB
[IonicCloudCopyTool-0.4.0:98406]   (features):     984.49 ms,  5.17 GB
[IonicCloudCopyTool-0.4.0:98406]     analysis:  38,611.23 ms,  5.17 GB
[IonicCloudCopyTool-0.4.0:98406]     (clinit):   1,090.72 ms,  5.17 GB
[IonicCloudCopyTool-0.4.0:98406]     universe:   3,314.59 ms,  5.17 GB
[IonicCloudCopyTool-0.4.0:98406]      (parse):   5,419.05 ms,  5.50 GB
[IonicCloudCopyTool-0.4.0:98406]     (inline):   6,870.00 ms,  5.76 GB
[IonicCloudCopyTool-0.4.0:98406]    (compile):  36,965.23 ms,  5.81 GB
[IonicCloudCopyTool-0.4.0:98406]      compile:  52,017.83 ms,  5.81 GB
[IonicCloudCopyTool-0.4.0:98406]        image:   5,420.82 ms,  5.88 GB
[IonicCloudCopyTool-0.4.0:98406]        write:   4,288.85 ms,  5.88 GB
[IonicCloudCopyTool-0.4.0:98406]      [total]: 112,588.06 ms,  5.88 GB

is-mbp-timothy4:ionic-cloud-copy-tool timothy$ ll
total 84928
drwxr-xr-x  13 timothy  1145057864   442B May  7 23:49 .
drwxr-xr-x  60 timothy  1145057864   2.0K May  7 22:56 ..
drwxr-xr-x  12 timothy  1145057864   408B May  7 23:38 .git
-rw-r--r--   1 timothy  1145057864    94B May  7 22:56 .gitignore
-rwxr-xr-x   1 timothy  1145057864    41M May  7 23:49 IonicCloudCopyTool-0.4.0
-rw-r--r--   1 timothy  1145057864    20K May  7 22:56 LICENSE.md
-rw-r--r--   1 timothy  1145057864   4.2K May  7 22:56 README.md
-rw-r--r--   1 timothy  1145057864   2.5K May  7 23:29 dependency-reduced-pom.xml
-rw-r--r--   1 timothy  1145057864    90B May  7 22:56 icct.bat
-rwxr-xr-x   1 timothy  1145057864    55B May  7 22:56 icct.sh
-rw-r--r--   1 timothy  1145057864   3.2K May  7 22:56 pom.xml
drwxr-xr-x   3 timothy  1145057864   102B May  7 22:56 src
drwxr-xr-x   7 timothy  1145057864   238B May  7 23:29 target
is-mbp-timothy4:ionic-cloud-copy-tool timothy$ ./IonicCloudCopyTool-0.4.0 -h
<source> <destination> [-a 'attribute1:val1:val2,attribute2:val3']
  Data from the source is copied to the destination and protected with IDTCS if the destination is remote.
Sources:
  file/system/path
  string:'Text of choice.'
  s3://s3bucket/path/to/object
  gs://gcsbucket/path/to/object
  az:azureContainer/path/to/blob
Destinations:
  file/system/path
  stdout:
  s3://s3bucket/path/to/object
  gs://gcsbucket/path/to/object
  az:azureContainer/path/to/blob
-a only valid for local or string sources
Single Argument Commands:
  version
  config

```

Look at that, a native image! Comparing sizes, the native image process did result in a larger file.

```bash
# Native image
-rwxr-xr-x   1 timothy  1145057864    41M May  7 23:49 IonicCloudCopyTool-0.4.0
# Uberjar
-rw-r--r--   1 timothy  1145057864    21M May  7 23:29 IonicCloudCopyTool-0.4.0.jar
```

But we do get those *much* snappier response times we're looking for from a CLI application!

```bash
is-mbp-timothy4:ionic-cloud-copy-tool timothy$ time for i in $(seq 1 10); do java -jar target/IonicCloudCopyTool-*.jar -h >/dev/null; done

real	0m4.167s
user	0m3.321s
sys	0m1.474s

is-mbp-timothy4:ionic-cloud-copy-tool timothy$ time for i in $(seq 1 10); do target/IonicCloudCopyTool-0.4.0 -h >/dev/null; done

real	0m0.172s
user	0m0.036s
sys	0m0.065s
```

For a last step, let's move that binary onto our path and make sure it still looks ok.

```bash
$ cp target/IonicCloudCopyTool-0.4.0 /usr/local/bin/icct
$ which icct
/usr/local/bin/icct
$ icct -h
<source> <destination> [-a 'attribute1:val1:val2,attribute2:val3']
  Data from the source is copied to the destination and protected with IDTCS if the destination is remote.
Sources:
  file/system/path
  string:'Text of choice.'
  s3://s3bucket/path/to/object
  gs://gcsbucket/path/to/object
  az:azureContainer/path/to/blob
Destinations:
  file/system/path
  stdout:
  s3://s3bucket/path/to/object
  gs://gcsbucket/path/to/object
  az:azureContainer/path/to/blob
-a only valid for local or string sources
Single Argument Commands:
  version
  config
```

Note that I haven't used this binary for anything serious yet, so caveats abound, but if this works out I'll at least consider jvm + native image for CLI tools. Honestly I probably won't consider it too often because I love python and go and go cross compiling is awesome, but if there are JVM packages to do something interesting I'll be less prone to shy away from CLI-based tooling.

## EDIT: 20200508

Right after I published this post I ran some quick function tests on the binary produced by `native-image`.

```bash
# Version command is ok
$ icct version
0.4.0-LOCAL

# Local copy works fine
$ icct /tmp/testfile.txt stdout:
hi there

$ icct /tmp/testfile.txt /tmp/testfile.txt.2
$ cat /tmp/testfile.txt.2
hi there

# Config output doesn't look good
$ icct config
Exception in thread "main" java.lang.ExceptionInInitializerError
	at com.oracle.svm.core.hub.ClassInitializationInfo.initialize(ClassInitializationInfo.java:290)
	at java.lang.Class.ensureInitialized(DynamicHub.java:496)
	at com.ionic.sdk.agent.hfp.Fingerprint.<init>(Fingerprint.java:28)
	at com.ionic.sdk.agent.Agent.<init>(Agent.java:95)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.checkIonicConfiguration(IonicCloudCopy.java:529)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.configurationCheck(IonicCloudCopy.java:605)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.main(IonicCloudCopy.java:138)
Caused by: java.lang.IllegalStateException: java.lang.ClassNotFoundException: com.ionic.sdk.core.codec8.TranscoderFactory8
	at com.ionic.sdk.core.codec.Transcoder.getFactory(Transcoder.java:62)
	at com.ionic.sdk.core.codec.Transcoder.<clinit>(Transcoder.java:45)
	at com.oracle.svm.core.hub.ClassInitializationInfo.invokeClassInitializer(ClassInitializationInfo.java:350)
	at com.oracle.svm.core.hub.ClassInitializationInfo.initialize(ClassInitializationInfo.java:270)
	... 6 more
Caused by: java.lang.ClassNotFoundException: com.ionic.sdk.core.codec8.TranscoderFactory8
	at com.oracle.svm.core.hub.ClassForNameSupport.forName(ClassForNameSupport.java:60)
	at java.lang.Class.forName(DynamicHub.java:1211)
	at com.ionic.sdk.core.codec.Transcoder.getFactory(Transcoder.java:60)
	... 9 more

# Copy to s3 doesn't look good
$ icct /tmp/testfile.txt s3://$BUCKET_NAME/testfile.txt
Exception in thread "main" java.lang.NoClassDefFoundError: org.apache.commons.logging.LogFactory
	at org.apache.commons.logging.LogFactory.class$(LogFactory.java:847)
	at org.apache.commons.logging.LogFactory.<clinit>(LogFactory.java:1717)
	at com.oracle.svm.core.hub.ClassInitializationInfo.invokeClassInitializer(ClassInitializationInfo.java:350)
	at com.oracle.svm.core.hub.ClassInitializationInfo.initialize(ClassInitializationInfo.java:270)
	at java.lang.Class.ensureInitialized(DynamicHub.java:496)
	at com.amazonaws.auth.AWSCredentialsProviderChain.<clinit>(AWSCredentialsProviderChain.java:41)
	at com.oracle.svm.core.hub.ClassInitializationInfo.invokeClassInitializer(ClassInitializationInfo.java:350)
	at com.oracle.svm.core.hub.ClassInitializationInfo.initialize(ClassInitializationInfo.java:270)
	at java.lang.Class.ensureInitialized(DynamicHub.java:496)
	at com.oracle.svm.core.hub.ClassInitializationInfo.initialize(ClassInitializationInfo.java:235)
	at java.lang.Class.ensureInitialized(DynamicHub.java:496)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.checkAWSCredentialsConfiguration(IonicCloudCopy.java:551)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.S3Location(IonicCloudCopy.java:359)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.destinationFromArg(IonicCloudCopy.java:202)
	at com.ionic.cloudstorage.icct.IonicCloudCopy.main(IonicCloudCopy.java:144)

```

So it looks like I have a bit more to dig into, likely involving [adding classpaths to the `native-image` call](https://github.com/oracle/graal/issues/671#issuecomment-422993966) and fixing [relection and dynamic resource loading](https://github.com/oracle/graal/blob/master/substratevm/CONFIGURE.md). It looks like `--allow-incomplete-classpath` was added to handle runtime dependencies that are not loaded, whereas I used it to force `native-image` to give me something when it was (rightly, it seems) complaining about missing dependencies at build time.

I'll publish updates on this post. If the work turns out to be significant, I'll move those updates to a new post.

## EDIT: 20200509

Continuing with graalvm, I'm following the recommendations in [the graalvm documentation for working with their java agent](https://github.com/oracle/graal/blob/master/substratevm/CONFIGURE.md) to trace the reflective calls (and resource access) from the application and write that to config files for the native image tool to consume.

```bash
# I'll be putting these directly into the META-INF directory of this maven project
# https://github.com/IonicDev/ionic-cloud-copy-tool
GRAAL_CONF_DIR=./src/main/resources/META-INF/native-image
mkdir -p $GRAAL_CONF_DIR

# Start collecting details about graalvm operation
# All other commands will use the `config-merge-dir` option instead of `config-output-dir`
/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/java -agentlib:native-image-agent=config-output-dir=$GRAAL_CONF_DIR -jar target/IonicCloudCopyTool-0.4.0.jar version

# The tool only takes a plaintext persisor now, so I need to export to plaintext for testing
# Uses the machinacli tool: https://dev.ionic.com/tools/machina
# https://github.com/IonicDev/ionic-cloud-copy-tool/blob/master/src/main/java/com/ionic/cloudstorage/icct/IonicCloudCopy.java
machina profile move -d L_qx.H.83d53616-ed4d-474d-74d3-b7ecc6e4e0ef -t plaintext -f ~/.ionicsecurity/profiles.pt
machina -t plaintext -f ~/.ionicsecurity/profiles.pt profile set -d L_qx.H.83d53616-ed4d-474d-74d3-b7ecc6e4e0ef

# Needed to export AWS_REGION instead AWS_DEFAULT_REGION
# https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/regions/providers/DefaultAwsRegionProviderChain.html
# https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html
# This is AWS_DEFAULT_REGION in boto3
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variable-configuration
# Also confusing in other tools: https://github.com/aws/aws-sdk-go/issues/2103
export AWS_REGION=$AWS_DEFAULT_REGION

# Run some commands with the tool, merging output for graal
/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/java -agentlib:native-image-agent=config-merge-dir=$GRAAL_CONF_DIR -jar target/IonicCloudCopyTool-0.4.0.jar config
/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/java -agentlib:native-image-agent=config-merge-dir=$GRAAL_CONF_DIR -jar target/IonicCloudCopyTool-0.4.0.jar /tmp/testfile.txt s3://$BUCKET_NAME/testfile.txt
/Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/java -agentlib:native-image-agent=config-merge-dir=$GRAAL_CONF_DIR -jar target/IonicCloudCopyTool-0.4.0.jar s3://$BUCKET_NAME/testfile.txt /tmp/testfile.txt.decrypted

# Inspect written files
ls -lah $GRAAL_CONF_DIR
for f in `ls $GRAAL_CONF_DIR`; do echo //$f; cat $GRAAL_CONF_DIR/$f | jq .; done

# Re-build the jar with the native image resources included
mvn package

# Ensure the META-INF files are included (I had originally written them to the wrong place)
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/jar tf target/IonicCloudCopyTool-0.4.0.jar | grep META-INF/native
META-INF/native-image/
META-INF/native-image/jni-config.json
META-INF/native-image/proxy-config.json
META-INF/native-image/reflect-config.json
META-INF/native-image/resource-config.json

# Build the native image from the jar
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/native-image -ea -jar target/IonicCloudCopyTool-0.4.0.jar --no-fallback --enable-http --enable-https --allow-incomplete-classpath --no-server
[IonicCloudCopyTool-0.4.0:61591]    classlist:   5,538.37 ms,  1.32 GB
[IonicCloudCopyTool-0.4.0:61591]        (cap):   3,568.30 ms,  1.32 GB
[IonicCloudCopyTool-0.4.0:61591]        setup:   5,479.04 ms,  1.67 GB
[IonicCloudCopyTool-0.4.0:61591]     analysis:  24,360.97 ms,  3.91 GB
Error: Classes that should be initialized at run time got initialized during image building:
 org.apache.http.pool.ConnPoolControl was unintentionally initialized at build time. To see why org.apache.http.pool.ConnPoolControl got initialized use -H:+TraceClassInitialization
org.apache.http.HttpClientConnection was unintentionally initialized at build time. To see why org.apache.http.HttpClientConnection got initialized use -H:+TraceClassInitialization
org.apache.http.conn.routing.HttpRoute was unintentionally initialized at build time. To see why org.apache.http.conn.routing.HttpRoute got initialized use -H:+TraceClassInitialization
org.apache.http.conn.ConnectionRequest was unintentionally initialized at build time. To see why org.apache.http.conn.ConnectionRequest got initialized use -H:+TraceClassInitialization
org.apache.http.protocol.HttpContext was unintentionally initialized at build time. To see why org.apache.http.protocol.HttpContext got initialized use -H:+TraceClassInitialization
org.apache.http.conn.HttpClientConnectionManager was unintentionally initialized at build time. To see why org.apache.http.conn.HttpClientConnectionManager got initialized use -H:+TraceClassInitialization

Error: Use -H:+ReportExceptionStackTraces to print stacktrace of underlying exception
Error: Image build request failed with exit status 1

# Still getting errors.
# Trying some additional tricks with initialization hints from: https://spring.io/blog/2020/04/16/spring-tips-the-graalvm-native-image-builder-feature
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/native-image -ea -jar target/IonicCloudCopyTool-0.4.0.jar --no-fallback --allow-incomplete-classpath --no-server --initialize-at-build-time=org.apache.http.conn.routing.HttpRoute,org.apache.http.protocol.HttpContext,org.apache.http.HttpClientConnection,org.apache.http.conn.ConnectionRequest,org.apache.http.pool.ConnPoolControl,org.apache.http.conn.HttpClientConnectionManager -H:+TraceClassInitialization
[IonicCloudCopyTool-0.4.0:62055]    classlist:   6,351.16 ms,  1.29 GB
[IonicCloudCopyTool-0.4.0:62055]        (cap):   2,361.68 ms,  1.29 GB
[IonicCloudCopyTool-0.4.0:62055]        setup:   4,093.37 ms,  1.29 GB
[IonicCloudCopyTool-0.4.0:62055]   (typeflow):  26,550.09 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]    (objects):  18,375.48 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]   (features):   1,496.49 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]     analysis:  48,187.45 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]     (clinit):     966.15 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]     universe:   2,632.33 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]      (parse):   5,510.07 ms,  9.21 GB
[IonicCloudCopyTool-0.4.0:62055]     (inline):  22,769.90 ms, 10.64 GB
[IonicCloudCopyTool-0.4.0:62055]    (compile):  50,351.15 ms, 11.46 GB
[IonicCloudCopyTool-0.4.0:62055]      compile:  90,526.27 ms, 11.46 GB
[IonicCloudCopyTool-0.4.0:62055]        image:   8,356.94 ms, 11.73 GB
[IonicCloudCopyTool-0.4.0:62055]        write:   5,285.07 ms, 11.73 GB
[IonicCloudCopyTool-0.4.0:62055]      [total]: 165,849.45 ms, 11.73 GB

# Got a working build! But got a fatal error when running.
# Thankfully the recommendation is quite clear.
$ ./IonicCloudCopyTool-0.4.0 config
Fatal error: javax.crypto.JceSecurity.getCodeBase(Class) is reached at runtime. This should not happen. The contents of JceSecurity.verificationResults are computed and cached at image build time. Try enabling all security services with --enable-all-security-services.

JavaFrameAnchor dump:

  No anchors
<more dump contents>

# Building again
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/native-image -ea -jar target/IonicCloudCopyTool-0.4.0.jar --no-fallback --allow-incomplete-classpath --no-server --initialize-at-build-time=org.apache.http.conn.routing.HttpRoute,org.apache.http.protocol.HttpContext,org.apache.http.HttpClientConnection,org.apache.http.conn.ConnectionRequest,org.apache.http.pool.ConnPoolControl,org.apache.http.conn.HttpClientConnectionManager --enable-all-security-services -H:+TraceClassInitialization
[IonicCloudCopyTool-0.4.0:62308]    classlist:   6,934.81 ms,  1.29 GB
[IonicCloudCopyTool-0.4.0:62308]        (cap):   5,159.98 ms,  1.29 GB
[IonicCloudCopyTool-0.4.0:62308]        setup:   6,967.24 ms,  1.29 GB
[IonicCloudCopyTool-0.4.0:62308]   (typeflow):  31,334.62 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]    (objects):  25,477.01 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]   (features):   2,076.97 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]     analysis:  61,493.13 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]     (clinit):   1,126.30 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]     universe:   3,392.50 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]      (parse):   5,999.22 ms,  9.61 GB
[IonicCloudCopyTool-0.4.0:62308]     (inline):  15,347.59 ms, 11.28 GB
[IonicCloudCopyTool-0.4.0:62308]    (compile):  42,364.79 ms, 11.58 GB
[IonicCloudCopyTool-0.4.0:62308]      compile:  68,682.98 ms, 11.58 GB
[IonicCloudCopyTool-0.4.0:62308]        image:   7,207.60 ms, 11.83 GB
[IonicCloudCopyTool-0.4.0:62308]        write:   5,135.07 ms, 11.83 GB
[IonicCloudCopyTool-0.4.0:62308]      [total]: 161,169.69 ms, 11.83 GB

# Still errors, but getting closer...
$ ./IonicCloudCopyTool-0.4.0 config
Exception in thread "main" java.lang.IllegalArgumentException: java.net.MalformedURLException: Accessing an URL protocol that was not enabled. The URL protocol https is supported but not enabled by default. It must be enabled by adding the -H:EnableURLProtocols=https option to the native-image command.

# Building again
$ /Library/Java/JavaVirtualMachines/graalvm-ce-java11-20.0.0/Contents/Home/bin/native-image -ea -jar target/IonicCloudCopyTool-0.4.0.jar --no-fallback --allow-incomplete-classpath --no-server --initialize-at-build-time=org.apache.http.conn.routing.HttpRoute,org.apache.http.protocol.HttpContext,org.apache.http.HttpClientConnection,org.apache.http.conn.ConnectionRequest,org.apache.http.pool.ConnPoolControl,org.apache.http.conn.HttpClientConnectionManager --enable-all-security-services --enable-http --enable-https -H:+TraceClassInitialization
[IonicCloudCopyTool-0.4.0:62455]    classlist:   6,262.77 ms,  1.55 GB
[IonicCloudCopyTool-0.4.0:62455]        (cap):   4,359.17 ms,  1.55 GB
[IonicCloudCopyTool-0.4.0:62455]        setup:   6,042.22 ms,  1.55 GB
[IonicCloudCopyTool-0.4.0:62455]   (typeflow):  28,935.83 ms,  7.94 GB
[IonicCloudCopyTool-0.4.0:62455]    (objects):  21,362.67 ms,  7.94 GB
[IonicCloudCopyTool-0.4.0:62455]   (features):   2,181.84 ms,  7.94 GB
[IonicCloudCopyTool-0.4.0:62455]     analysis:  55,527.36 ms,  7.94 GB
[IonicCloudCopyTool-0.4.0:62455]     (clinit):   1,751.76 ms,  7.94 GB
[IonicCloudCopyTool-0.4.0:62455]     universe:   4,590.87 ms,  7.94 GB
[IonicCloudCopyTool-0.4.0:62455]      (parse):   8,816.98 ms,  8.29 GB
[IonicCloudCopyTool-0.4.0:62455]     (inline):   8,942.87 ms, 10.02 GB
[IonicCloudCopyTool-0.4.0:62455]    (compile):  43,584.38 ms, 10.91 GB
[IonicCloudCopyTool-0.4.0:62455]      compile:  65,789.12 ms, 10.91 GB
[IonicCloudCopyTool-0.4.0:62455]        image:  11,449.58 ms, 10.91 GB
[IonicCloudCopyTool-0.4.0:62455]        write:   3,868.79 ms, 10.91 GB
[IonicCloudCopyTool-0.4.0:62455]      [total]: 153,932.43 ms, 10.91 GB

# Definitely getting closer, but this one is strange.
# The "Failed to parse serialized data" is unexpected. The Ionic SDK swallows the exception details, so we don't have much to go on here.
$ ./IonicCloudCopyTool-0.4.0 config
Ionic Configuration Status: ERROR:
	40010 - Failed to parse serialized data

AWS Credential Configuration: CONFIGURED
AWS Region Configuration: CONFIGURED
Google Credential Configuration: ERROR:
	Error reading credential file from location /Users/timothy/.config/gcloud/application_default_credentials.json: 400 Bad Request
{
  "error" : "invalid_grant",
  "error_description" : "Bad Request"
}

Azure Credential Configuration: ERROR:
	AZURE_STORAGE_ACCOUNT is not present in environment.

# Likely related to the `config` error.
$ ./IonicCloudCopyTool-0.4.0 s3://$BUCKET_NAME/testfile.txt /tmp/testfile.txt.decrypted
Ionic Persistor not found at: /Users/timothy/.ionicsecurity/profiles.pt

# OK, but these worked before too.
$ ./IonicCloudCopyTool-0.4.0 /tmp/testfile.txt /tmp/testfile.txt.2
$ ./IonicCloudCopyTool-0.4.0 /tmp/testfile.txt stdout:
```

So it looks like the error is getting swallowed into an unknown exception and returned as an error. I'll dig into this one later and post another update.

Since this is supposed to be an experience report, here are my thoughts at this point:

* The native image files are *much* faster to startup than the java jars (>10x), which is pretty awesome.
    * I'll keep messing with graal for that reason alone.
* The graal java agent (for writing `native-image` config files) is pretty cool, but definitely not a panacea.
* For larger projects I think these `native-image` config files would get hard to manage.
    * I would also be pretty uncomfortable deploying something that would hit a runtime exception in case a missing configuration just because I failed to exersize some edge case of the application's behavior to get the agent to write config for me.
    * I imagine this set of resources would stabilize over time, but as dependencies are updated this gives me yet another edge case of things to check.
    * This pushes us from the benefits of build time checks backwards to more run time worries. I'm used to dealing with this in python, but I trust large scala, go, and java systems more than python systems because of the safety static compilation and type checking.
* The swallowing of the native image related runtime exception is unfortunate.
    * Perhaps there is another way that the runtime can be instrumented to dump more details on error?
* The native image compile time is very slow.
    * Like 90s+ for a maven project that takes ~5s.
    * This makes iteration on this phase of development quite slow, and I imagine it gets worse for substantially larger projects.
    * I bet running the build in server mode can help with caching of build stages to make this less painful, but still, this is very slow.

In summary: this is really neat technology, but it does have some leaky abstractions associated with it. I can't just toss an uberjar over the wall at `native-image` and expect success. If the technology and solution continues to advance to resolve the complexities associated with reflection and build time I can see this becoming a tool useful for more general problems, but as it stands, I would be most likely to recommend Graal's `native-image` if I know someone really needed fast boot for an existing Java code base, or needed to wrap mature Java libraries for a CLI application. For many other scenarios (like greenfield development) I'd still be more likely to recommend a non-JVM language for these problems, most likely Go or Rust (I haven't played with Rust yet but I hear great things from people I respect).

