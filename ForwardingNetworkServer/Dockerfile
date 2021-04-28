FROM python:3.7

ENV APP_HOME /app

# RUN mkdir $APP_HOME
WORKDIR $APP_HOME

ADD requirements.txt $APP_HOME/
ADD ./ $APP_HOME/

RUN apt-get update
RUN apt-get install nano

#EXPOSE 9999/udp

RUN pip3 install -r requirements.txt

#CMD ["python","-u","server.py"]
