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

is-mbp-timothy4:ionic-cloud-copy-tool timothy$ time for i in $(seq 1 10); do target/IonicCloudCopyTool-0.4.0 >/dev/null; done

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

