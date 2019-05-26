Title: Developing an OSX app with Python
Date: 2018-03-16 15:00
Tags: python, osx, ionic, pyinstaller, multiprocessing, pkgbuild
Status: published

## Application architecture

The purpose of the project was to build an application that would watch a directory for changes and respond to directory events with a flexible set of actions.

I broke the problem into a few parts, which mapped well into separate processes.

1. Directory watcher. Responsible for responding to directory changes and spawning an event.
2. Event enrichment. Takes events from step 1, filters out events that don't need a response, and enriches events with additional information.
3. Action executor. Takes enriched events from step 2 and acts on them.

I used [python's multiprocessing library](https://docs.python.org/2/library/multiprocessing.html) to spin off 3 worker processes and connect them together via queues.  Step 1 uses the excellent [watchdog library](http://pythonhosted.org/watchdog/).  Step 2 takes a list of functions that are called on every event. Each function returns either a modified event object or `None` (if the event should not be processed any further). Step 3 uses [the Ionic OSX Python SDK](https://dev.ionic.com/getting-started/osx-python.html) to encrypt, decrypt, or reencrypt files.

I used [argparse](https://docs.python.org/2/library/argparse.html) to handle command line arguments, [configparser](https://docs.python.org/2/library/configparser.html) for processing a configuration file, and [the `entry_points` feature of setuptools](http://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation) to generate an executable script when users install the package via [pip](https://pip.pypa.io/en/stable/quickstart/) (or native setuptools).

After this was all working, I wanted to make the package easier to install for less-technical users.  Also, I wanted the application to always be running in the background when the user was logged in.

Thus began my journey toward OSX packaging nirvana.

## Problem 1: Locking in shared library access when using multiprocessing

This problem was not related to OSX packaging specifically, and I talked about that problem already [here](/python-multiprocessing-and-corefoundation-libraries.html).  

> TL;DR: You can still use complex C libraries with multiprocessing if you take a couple steps to avoid issues with how \*nix OSes fork processes.

## Problem 2: Missing shared library for pyinstaller

When I ran [pyinstaller](http://www.pyinstaller.org/) on the application, it found most of what it needed, but when the application got to the step where it tried to perform operations with the Ionic SDK, the application could not find the shared library it needed.  For reference, the command I used to build the OSX app was:

    #!bash
    # https://pyinstaller.readthedocs.io/en/stable/usage.html#building-mac-os-x-app-bundles
    pyinstaller --windowed --osx-bundle-identifier "com.ionic.python.ionic-fs-watcher" ionic-fs-watcher.spec --clean

The fix for this was not too hard, though it took me a little while to figure out the syntax that pyinstaller required in its specfile.  This is the section of the spec file that adds support for finding the shared library looks like.

    #!python
    # In this example I just grab the path for the shared lib on osx. In future versions, I'll extend to grab the path the shared lib on Windows and Linux, or even add a hook to automate this for future pyinstaller usersßß:
    # http://pyinstaller.readthedocs.io/en/stable/hooks.html
    # The Entrypoint class is a slightly modified version of the code here: https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Setuptools-Entry-Point
    a = Entrypoint('ionic-sdk-ext', 'console_scripts', 'ionic-fs-watcher',
      binaries=[
        # Grab the shared lib
        # https://pythonhosted.org/PyInstaller/spec-files.html#adding-binary-files
        # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Collect-Data-Files
        (os.path.join(os.path.dirname(ionicsdk.__file__), "lib/libISAgentSDKC.dylib"), ".")
      ],
    )

One other detail: [the section of the pyinstaller documentation that discusses the `BUNDLE` command for OSX](https://pyinstaller.readthedocs.io/en/stable/spec-files.html#spec-file-options-for-a-mac-os-x-bundle) recommends calling `BUNDLE` with output of `EXE`.  When I did that, I noticed a lot of files missing in the `dist/IonicFSWatcher.app/Contents/MacOS/` directory, esp. compared to the outout in `dist/ionic-fs-watcher/` (created by the `COLLECT` operation).  On a whim, I tried calling `BUNDLE` with the output of `COLLECT` instead of `EXE`.  WHen I did that, all the files I was looking for were present.

After that step, I could successfully run the executable file `ionic-fs-watcher` that was created at `dist/IonicFSWatcher.app/Contents/MacOS/ionic-fs-watcher`.

## Problem 3: Strange default install behavior with pkgbuild

After a bit of Googling, building with `pkgbuild` was not very difficult to figure out once I realized that I could just set up a "fake root" to add files into and package that entire root.  But after building the application, I was having unexpected behavior when I installed.  I was building and installing the package like this:

    #!bash
    # Add contents into clean "fake root"
    rm -rf /tmp/fs-watcher-root
    mkdir -p /tmp/fs-watcher-root/Applications
    cp -r dist/IonicFSWatcher.app /tmp/fs-watcher-root/Applications/IonicFSWatcher.app

    # Build
    pkgbuild --identifier com.ionic.python.ionic-fs-watcher --root /tmp/fs-watcher-root

    # Install
    # The `-dumplog -verbose` options are not needed, but certainly help debugging
    installer -pkg IonicFSWatcher.pkg -target / -dumplog -verbose

When I ran the `installer` command I did not see anything created in `/Applications/IonicFSWatcher.app`. I checked the output of `pkgutil --files com.ionic.python.ionic-fs-watcher` (and compared with the output for other installed applications), and it looked like everything was set up correctly (i.e. all files listed at the correct paths).

After much searching, I learned that the issue was the `BundleIsRelocatable` attribute of the package, which [is by default set to `true`](https://scriptingosx.com/2017/05/relocatable-package-installers-and-quickpkg-update/).  If you do not set this to `false` and the package is not already installed in `/Applications`, OSX will try to find another copy of the app that the user may have installed previously and moved, and install there.  THe idea here is to make upgrading applications even when the user has moved the application around.

In my case, the other copy of the application that OSX found was the same `.app` directory I had just created the package from.  As [others have have noted](https://apple.stackexchange.com/questions/219123/pkgbuild-created-package-does-not-install-correctly), this is not a very obvious default behavior.  To fix this, you need to pass an extra option file to `pkgbuild`.  You can get a sample file to pass to `pkgbuild` with the following command.

    #!bash
    # Dumps to `example.plist`
    pkgbuild --analyze --identifier com.ionic.python.ionic-fs-watcher --install-location /Applications --root /tmp/fs-watcher-root example.plist

After modification, `example.plist` should look like this (note the value of `BundleIsRelocatable`).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<array>
    <dict>
        <key>BundleHasStrictIdentifier</key>
        <true/>
        <key>BundleIsRelocatable</key>
        <false/>
        <key>BundleIsVersionChecked</key>
        <true/>
        <key>BundleOverwriteAction</key>
        <string>upgrade</string>
        <key>RootRelativeBundlePath</key>
        <string>Applications/IonicFSWatcher.app</string>
    </dict>
</array>
</plist>
```

Once you modify `example.plist`, you can use it calling `pkgbuild` with the option `--component-plist example.plist`.

After rebuilding with those new options and re-installing, I saw files showing up in `/Applications` as expected.  Even better, running `/Applications/IonicFSWatcher.app/Contents/MacOS/ionic-fs-watcher` directly gave the expected output.

## Problem 4: OSX LaunchAgent and keychain access

The last step was getting the installer to also create a `ServiceAgent` that would run in the background.  I was able to use a `postinstall` script to create the file `~/Library/LaunchAgents/com.ionic.python.ionic-fs-watcher.startup.plist` (see `man pkgbuild` and the `--scripts` option for details).

The first set of problems I ran into were around permissions.  If anything fails when trying to run a LaunchAgent, very little (if any) information shows up in syslog (`tail -f /var/log/system.log`).  Debugging permissions errors for things like log directories is especially difficult.  I don't have a great solution to this aside from a piece of advice: keep your LaunchAgent plist file very simple when debugging, and slowly add in any additional options as the service is running.

But the bigger issue I ran into was just a general confusion about how to load, unload, launch, stop, and debug runs of a LaunchAgent.  Because of this I was getting some strange issues when trying to access the user's keychain, which is where the [Ionic device profiles are stored on OSX](https://dev.ionic.com/registration.html).  I was able to slowly and painfully work out a solution that is documented in these [StackOverflow](https://stackoverflow.com/) questions:

* https://stackoverflow.com/questions/49289890/error-code-9216-when-attempting-to-access-keychain-password-in-launchagent/49323395#49323395
* https://stackoverflow.com/questions/49290174/osx-syntax-for-loading-a-single-launchagent-for-current-user/49302586#49302586

The short story here is: if you are doing any of these things, [you are going to have a bad time](https://www.youtube.com/watch?v=ynxPshq8ERo).

* Using `sudo` to launch your launch agent
* Setting permissions on your plist file that are anything except for 644 with the installing user as the owner, and that user's default group as the group
* Using legacy `launchctl` commands like `load` and `unload` instead of their new equivalents `bootstrap` and `bootout`
* Not using the `launchctl` `kickstart` and `debug` commands for debugging
* Not playing attention to whether your agents are enabled or disabled (`launchctl enable ...`)

Please refer to the question answer themselves for more information about and recommendations for working with `launchd`.

## Summary

After all of that, I have an application, packaged as an OSX `pkg`, which can monitor directories for changes and run a series of actions in response to those changes.  Installing the application sets up, enables, and starts a bacnground process that will watch directories specified by the user.

More importantly, I have gained knowledge that will allow me to do this faster next time.  Well, here's to wishful thinking...
