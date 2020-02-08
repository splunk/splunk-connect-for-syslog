# Development setup (BETA)

## Get Docker

Development requires Docker desktop available for windows + and mac or Docker CE available for Linux visit (Docker)[https://www.docker.com/get-started]
for download instructions

## Setup VS Code IDE

VS Code provides a free IDE experience that is effective for daily development with SC4S visit (Microsoft)[https://code.visualstudio.com/docs/introvideos/basics]
to download and install for your plaform (windows/mac/linux)

## Fork and Clone the github repository

Visit our repository at (Github)[https://github.com/splunk/splunk-connect-for-syslog] and "fork" our repository this will allow you to make changes and submit pull requests.

![How to Fork](gh_fork.png)

Click the clone icon and select the location

![How to Clone](gh_clone.png)

## Setup the project and install requirements

The follow steps are only required on the first time run.

* Install VS Code Extensions S
    * Python
    * Test Explorer
    * "Python Test Explorer"
* Click the "Run/Debug" bug icon
* Select the "Setup Project" task and click the Green play icon
* Select the "Setup Requirements" task and click the Green play icon

![VS Code setup](vsc_run.png)

## Click the test lab icon

* Run all tests this will appear to do nothing for a period system fan may spin loud whiletests are run icons on each test will turn green
or red to indicate pass fail however VS Code does not show the status of status until the tests complete

![VS Code Debug](vsc_debug.png)

