#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
FROM ubuntu:rolling

RUN apt-get update ;apt-get install -y build-essential autoconf wget git libboost-all-dev libpcap-dev libtool autogen


RUN cd ~ ; git clone https://github.com/ska-sa/udpreplay.git
RUN cd ~/udpreplay && \
  ./bootstrap.sh && \
  ./configure && \
  make && \
  make install  && \
  cd ~ ; rm -Rf udpreplay

RUN cd ~ ; git clone https://github.com/GabrielGanne/tcpreplay.git
RUN cd ~/tcpreplay && \
    ./autogen.sh; ./configure; make install
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
