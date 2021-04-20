ARG SPLUNK_VERSION=latest
FROM splunk/splunk:$SPLUNK_VERSION

COPY deps/build/addonfactory_test_matrix_splunk/packages/all/common/ /opt/splunk/etc/apps/
COPY deps/build/addonfactory_test_matrix_splunk/packages/all/sh/ /opt/splunk/etc/apps/