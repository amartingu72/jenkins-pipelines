FROM pull node:16.13.1-alpine

# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

#Install apic
RUN npm –g install apiconnect

#Intall pip modules
RUN pip install -r "scripts/requirements.txt"

#Copy scritps
ADD scripts .
