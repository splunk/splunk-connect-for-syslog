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

- Update the splunkbase username and password in .env this allows the splunk container to install required add-ons for the demo

- Start the demo environment

```bash
./demo-with-compose.sh
```

- Login to splunk by browsing to http://127.0.0.1:8000 user name admin password "Changed@11"

- Search the main index to see indexed events

```spl
index = *
```
