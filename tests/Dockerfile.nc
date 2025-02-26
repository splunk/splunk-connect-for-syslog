ARG SYSLOGNG_VERSION=4.9.0
FROM ghcr.io/axoflow/axosyslog:${SYSLOGNG_VERSION}

RUN apk --no-cache add -U netcat-openbsd
