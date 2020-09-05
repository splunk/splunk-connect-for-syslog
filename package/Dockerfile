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

#We first build a "builder" image as a layer this is handy when working locally to reduce build time
FROM centos:centos8 AS builder
RUN dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y ;\
    dnf install 'dnf-command(config-manager)' -y ;\
    dnf config-manager --set-enabled PowerTools -y; \
    dnf update -y ;\
    dnf upgrade ;\
    dnf install -y ca-certificates wget curl  ;\
    dnf group install "Development Tools" -y ;\
    dnf install findutils autoconf \
    automake git libtool pkgconfig bison byacc file \
    flex pcre-devel glib2-devel openssl-devel libcurl-devel \
    python3 python3-devel perl-devel \
    libuuid-devel cmake make libxslt gcc-c++ tzdata libxml2 sqlite \
    gnupg which bzip2 libsecret ivykis-devel autoconf-archive json-c-devel libzstd-devel -y

RUN CRITERION_VERSION=2.3.3 ;\
    cd /tmp/;\
    wget https://github.com/Snaipe/Criterion/releases/download/v${CRITERION_VERSION}/criterion-v${CRITERION_VERSION}.tar.bz2 ;\
    tar xvf /tmp/criterion-v${CRITERION_VERSION}.tar.bz2;cd /tmp/criterion-v${CRITERION_VERSION} ;\
    cmake -DCMAKE_INSTALL_PREFIX=/usr . ;\
    make install ;\
    ldconfig ;\
    rm -rf /tmp/criterion.tar.bz2 /tmp/criterion-v${CRITERION_VERSION}

# Using the builder layer we will build syslog-ng and make this a layer we can copy from
FROM builder as syslog-ng

ARG BRANCH_SNMP=master
ENV SNMP_VERSION=$BRANCH_SNMP
RUN echo cloning $SNMP_VERSION ;\
    git clone https://github.com/net-snmp/net-snmp.git /work/net-snmp ;\
    cd /work/net-snmp ;\
    if [ "$SNMP_VERSION" != "master" ]; then git checkout tags/$SNMP_VERSION; fi

ENV CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=system --with-jsonc=system --disable-env-wrapper --disable-memtrace --disable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --enable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking --with-net-snmp=/opt/net-snmp/bin"

ENV DISTCHECK_CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=system --with-jsonc=system --disable-env-wrapper --disable-memtrace --disable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --enable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking --with-net-snmp=/opt/net-snmp/bin"

RUN cd /work/net-snmp;\
    ./configure --with-default-snmp-version="3" --with-sys-contact="contact" --with-sys-location="unknown" --with-logfile="/var/log/snmpd.log" --with-persistent-directory="/var/net-snmp" --prefix=/opt/net-snmp;\
    make ;\
    make install

ARG KAFKA_VERSION=master
ENV KAFKA_VERSION=$KAFKA_VERSION
RUN cd /work ;\
    echo cloning $KAFKA_VERSION ;\
    git clone https://github.com/edenhill/librdkafka.git /work/librdkafka ;\
    cd /work/librdkafka  ;\
    if [ "$KAFKA_VERSION" != "master" ]; then git checkout tags/$KAFKA_VERSION; fi
RUN cd /work/librdkafka; ./configure --prefix=/usr --libdir=/usr/lib64;\
    make ;\    
    make install


ARG BRANCH_SYSLOGNG=master
ENV SYSLOG_VERSION=$BRANCH_SYSLOGNG
COPY syslog-ng /work/syslog-ng

RUN cd /work/syslog-ng;\
    pip3 install -r requirements.txt ;\
    ./autogen.sh ;\
    ./configure $CONFIGURE_FLAGS ;\
    make -j -l 2.5 install

#This is the actual splunk-syslog-ng container with syslog-ng and goss
FROM registry.access.redhat.com/ubi8/ubi as base

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

HEALTHCHECK --timeout=6s CMD curl -s --fail http://localhost:8080/healthz || exit 1

FROM base

COPY --from=hairyhenderson/gomplate:v3.5.0 /gomplate /usr/local/bin/gomplate

COPY goss.yaml.tmpl goss.yaml.tmpl

COPY etc/syslog-ng.conf.tmpl /opt/syslog-ng/etc/syslog-ng.conf.tmpl
COPY etc/conf.d /opt/syslog-ng/etc/conf.d
COPY etc/go_templates /opt/syslog-ng/etc/go_templates
COPY etc/context_templates /opt/syslog-ng/etc/context_templates
COPY etc/local_config /opt/syslog-ng/etc/local_config
COPY reset_persist /opt/syslog-ng/etc/
COPY sbin/entrypoint.sh /

RUN mkdir -p /opt/syslog-ng/var/log/
COPY snmp/snmptrapd.conf /opt/net-snmp/etc/snmp/
COPY VERSION /

RUN  /opt/syslog-ng/sbin/syslog-ng -V

#USER [syslog]