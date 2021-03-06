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
FROM registry.access.redhat.com/ubi8/ubi

COPY --from=hairyhenderson/gomplate:v3.5.0 /gomplate /usr/local/bin/gomplate

RUN curl -fsSL https://goss.rocks/install | GOSS_VER=v0.3.13 sh

RUN cd /tmp ;\
    dnf install 'dnf-command(copr)' -y ;\
    dnf install http://mirror.centos.org/centos/8/AppStream/x86_64/os/Packages/libnet-1.1.6-15.el8.x86_64.rpm -y; \
    dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y ;\
    dnf copr enable czanik/syslog-ng329  -y ;\
    dnf install tzdata curl wget nc perl syslog-ng syslog-ng-python syslog-ng-http syslog-ng-kafka syslog-ng-afsnmp net-snmp python3-pip gcc python3-devel procps-ng -y ;\
    dnf update -y

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
#USER syslog

ENTRYPOINT ["/entrypoint.sh"]

HEALTHCHECK --timeout=6s CMD curl -s --fail http://localhost:8080/healthz || exit 1

COPY package/etc/goss.yaml.tmpl /etc/syslog-ng/goss.yaml.tmpl

COPY package/etc/syslog-ng.conf.tmpl /etc/syslog-ng/syslog-ng.conf.tmpl
COPY package/etc/conf.d /etc/syslog-ng/conf.d
COPY package/etc/go_templates /etc/syslog-ng/go_templates
COPY package/etc/context_templates /etc/syslog-ng/context_templates
COPY package/etc/local_config /etc/syslog-ng/local_config
COPY package/etc/local_config /etc/syslog-ng/local_config
COPY package/etc/patterndb.d /etc/syslog-ng/patterndb.d
COPY package/etc/patterndb-raw.d /etc/syslog-ng/patterndb-raw.d
COPY package/sbin/entrypoint.sh /

COPY package/snmp/snmptrapd.conf /etc/snmp/
ENV SC4S_MIGRATE_CONFIG=yes
ENV SC4S_CONTAINER_OPTS=--no-caps
ARG VERSION=unknown
RUN echo $VERSION>/etc/syslog-ng/VERSION
