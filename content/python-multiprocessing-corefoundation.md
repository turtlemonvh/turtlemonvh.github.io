Title: Python multiprocessing and CoreFoundation libraries
Date: 2018-03-02 15:00
Tags: python, multiprocessing, parallel
Status: published

Python's [multiprocessing library](https://docs.python.org/2/library/multiprocessing.html) is pretty awesome, and it can make it much easier to build programs that exersize multiple cores in python.  However, some libraries are known not to behave well with multiprocessing.  You may be running into this problem if you see output like this from your program, in addition to strange behavior like hanging code.

    The process has forked and you cannot use this CoreFoundation functionality safely. You MUST exec().
    Break on __THE_PROCESS_HAS_FORKED_AND_YOU_CANNOT_USE_THIS_COREFOUNDATION_FUNCTIONALITY___YOU_MUST_EXEC__() to debug.

These issues come about because when the multiprocessing library creates a new process it does not call `exec` on forked processes, and because \*nix OSes use "COW" (copy-on-write) forks of the parent process, there can be references shared between child and parent processes than can cause issues in some libraries.

For details, see:

* https://bugs.python.org/issue8713
* https://groups.google.com/forum/#!topic/comp.lang.python/b2Ayc8bQzMQ

To address this, Python 3 adds support for a ["spawn" option for starting processes](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods). This creates an entirely new python interpreter process.

> As an aside, this "spwan" behavior is actually the default behavior on Windows, which doesn't have COW forks.
> This behavior can cause problems porting multiprocessing applications from \*nix to Windows, since the COW forked processes in \*nix OSes can sometimes have access to variables that the new-interpreter Windows processes cannot see.

To address this problem in Python 2 code, we take a pretty simple approach.  Since the problem is shared references between parent and child processes, if the problematic libraries are never touched in the parent process (and only in child processes which don't fork additional children themselves), we shouldn't have problems with contention and reference collisions.

However, sometimes you need to get access to a library before you launch a pool of worker processes.  What do you do then?  Here is the pattern I adopted for a project recently:

    #!python
    from functools import wraps
    from multiprocessing import Process, Queue

    def run_in_forked_process(f):
        def wrapf(q, f, args, kwargs):
            q.put(f(*args, **kwargs))

        @wraps(f)
        def wrapper(*args, **kwargs):
            q = Queue()
            Process(target=wrapf, args=(q, f, args, kwargs)).start()
            return q.get()

        return wrapper

The code looks a little complex, but it is just a [decorator](https://www.python.org/dev/peps/pep-0318/) that you can add to a function that makes it safe to call in the main parent process.

What this decorator does is

* create a queue
* run the function you want to execute in a new forked process, collecting the result on the queue
* return the result it got back from the queue

You can use it like this to make the function `my_function_using_corefoundation_libs` safe to run in the main process of a codebase that uses multiprocessing.

    #!python

    # Function definition

    @run_in_forked_process
    def my_function_using_corefoundation_libs(a, b=False):
        # Your code goes here
        pass

    # You can call your function as normal.
    # It will just execute in a forked process instead of running in the main parent process.

    c, d = my_function_using_corefoundation_libs("cat", True)

This solution is not perfect.  It is not very efficient since it forks a whole process to run the function, and it won't handle exceptions very well.  But it does allow you to use some nice libraries with multiprocessing to get stuff done.
