FROM python:3.7

ENV APP_HOME /app

WORKDIR $APP_HOME

ADD requirements.txt $APP_HOME/

RUN apt-get update
RUN apt-get install nano -y
RUN apt-get install git -y

RUN pip3 install -r requirements.txt

RUN git clone https://github.com/inefix/pycose && cd pycose && pip3 install .
