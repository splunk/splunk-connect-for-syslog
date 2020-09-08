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
ARG SC4S_BASE_IMAGE=base
FROM splunk/scs:${SC4S_BASE_IMAGE}

RUN cd /tmp ;\
    dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y; \
    dnf update -y ;\
    dnf install wget gcc tzdata libdbi libsecret libxml2 sqlite libzstd\
    python3 libcurl ivykis scl-utils curl wget openssl nc perl -y; 

ENV DEBCONF_NONINTERACTIVE_SEEN=true

RUN curl -fsSL https://goss.rocks/install | GOSS_VER=v0.3.13 sh

COPY --from=syslog-ng /opt/syslog-ng /opt/syslog-ng
COPY --from=syslog-ng /opt/net-snmp /opt/net-snmp
COPY --from=syslog-ng /work/librdkafka /work/librdkafka

RUN groupadd --gid 1024 syslog ;\
    useradd -M -g 1024 -u 1024 syslog ;\
    usermod -L syslog

RUN mkdir -p /opt/net-snmp/etc/snmp

RUN cd /work/librdkafka ;\
    make install ;\
    cd ..; rm -rf /work/librdkafka

RUN chown :1024 /opt/syslog-ng/etc ;\
    chmod 775 /opt/syslog-ng/etc ;\
    chown :1024 /opt/syslog-ng/var ;\
    chmod 775 /opt/syslog-ng/var ;\
    touch /var/log/syslog-ng.out ;\
    touch /var/log/syslog-ng.err ;\
    chmod 755 /var/log/syslog-ng.*


EXPOSE 514
EXPOSE 601/tcp
EXPOSE 6514/tcp

#Note this is commented out because the default syslog-ng config will try to read
#/dev/log a low priv user cannot read this and the container will fail in SC4S
#and other uses the low user may be selected
#USER syslog

RUN /opt/syslog-ng/sbin/syslog-ng -V

ENTRYPOINT ["/entrypoint.sh", "-F"]

HEALTHCHECK --timeout=6s CMD curl -s --fail http://localhost:8080/healthz || exit 1

FROM base

COPY --from=hairyhenderson/gomplate:v3.5.0 /gomplate /usr/local/bin/gomplate

COPY package/goss.yaml.tmpl goss.yaml.tmpl

COPY package/etc/syslog-ng.conf.tmpl /opt/syslog-ng/etc/syslog-ng.conf.tmpl
COPY package/etc/conf.d /opt/syslog-ng/etc/conf.d
COPY package/etc/go_templates /opt/syslog-ng/etc/go_templates
COPY package/etc/context_templates /opt/syslog-ng/etc/context_templates
COPY package/etc/local_config /opt/syslog-ng/etc/local_config
COPY package/reset_persist /opt/syslog-ng/etc/
COPY package/sbin/entrypoint.sh /

RUN mkdir -p /opt/syslog-ng/var/log/
COPY package/snmp/snmptrapd.conf /opt/net-snmp/etc/snmp/
COPY package/VERSION /opt/syslog-ng/etc

RUN  /opt/syslog-ng/sbin/syslog-ng -V

#USER [syslog]