FROM python:3-alpine

ENV DOCKNV_USER_PATH    /config
ENV DOCKNV_PROJECT_PATH /project

COPY . /src
WORKDIR /src
RUN pip install -e . --upgrade

WORKDIR /project

CMD ["docknv"]
