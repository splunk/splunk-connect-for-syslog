ARG SYSLOGNG_VERSION=4.8.1
FROM ghcr.io/axoflow/axosyslog:${SYSLOGNG_VERSION}

RUN apk add -U netcat-openbsd
