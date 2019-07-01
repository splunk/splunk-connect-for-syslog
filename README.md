# splunk-connect-for-syslog

Splunk Connect for Syslog is an open source packaged solution for 
getting data into Splunk using syslog-ng (OSE) and the Splunk 
HTTP event Collector. 

# Use the demo

The Splunk Connect for syslog demo uses docker and docker compose
to configure a instance of Splunk along with syslog-ng and a test
harness to simulate a mix of events. Ensure git, docker and docker-compose
are pre-installed and working prior to continuing.


- Clone the repository and cd into directory

```bash
git clone git@github.com:splunk/splunk-connect-for-syslog.git
cd splunk-connect-for-syslog
```

- Create a working .env file * Note for demo purposes this file does not need to be modified

```bash
cp .env.template .env
```

- Start the demo environment

```bash
./demo-with-compose.sh
```

- Login to splunk by browsing to http://127.0.0.1:8000 user name admin password "Changed@11"

- Search the main index to see indexed events

```spl
index = main
```

# License



Configuration and documentation licensed subject to [CC0](LICENSE-CC0)

Code and scripts licensed subject to [BSD-2-Clause](LICENSE-BSD2) 