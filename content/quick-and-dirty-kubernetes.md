Title: Quick and dirty kubernetes
Date: 2017-10-27 18:47
Tags: kubernetes, docker, sftp
Status: published

# The Problem

As part of our analytics solution at Ionic, my team was working on a system to push files to customer owned endpoints.  We wanted to do a quick validation that pushed to a server outside our network was working.

We already had a test environment running locally with [an sftp docker image](https://github.com/atmoz/sftp), and since I didn't already have a public server sitting around to setup an sftp on, I decided this was a great opportunity to play around with Google Cloud's Container service and kubernetes to spin up a quick helper service.

I started here: [https://cloud.google.com/sdk/docs/quickstart-linux](https://cloud.google.com/sdk/docs/quickstart-linux).  I installed all this into a Centos 7 vagrant box that my team uses for most of our development.

```
# Download, extract, install, init
wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-177.0.0-linux-x86_64.tar.gz
tar xzvf google-cloud-sdk-177.0.0-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Move it to a better place than `/tmp` since I'm going to be sticking this on my path
sudo mv google-cloud-sdk /opt/
export PATH=$PATH:/opt/google-cloud-sdk/bin

# Init
gcloud init

# Get credentials for the cluster
# This is pretty cool - it gives you a url to visit in your browser, redirects you to an Oauth authorization page, and finally gives you a token to paste back into your console.
# I replaced by project id with XXXX.
gcloud container clusters get-credentials sftp --zone us-central1-a --project ionictest-XXXX

```

# The first hiccup: install path

This was all working pretty well, but then I ran into issues when I ran `gcloud components install kubectl`.  There were permission issues because `gcloud` tries to write a scratch directory at the same level as its installation directory (i.e. in `/opt` instead of in `/opt/google-cloud-sdk`.)  This was a strange choice, since it meant that I had to nest the installation another level deeper.

```
# Nesting nesting
sudo mkdir -p /opt/google
sudo chown -R vagrant:vagrant /opt/google
sudo mv /opt/google-cloud-sdk /opt/google

# Fix path
# Really this was more manual since I removed the old bin path and also updated ~/.bashrc
export PATH=$PATH:/opt/google/google-cloud-sdk/bin

# Now installation works
gcloud components install kubectl
```

At this point the path was bjorked.  When I tried to run `kubectl run` I got this mysterious error

```
error: failed to discover supported resources: Get https://XX.XX.XX.XX/api: error executing access token command "/opt/google-cloud-sdk/bin/gcloud config config-helper --format=json": err=fork/exec /opt/google-cloud-sdk/bin/gcloud: no such file or directory output=
```

Notice the path is pointing to the old installation location.  I reset my PATH, logged out of the vm and logged back in, and re-ran `gcloud components install kubectl`, none of which worked.  Then I re-ran the `gcloud container clusters get-credentials`, which worked.  So I guess the path to the binary is stored somewhere in the credentials config?  I'm not sure.  This article is called "quick and dirty" for a reason.

Now to launch containers.

```
kubectl run sftp --image=atmoz/sftp --port 22
kubectl expose deployment sftp --type=LoadBalancer --port 22 --target-port 22
```

Alright - we're running!

# The second hiccup: container arguments

Well, almost.  When I checked the Google Container Engine dashboard I saw the the containers has the status `CrashLoopBackoff`, which didn't sound good.  I dug into the kubectl cli a bit more and found some useful commands.

```
# List items
kubectl get pods
kubectl get services
kubectl get deployments

# Clear out items (very helpful when testing)
kubectl delete pod sftp-2557270963-pc8q8
kubectl delete service sftp
kubectl delete deployment sftp
```

I leave it to the kubernetes docs to define what the things are in depth, but in brief the pods are containers and services and deployments are higher level management concepts to work with containers.  For the point of this article the most important take aways are this

* If you delete a pod, it will come back.
* If you want to stop something from running and start over, delete the service and the deployment. The pods will go away with those.

So - now we have pods deployed, but crashing.  The missing link here was the difference between kubernetes commands and docker entrypoints.

```
# What our docker compose looks like for running locally
# Use the default entrypoint, override the command
version: '2'
services:
  sftp:
    image: atmoz/sftp
    command: username:password:::export

# What we had to do in kubectl
# Use the default command, send an argument
kubectl run sftp --image=atmoz/sftp --port=22 -- "username:password:::export"
```

# Final steps and success

Once that was updated, I just had to expose the services again (`kubectl expose deployment sftp --type=LoadBalancer --port 22 --target-port 22`).  I also had to wait for the service to come up.  You can check this via `kubectl get services` and waiting until the `EXTERNAL-IP` field changes from "pending" to a real ip.  Once that was ready, and I could sftp in!

```
[vagrant@localhost ~]$ sftp username@XX.XX.XX.XX
username@XX.XX.XX.XX's password:
Connected to XX.XX.XX.XX.
sftp> ls export/
export/testfile.json
```

I hope that was helpful.  I have been using docker daily for a few years now, but this is my first time playing with kubernetes.  If I did something stupid, let me know!  You can find me on twitter (`@turtlemonvh`).
