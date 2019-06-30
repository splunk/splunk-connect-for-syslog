FROM python:3.7

COPY requirements.txt /

RUN pip3 install -r /requirements.txt
RUN mkdir -p /work/tests
RUN mkdir -p /work/test-results/functional
#WORKDIR /work
CMD cd /work;python -m pytest --junitxml=/work/test-results/functional/functional.xml
