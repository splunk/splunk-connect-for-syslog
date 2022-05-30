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
FROM registry.access.redhat.com/ubi8:8.5-214

RUN curl -fsSL https://goss.rocks/install | GOSS_VER=v0.3.18 sh

RUN cd /tmp ;\
    dnf install 'dnf-command(copr)' -y ;\
    dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y ;\
    dnf copr enable czanik/syslog-ng336  -y ;\
    dnf install -y \
        tzdata \
        curl wget nc socat openssl\
        syslog-ng syslog-ng-python syslog-ng-http syslog-ng-kafka \
        python39-pip python39-devel \
        procps-ng net-tools less;\
    dnf update -y ;\
    dnf clean all

RUN groupadd --gid 1024 syslog ;\
    useradd -M -g 1024 -u 1024 syslog ;\
    usermod -L syslog

RUN touch /var/log/syslog-ng.out ;\
    touch /var/log/syslog-ng.err ;\
    chmod 755 /var/log/syslog-ng.*


EXPOSE 514
EXPOSE 601/tcp
EXPOSE 6514/tcp

#Note this is commented out because the default syslog-ng config will try to read
#/dev/log a low priv user cannot read this and the container will fail in SC4S
#and other uses the low user may be selected

HEALTHCHECK --interval=10s --retries=6 --timeout=6s CMD /healthcheck.sh

COPY package/etc/goss.yaml /etc/syslog-ng/goss.yaml

COPY pyproject.toml /
COPY poetry.lock /
RUN pip3 install poetry
RUN poetry export --format requirements.txt | pip3 install --user -r /dev/stdin

COPY package/etc/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
COPY package/etc/conf.d /etc/syslog-ng/conf.d
COPY package/etc/pylib /etc/syslog-ng/pylib
COPY package/etc/context_templates /etc/syslog-ng/context_templates
COPY package/etc/test_parsers /etc/syslog-ng/test_parsers
COPY package/etc/local_config /etc/syslog-ng/local_config
COPY package/etc/local_config /etc/syslog-ng/local_config
COPY package/sbin/entrypoint.sh /
COPY package/sbin/healthcheck.sh /

ENV SC4S_CONTAINER_OPTS=--no-caps
ARG VERSION=unknown
RUN echo $VERSION>/etc/syslog-ng/VERSION

ENTRYPOINT ["/entrypoint.sh"]