#Splunk Connect for Syslog (SC4S) by Splunk, Inc.
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
FROM centos:centos8


ENV CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=system --with-jsonc=system --disable-env-wrapper --disable-memtrace --disable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --disable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking"

ENV DISTCHECK_CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=system --with-jsonc=system --disable-env-wrapper --disable-memtrace --disable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --disable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking"

RUN dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y ;\
    dnf install 'dnf-command(config-manager)' -y ;\
    dnf config-manager --set-enabled PowerTools -y; \
    dnf update -y ;\
    dnf upgrade

RUN dnf group install "Development Tools" -y ;\
    dnf install findutils autoconf \
    autoconf automake ca-certificates git libtool pkgconfig bison byacc file \
    flex pcre-devel glib2-devel openssl-devel libcurl-devel \
    python3 python3-devel \
    net-snmp-devel \
    libuuid-devel cmake make libxslt gcc-c++ tzdata libxml2 sqlite \
    gnupg wget curl which bzip2 libsecret ivykis-devel autoconf-archive json-c-devel -y


RUN CRITERION_VERSION=2.3.3 ;\
    cd /tmp/;\
    wget https://github.com/Snaipe/Criterion/releases/download/v${CRITERION_VERSION}/criterion-v${CRITERION_VERSION}.tar.bz2 ;\
    tar xvf /tmp/criterion-v${CRITERION_VERSION}.tar.bz2;cd /tmp/criterion-v${CRITERION_VERSION} ;\
    cmake -DCMAKE_INSTALL_PREFIX=/usr . ;\
    make install ;\
    ldconfig ;\
    rm -rf /tmp/criterion.tar.bz2 /tmp/criterion-v${CRITERION_VERSION}


COPY syslog-ng /work

RUN cd /work;\
    pip3 install -r requirements.txt ;\
    ./autogen.sh ;\
    ./configure $CONFIGURE_FLAGS ;\
    make -j -l 2.5 install


FROM registry.access.redhat.com/ubi8/ubi

RUN cd /tmp ;\
    dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm -y; \
    dnf update -y ;\
    dnf install wget gcc tzdata libdbi libsecret libxml2 sqlite \
    python3 libcurl ivykis scl-utils curl wget openssl -y

ENV DEBCONF_NONINTERACTIVE_SEEN=true

RUN curl -fsSL https://goss.rocks/install | GOSS_VER=v0.3.7 sh
COPY goss.yaml /etc/goss.yaml

COPY --from=0 /opt/syslog-ng /opt/syslog-ng

RUN curl -o /usr/local/bin/gomplate -sSL https://github.com/hairyhenderson/gomplate/releases/download/v3.5.0/gomplate_linux-amd64-slim && \
    chmod 755 /usr/local/bin/gomplate


COPY etc/syslog-ng.conf /opt/syslog-ng/etc/syslog-ng.conf
COPY etc/conf.d /opt/syslog-ng/etc/conf.d
COPY etc/go_templates /opt/syslog-ng/etc/go_templates
COPY etc/context_templates /opt/syslog-ng/etc/context_templates
COPY etc/local_config /opt/syslog-ng/etc/local_config

COPY sbin/entrypoint.sh /
RUN mkdir -p /opt/syslog-ng/var/data/disk-buffer
RUN source scl_source enable rh-python36 ;/opt/syslog-ng/sbin/syslog-ng -V

COPY VERSION /

EXPOSE 514
EXPOSE 601/tcp
EXPOSE 6514/tcp

ENTRYPOINT ["/entrypoint.sh", "-F"]

HEALTHCHECK --start-period=15s --interval=30s --timeout=6s CMD goss -g /etc/goss.yaml validate