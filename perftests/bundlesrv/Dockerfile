FROM registry.access.redhat.com/ubi7/ubi as build

COPY scenarios /scenarios

RUN yum install zip -y

RUN mkdir /bundles

RUN cd /scenarios;./build.sh;cp *.zip /bundles

FROM nginx:stable

COPY ./ngnix.conf /etc/nginx/conf.d/default.conf
COPY --from=build /bundles/ /var/www
