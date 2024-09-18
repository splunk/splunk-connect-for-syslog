# install requirements in venv
FROM python:3.12 AS venv_builder
RUN pip install ansible~=6.1.0 --no-cache-dir
RUN pip install pywinrm>=0.4.2 --no-cache-dir
RUN pip install ansible-lint>=6.0.0 --no-cache-dir

WORKDIR /opt
COPY ./ansible .
COPY ./charts .

RUN apt-get update -y
RUN apt-get install parallel -y
RUN apt-get install sshpass

ENV ANSIBLE_CONFIG /opt/ansible.cfg
ENV ANSIBLE_HOST_KEY_CHECKING False
