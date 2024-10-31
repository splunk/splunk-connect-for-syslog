#Splunk Connect for Syslog (SC4S) by Splunk, Inc.
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#Splunk Syslog-NG Container Image
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Syslog-NG Container image.
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.


ARG SYSLOGNG_VERSION=4.8.1
FROM ghcr.io/axoflow/axosyslog:${SYSLOGNG_VERSION}


RUN apk add -U --upgrade --no-cache \
      bash \
      build-base \
      curl \
      grep \
      less \
      net-tools \
      netcat-openbsd \
      openssl \
      procps \
      py3-pip \
      libffi-dev \
      shadow \
      socat \
      tzdata \
      wget \
      cargo \
      ca-certificates \
      poetry \
      gdb \
      build-base openssl-dev libffi-dev zlib-dev bzip2-dev xz-dev readline-dev sqlite-dev

RUN wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz \
    && tar xzf Python-3.13.0.tgz \
    && cd Python-3.13.0 \
    && ./configure --without-tests \
    && make altinstall

RUN rm /usr/bin/python3 && ln -s /usr/local/bin/python3.13 /usr/bin/python3 \
    && cd .. \
    && rm -rf Python-3.13.0 Python-3.13.0.tgz \
    && groupadd --gid 1024 syslog \
    && useradd -M -g 1024 -u 1024 syslog \
    && usermod -L syslog \
    && touch /var/log/syslog-ng.out /var/log/syslog-ng.err \
    && chmod 755 /var/log/syslog-ng.*

EXPOSE 514
EXPOSE 601/tcp
EXPOSE 6514/tcp

#Note this is commented out because the default syslog-ng config will try to read
#/dev/log a low priv user cannot read this and the container will fail in SC4S
#and other uses the low user may be selected

HEALTHCHECK --interval=2m --timeout=5s --start-period=30s CMD /usr/sbin/syslog-ng-ctl healthcheck --timeout 5

COPY pyproject.toml /
COPY poetry.lock /

RUN python3 -m venv /var/lib/python-venv \
    && source /var/lib/python-venv/bin/activate \
    && python3 -m pip install --upgrade poetry \
    && poetry export --format requirements.txt | /var/lib/python-venv/bin/pip3 --no-cache-dir install -r /dev/stdin

COPY package/etc/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
COPY package/etc/conf.d /etc/syslog-ng/conf.d
COPY package/etc/pylib /etc/syslog-ng/pylib
COPY package/etc/context_templates /etc/syslog-ng/context_templates
COPY package/etc/test_parsers /etc/syslog-ng/test_parsers
COPY package/etc/local_config /etc/syslog-ng/local_config
COPY package/etc/local_config /etc/syslog-ng/local_config
COPY package/sbin/entrypoint.sh /
COPY package/sbin/source_ports_validator.py /

ENV SC4S_CONTAINER_OPTS=--no-caps
ARG VERSION=unknown
RUN echo $VERSION>/etc/syslog-ng/VERSION

ENTRYPOINT ["/entrypoint.sh"]
