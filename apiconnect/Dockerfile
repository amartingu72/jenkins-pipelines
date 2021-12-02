FROM node:alpine

# Install python/pip
ENV PYTHONUNBUFFERED=1
WORKDIR /apiconnect
RUN sed -i 's/https/http/' /etc/apk/repositories
RUN set -x && apk -v --update add --no-cache  python3 curl
#RUN ln -sf python3 /usr/bin/python3
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#Install apic
RUN npm -g install apiconnect

#Copy scritps
ADD scripts . 

#Intall pip modules
RUN pwd 1>&2
RUN pip install -r "requirements.txt"


