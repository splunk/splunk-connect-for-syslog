# install requirements in venv
FROM python:3.14 AS venv_builder
RUN pip install ansible~=6.1.0 --no-cache-dir \
    && pip install pywinrm>=0.4.2 --no-cache-dir \
    && pip install ansible-lint>=6.0.0 --no-cache-dir

WORKDIR /opt
COPY ./ansible .
COPY ./charts .

RUN apt update -y \
    && apt install --no-install-recommends -y build-essential parallel \
    && apt install --no-install-recommends -y sshpass \
    && apt clean

ENV ANSIBLE_CONFIG /opt/ansible.cfg
ENV ANSIBLE_HOST_KEY_CHECKING False
