#Splunk Connect for Syslog (SC4S) by Splunk, Inc.
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
FROM python:3.7

COPY requirements.txt /
RUN pip3 install -r /requirements.txt
RUN pip3 install pytest-xdist
RUN mkdir -p /work/tests
RUN mkdir -p /work/test-results/functional
COPY entrypoint.sh /
COPY wait-for /bin/
COPY ./* /work/tests/
COPY pytest-ci.ini /work/pytest.ini
COPY ./data /work/tests/data
#WORKDIR /work
CMD /entrypoint.sh

