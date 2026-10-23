# install requirements in venv
FROM python:3.15@sha256:67ee282bdbe5ece1e38ea94fa68f1420e969e6176e6c826b9acc931055011bfb AS venv_builder

RUN pip install --require-hashes --only-binary :all: \
    ansible~=6.1.0 --no-cache-dir \
    && pip install --require-hashes --only-binary :all: \
    pywinrm>=0.4.2 --no-cache-dir \
    && pip install --require-hashes --only-binary :all: \
    ansible-lint>=6.0.0 --no-cache-dir

WORKDIR /opt
COPY ./ansible .
COPY ./charts .

RUN apt update -y \
    && apt install --only-binary :all: \
    --no-install-recommends -y build-essential parallel \
    && apt install --only-binary :all: \
    --no-install-recommends -y sshpass \
    && apt clean

ENV ANSIBLE_CONFIG /opt/ansible.cfg
ENV ANSIBLE_HOST_KEY_CHECKING False
