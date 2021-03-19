FROM ubuntu:18.04

WORKDIR /usr/src/app
COPY . .
RUN apt update
RUN apt -y upgrade
RUN apt -y install git wget pkg-config build-essential cmake autoconf libtool zlib1g-dev lsb-release

RUN apt -y install graphviz swig python3-dev python3-wheel python3-setuptools python3-six python3-pip unzip libgraphviz-dev pkg-config gcc g++ make python3-numpy python3-numpy-dev libssl-dev musl-dev libffi-dev

RUN pip3 install pyyaml pygraphviz uvloop==0.8.1
RUN pip3 install -r requirements.txt
RUN unzip or-tools-6.10.zip
RUN cd or-tools-6.10 && make
RUN python3 -m pip install -U --user ortools==6.10.6025


EXPOSE 8001

CMD python3 routes.py