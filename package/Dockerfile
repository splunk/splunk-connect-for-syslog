FROM registry.access.redhat.com/rhel7/rhel

ENV           CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=internal --with-jsonc=system --disable-env-wrapper --disable-memtrace --enable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --enable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking"

ENV DISTCHECK_CONFIGURE_FLAGS="--prefix=/opt/syslog-ng --with-ivykis=internal --with-jsonc=system --disable-env-wrapper --disable-memtrace --enable-tcp-wrapper --disable-linux-caps --disable-man-pages --enable-all-modules --enable-force-gnu99 --enable-json --enable-native --enable-python --enable-http --enable-kafka --disable-java --disable-java-modules --disable-spoof_source --disable-sun_streams --disable-sql --disable-pacct --disable-mongodb --disable-amqp --disable-stomp --disable-redis --disable-systemd --disable-geoip --disable-geoip2 --disable-riemann --disable-smtp --disable-snmp_dest --with-python=3 --enable-dynamic-linking"
COPY confluent.repo /etc/yum.repos.d/confluent.repo
RUN subscription-manager register --org=12579482 --activationkey=dev1 --force
RUN subscription-manager repos --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-server-rhscl-7-rpms
RUN subscription-manager repos --enable "rhel-*-optional-rpms" --enable "rhel-*-extras-rpms"  --enable "rhel-ha-for-rhel-*-server-rpms"
RUN rpm --import https://packages.confluent.io/rpm/5.2/archive.key
RUN yum install findutils autoconf \
    autoconf-archive automake ca-certificates git libtool pkgconfig bison byacc file \
    flex pcre-devel glib2-devel openssl-devel librdkafka-devel libcurl-devel \
    rh-python36 rh-python36-python-tools rh-python36-scldevel\
    net-snmp-devel \
    libuuid-devel cmake make libxslt docbook-style-xsl gcc-c++ tzdata libxml2 sqlite \
    json-c-devel gnupg wget curl which bzip2 doxygen libsecret -y

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


RUN source scl_source enable rh-python36 ;\
    mkdir /work ;\
    cd /work;\
    git clone https://github.com/balabit/syslog-ng.git;\
    cd syslog-ng;\
    pip install -r requirements.txt ;\
    ./autogen.sh ;\
    ./configure $CONFIGURE_FLAGS ;\
    make -j -l 2.5 install


FROM registry.access.redhat.com/ubi7/ubi

COPY confluent.repo /etc/yum.repos.d/confluent.repo

RUN rpm --import https://packages.confluent.io/rpm/5.2/archive.key ;\
    yum install tzdata libdbi libsecret libxml2 sqlite tcp_wrappers librdkafka \
    rh-python36 rh-python36-python-tools libcurl -y;\
    echo source scl_source enable rh-python36 >>/etc/profile.d/enablepython36.sh

COPY --from=0 /opt/syslog-ng /opt/syslog-ng