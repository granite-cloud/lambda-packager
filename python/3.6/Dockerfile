FROM amazonlinux:2017.03 as base

RUN yum -y install git \
    python36 \
    python36-pip \
    python36-devel \
    zip \
    gcc \
    && yum clean all

RUN python3 -m pip install --upgrade pip

ARG VERSION

COPY python/${VERSION}/entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py
CMD ["python3", "/entrypoint.py"]

FROM base as test
COPY python/3.6/requirements-test.pip .
RUN pip install -r requirements-test.pip
COPY tests/python /tests
COPY python/3.6 /src
CMD ["/bin/bash"]
