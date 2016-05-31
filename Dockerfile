FROM ubuntu:16.04
MAINTAINER Jorge Garcia Irazabal <jorge.garcia@bq.com>

RUN apt-get update
RUN apt-get upgrade
RUN apt-get install git -y
RUN apt-get install python -y
RUN apt-get install python-pip -y
RUN apt-get install sudo -y
RUN apt-get install python-tk -y
RUN pip install --upgrade pip
RUN useradd -d /home/w2b -m w2b
RUN su - w2b
WORKDIR /home/w2b
RUN mkdir repos
WORKDIR /home/w2b/repos
RUN git clone https://github.com/bq/web2board.git
WORKDIR web2board
RUN pip install -r requirements.txt
RUN chown w2b -R /home/w2b


CMD sleep 99999999999999