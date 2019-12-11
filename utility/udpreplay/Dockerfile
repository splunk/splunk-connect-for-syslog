#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
FROM registry.access.redhat.com/rhel7/rhel

ARG RH_ORG
ARG RH_ACTIVATION

RUN subscription-manager register --org=$RH_ORG --activationkey=$RH_ACTIVATION --force
RUN subscription-manager repos --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-server-rhscl-7-rpms

RUN yum -y install libpcap-devel gcc-c++ git findutils autoconf \
    autoconf-archive automake ca-certificates git libtool pkgconfig bison byacc file \
    flex pcre-devel glib2-devel openssl-devel librdkafka-devel libcurl-devel \
    rh-python36 rh-python36-python-tools rh-python36-scldevel\
    net-snmp-devel \
    libuuid-devel make libxslt docbook-style-xsl gcc-c++ tzdata libxml2 sqlite \
    json-c-devel gnupg wget curl which bzip2 doxygen libsecret ivykis-devel -y

RUN cd /tmp ;\
    wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm ;\
    yum install epel-release-latest-7.noarch.rpm -y ;\
    rm epel-release-latest-7.noarch.rpm ;\
    yum install -y cmake3 boost-devel



RUN cd ~ ; git clone https://github.com/ska-sa/udpreplay.git
RUN cd ~/udpreplay && \
  ./bootstrap.sh && \
  ./configure && \
  make && \
  make install  && \
  cd ~ ; rm -Rf udpreplay

RUN subscription-manager unregister
ENTRYPOINT ["/bin/tail", "-f", "/dev/null"]
