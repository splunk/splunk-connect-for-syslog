#Splunk Connect for Syslog (SC4S) by Splunk, Inc.
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
FROM registry.access.redhat.com/rhel7/rhel

ARG RH_ORG
ARG RH_ACTIVATION

ENV           CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=system --with-jsonc=system --disable-env-wrapper --disable-memtrace --enable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --enable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking"

ENV DISTCHECK_CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=system --with-jsonc=system --disable-env-wrapper --disable-memtrace --enable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --enable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking"
COPY confluent.repo /etc/yum.repos.d/confluent.repo
RUN subscription-manager register --org=$RH_ORG --activationkey=$RH_ACTIVATION --force
RUN subscription-manager repos --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-server-rhscl-7-rpms
RUN yum update -y; yum install wget -y
RUN rpm --import https://packages.confluent.io/rpm/5.2/archive.key
RUN cd /tmp ;\
    wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm ;\
    yum install epel-release-latest-7.noarch.rpm -y ;\
    rm epel-release-latest-7.noarch.rpm
RUN yum install findutils autoconf \
    autoconf-archive automake ca-certificates git libtool pkgconfig bison byacc file \
    flex pcre-devel glib2-devel openssl-devel librdkafka-devel libcurl-devel \
    rh-python36 rh-python36-python-tools rh-python36-scldevel\
    net-snmp-devel \
    libuuid-devel cmake make libxslt docbook-style-xsl gcc-c++ tzdata libxml2 sqlite \
    json-c-devel gnupg wget curl which bzip2 doxygen libsecret ivykis-devel -y

RUN subscription-manager unregister

RUN echo source scl_source enable rh-python36 >>/etc/profile.d/enablepython36.sh ;\
    source scl_source enable rh-python36

RUN CRITERION_VERSION=2.3.3 ;\
    cd /tmp/;\
    wget https://github.com/Snaipe/Criterion/releases/download/v${CRITERION_VERSION}/criterion-v${CRITERION_VERSION}.tar.bz2 ;\
    tar xvf /tmp/criterion-v${CRITERION_VERSION}.tar.bz2;cd /tmp/criterion-v${CRITERION_VERSION} ;\
    cmake -DCMAKE_INSTALL_PREFIX=/usr . ;\
    make install ;\
    ldconfig ;\
    rm -rf /tmp/criterion.tar.bz2 /tmp/criterion-v${CRITERION_VERSION}


COPY syslog-ng /work

RUN source scl_source enable rh-python36 ;\
    cd /work;\
    pip install -r requirements.txt ;\
    ./autogen.sh ;\
    ./configure $CONFIGURE_FLAGS ;\
    make -j -l 2.5 install


FROM registry.access.redhat.com/ubi7/ubi

COPY confluent.repo /etc/yum.repos.d/confluent.repo

RUN cd /tmp ;\
    yum install -y wget ;\
    wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm ;\
    yum install epel-release-latest-7.noarch.rpm -y ;\
    rm epel-release-latest-7.noarch.rpm ;\
    rpm --import https://packages.confluent.io/rpm/5.2/archive.key ;\
    yum install gcc tzdata libdbi libsecret libxml2 sqlite tcp_wrappers librdkafka \
    rh-python36 rh-python36-python-tools libcurl ivykis scl-utils tcp_wrappers-libs curl -y;\
    echo source scl_source enable rh-python36 >>/etc/profile.d/enablepython36.sh ;\
    source scl_source enable rh-python36 ;\
    pip install dumb-init


ENV DEBCONF_NONINTERACTIVE_SEEN=true
ENV SPLUNK_CONNECT_METHOD=hec
ENV SYSLOGNG_HEC_WORKERS=10

RUN source scl_source enable rh-python36 ; curl -fsSL https://goss.rocks/install | GOSS_VER=v0.3.7 sh
COPY goss.yaml /etc/goss.yaml

COPY --from=0 /opt/syslog-ng /opt/syslog-ng
COPY etc/syslog-ng.conf /opt/syslog-ng/etc/syslog-ng.conf
COPY etc/conf.d /opt/syslog-ng/etc/conf.d
COPY etc/context /opt/syslog-ng/etc/context
COPY sbin/entrypoint.sh /sbin/entrypoint.sh

RUN ls -l /opt/syslog-ng/etc/context
RUN mkdir -p /opt/syslog-ng/var/data/disk-buffer
RUN source scl_source enable rh-python36 ;/opt/syslog-ng/sbin/syslog-ng  -V
RUN source scl_source enable rh-python36 ;/opt/syslog-ng/sbin/syslog-ng -t
RUN mkdir -p /var/log/syslog-ng/data/disk-buffer

EXPOSE 514
EXPOSE 601/tcp
EXPOSE 6514/tcp

ENV SPLUNK_CONNECT_METHOD=UF

ENTRYPOINT ["/sbin/entrypoint.sh", "--"]

HEALTHCHECK --interval=1s --timeout=6s CMD source scl_source enable rh-python36 ;goss -g /etc/goss.yaml validate