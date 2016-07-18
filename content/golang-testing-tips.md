Title: Helpful tips for testing in go
Date: 2016-04-04 11:00
Tags: go, testing
Status: published

This post is a summary of some of the best resources I've found for explaining how to test [golang](https://golang.org/) applications.

The first section of the article is a list of resources and what I learned from each one. 

The second section is a high level summary of suggestions, as well as some techniques I've used to fill in gaps not directly addressed by other articles or talks.

I conclude with a few packages that may make life easier.

# Article summaries

## [Testing techniques](https://talks.golang.org/2014/testing.slide#1)

> See: [Slides](https://talks.golang.org/2014/testing.slide#1) | [Video](https://www.youtube.com/watch?v=ndmB0bj7eyw)

This slidedeck is a great starting point for learning about testing. It provides a broad overview pretty quickly.

### Writing tests

* Use [table driven tests](http://dave.cheney.net/2013/06/09/writing-table-driven-tests-in-go)
    * Makes adding new test cases very easy.
    * There is even a tool to create these for you: [gotests](https://github.com/cweill/gotests) (I haven't tried this yet)
* Use features of the `*testing.T` object
    * logging, skipping, parallelizing
* Use the [built in coverage tool](http://blog.golang.org/cover) to guide addition of new tests
    * `go test -cover`
* Use `httptest` package.
* Try out the race detection tools as part of your testing process.  Just run tests with `-race` flag.
* Use go's concurrency primitives (locks, channels, waitgroups) to make concurrent tests more robust. Avoid `time.Sleep`.
* Use static analysis.
* If you have a complex package, use the fact that go lets `_test` files access unexported package details to test implementation.
* If you want to enforce testing only the interface, you can use the package name `<package>_test` for your test files.
    * Then they will only be able to access exported methods in the package under test.
* Avoid mocking and faking, and write good broad interfaces instead.


## [Advanced Testung With Go](https://speakerdeck.com/mitchellh/advanced-testing-with-go)

This slidedeck from one of the founders of [Hashicorp](https://www.hashicorp.com/) (the maker of great tools like Vagrant, Packer, Consul, and Terraform) has mostly simple suggestions, with a few neat ideas.

### Writing tests

* Use test fixtures, taking advantage of the fact that `pwd` is set for you when running tests.
* Use flags to generate output files used to compare to expected output in tests.
    * Check these into version control so that any changes can be 'human checked'
* Write test helpers that accept a `*testing.T` object and fail
    * Don't bother returning errors.
* Don't mock networking. Just use network connections directly.
* Don't mock subprocesses. Just run them.
    * If you need to fake it, make a simpler version of the subprocess (a different `cmd.Exec` object) and execute that.
* Try not to test internal api unless implementation is very complex.
    * This ensures you are testing interface and not implementation.
* `go test` is awesome. Avoid frameworks that don't use it.
* When testing time related code, use a time multiplier instead of "fake time".
* Avoid the built in parallel tests feature. Makes tests less reproducable.
    * Instead, run multiple processes yourself if you want to test for concurrency bugs.

### Writing testable code

* Parameterize methods and objects. 
    * Even things that are always the same value in practice could benefit from flexibility when testing.
* Minimize global state. This is very hard to test.
* Getting the scope and size of packages right takes time. Huge and very small packages are not good.


## [Integration testing in Go using docker](https://divan.github.io/posts/integration_testing/)

This article has some good suggestions on testing large complex applications with a lot of dependencies.

### Writing tests

* docker is great for testing things like databases, queues, connections to other complex systems, etc.
* use flags to limit what is included in tests
    * to avoid running long test cases all the time
    * __NOTE__: Others recommend [build tags](https://golang.org/pkg/go/build/) as an alternate solution.
* account for multiple platforms (windows, osx vs linux) using [docker-machine](https://docs.docker.com/machine/)

The package [dockertest](https://github.com/ory-am/dockertest) formalizes a lot of these ideas.


## [Go in production: Testing and validation](https://peter.bourgon.org/go-in-production/#testing-and-validation)

This article from an engineer at SoundCloud has a lot of great suggestions. Testing and validation is just 1 part.

### Writing tests

* use `reflect.DeepEqual` often to test for equality
* use build tags to specify what files should be included in tests
    * this makes it easy to selectively run longer tests as part of integration testing while keeping unit tests fast
* use flags for things like service addresses and use these in your tests
    * essentially these are package level global variables, but at least they are easy to modify

## [Lesser known features of go test](https://splice.com/blog/lesser-known-features-go-test/)

This post by engineers at [splice](https://splice.com/) (a music creation and collaboration service) outlines a lot of nice built in features of `go test`.

### Writing tests

* use the build in `-short` and `-v` flags and the associated `testing.Short()` and `testing.Verbose()` conditionals
    * use these to skip portions of tests 
* use the `-timeout` flag to fail tests that take more than a given amt of time
* use the `-run` flag to run a specific test (e.g. `go test -run TestTheThing`)
* the `<package>_test` package name for tests can be helpful in breaking import cycles
* use the `-parallel` command line flag to control the parallelism of tests
* send multiple package names to `go test` to build and run tests for each package in a separate process (e.g. `go test p1 p2 p3`)
    * this happens naturally when you run `go test ./...`
    * can use `-p` flag to control parallelism when running tests this way
* to get tests to run with multiple processors, do either of:
    * adjust `GOMAXPROCS` to >1
    * use `-cpu` flag to specify the cpu counts you want to run with (e.g. `go test -cpu 1,2 ./...` will run all tests 2X, once with 1 cpu and once with 2 cpus)


# Summary of recommendations

Some things were repeated over and over

* Use table driven tests
* Use the built in testing tool as much as possible, avoiding packages that break it
* Avoid mocking, actually executing code or using interfaces instead


There are also a few things that I picked up that either weren't mentioned elsewhere or just have been helpful to remember.

* For open source projects, [integration with travis CI](https://docs.travis-ci.com/user/languages/go) is very simple
* To run all tests in a project
    * `go test ./...`

And there are a few things I still need to figure out.

* How to share test utilities
    * Unfortunately functions and objects in `*_test.go` files are not available for import by other tests
    * Right now I am adding a `<package>_test_utilities.go` file to packages that provides utilities I can use in other tests
    * This seems to be a common pattern, even seen in the standard library
        * The upside is we access to package internals
        * The downside is we include test-specific code as part of the public interface of our package
    * Some other questions about this
        * [grokbase | Importing from test packages?](http://grokbase.com/t/gg/golang-nuts/136t4f5een/go-nuts-importing-from-test-packages)
        * [StackOverflow | Can I create shared test utilities in go?](http://stackoverflow.com/questions/31794141/can-i-create-shared-test-utilities-in-go)
* How to check equality for json strings
    * I wrote [this utility](https://gist.github.com/turtlemonvh/e4f7404e28387fadb8ad275a99596f67) which loads in json then compares using `reflect`, but I don't love it.


# Useful packages

## [testify](https://github.com/stretchr/testify)

[testify](https://github.com/stretchr/testify) is the only testing-specific package I use regularly.  It plays nice with the standard [testing](https://golang.org/pkg/testing/) package and adds lots of assertions that make declaring tests less verbose. 
I don't use any of the mocking features.
Even this package has dropped http testing utilities for the standard library's [httptest package](https://golang.org/pkg/net/http/httptest/).

## [gometalinter](https://github.com/alecthomas/gometalinter)

I'm just starting to use this package.  It is a wrapper around a bunch of static analysis tools.
If this becomes a regular part of my workflow, I'll loop back around and write about how I use it.

## [viper](https://github.com/spf13/viper)

They're not testing specific at all, but I use [viper](https://github.com/spf13/viper) and [cobra](https://github.com/spf13/cobra) for most of my new go projects, and those packages make working with editable global state very easy.  These makes testing variable configuration very easy.


# The end

I didn't address [performance profiling](http://blog.golang.org/profiling-go-programs) or [benchmarking](http://dave.cheney.net/2013/06/30/how-to-write-benchmarks-in-go), but may do so in a future post.  I will also probably be adding to this post over the next couple weeks.

Still, I hope that was helpful as it was.  If you think I missed something obvious, please [let me know](https://twitter.com/turtlemonvh).

