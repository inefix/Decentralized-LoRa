FROM python:3.7

ENV APP_HOME /app

# RUN mkdir $APP_HOME
WORKDIR $APP_HOME

ADD requirements.txt $APP_HOME/
# ADD ./ $APP_HOME/

RUN apt-get update
RUN apt-get install nano -y
RUN apt-get install git -y

#EXPOSE 9999/udp

RUN pip3 install -r requirements.txt

RUN git clone https://github.com/inefix/pycose && cd pycose && pip3 install .

#CMD ["python","-u","server.py"]
