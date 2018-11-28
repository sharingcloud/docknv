FROM ubuntu:14.04

RUN apt-get update -y
RUN apt-get install python-dev python-pip ipython-notebook vim graphviz -y
RUN pip install graphviz

CMD ipython notebook --profile=nbserver

EXPOSE 8888
