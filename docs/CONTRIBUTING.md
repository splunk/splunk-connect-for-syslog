#CONTRIBUTING

##Prerequisites

When contributing to this repository, please first discuss the change you wish to make via a GitHub issue or Slack message with the owners of this repository.

##Setup Development Environment

For a basic development environment docker and a bash shell is all you need. For a more complete IDE experience see our wiki (Setup PyCharm)[https://github.com/splunk/splunk-connect-for-syslog/wiki/SC4S-Development-Setup-Using-PyCharm] 

##Contribution Workflow

SC4S is a community project so please consider contributing your efforts! For example, documentation can always use improvement. There's always code that can be clarified, functionality that can be extended, new data filters to develop. If you see something you think should be fixed or added, go for it.

#Feature Requests and Bug Reports

Have ideas on improvements or found a problem? While the community encourages everyone to contribute code, it is also appreciated when someone reports an issue. Please report any issues or bugs you find through GitHub's issue tracker.

If you are reporting a bug, please include the following details:

* Your operating system name and version
* Any details about your local setup that might be helpful in troubleshooting (ex. container runtime you use, etc.)
* Detailed steps to reproduce the bug
* We want to hear about you enhancements as well. Feel free to submit them as issues:

* Explain in detail how they should work
* Keep the scope as narrow as possible. This will make it easier to implement

##Fixing Issues

Look through our issue tracker to find problems to fix! Feel free to comment and tag community members of this project with any questions or concerns.

##Pull Requests

What is a "pull request"? It informs the project's core developers about the changes you want to review and merge. Once you submit a pull request, it enters a stage of code review where you and others can discuss its potential modifications and even add more commits to it later on.

If you want to learn more, please consult this tutorial on how pull requests work in the GitHub Help Center.

Here's an overview of how you can make a pull request against this project:

* Fork the Splunk-connect-for-syslog GitHub repository
* Clone your fork using git and create a branch off develop
$ git clone git@github.com:YOUR_GITHUB_USERNAME/splunk-connect-for-syslog.git
$ cd splunk-connect-for-syslog
* This project uses 'develop' for all development activity, so create your branch off that
$ git checkout -b your-bugfix-branch-name develop
* Run all the tests to verify your environment
$ cd splunk-connect-for-syslog
$ ./test-with-compose.sh
* Make your changes, commit and push once your tests have passed
$ git commit -m ""
$ git push
* Submit a pull request through the GitHub website using the changes from your forked codebase

##Code Review

There are two aspects of code review: giving and receiving.
To make it easier for your PR to receive reviews, consider the reviewers will need you to:

* Follow the project coding conventions
* Write good commit messages
* Break large changes into a logical series of smaller patches which individually make easily understandable changes, and in aggregate solve a broader issue
* Reviewers, the people giving the review, are highly encouraged to revisit the Code of Conduct and must go above and beyond to promote a collaborative, respectful community.
* When reviewing PRs from others The Gentle Art of Patch Review suggests an iterative series of focuses which is designed to lead new contributors to positive collaboration without inundating them initially with nuances:
* Is the idea behind the contribution sound?
* Is the contribution architected correctly?
* Is the contribution polished?
* For this project, we require that at least 2 approvals are given and a build from our continuous integration system is successful off of your branch. Please note that any new changes made with your existing pull request during review will automatically unapprove and retrigger another build/round of tests.

##Testing

Testing is the responsibility of all contributors. In general, we try to adhere to TDD, writing the test first.
There are multiple types of tests. The location of the test code varies with type, as do the specifics of the environment needed to successfully run the test.

* Review existing tests in the tests folder of the repo

We could always use improvements to our documentation! Anyone can contribute to these docs - whether you’re new to the project, you’ve been around a long time, and whether you self-identify as a developer, an end user, or someone who just can’t stand seeing typos. What exactly is needed?

* More complementary documentation. Have you perhaps found something unclear?
* More examples or generic templates that others can use.
* Blog posts, articles and such – they’re all very appreciated.
* You can also edit documentation files directly in the GitHub web interface, without creating a local copy. This can be convenient for small typos or grammar fixes.