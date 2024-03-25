FROM docker.io/python:3.9
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install --no-cache-dir -r requirements.txt

RUN printf 'HostkeyAlgorithms ssh-dss,ssh-rsa\nKexAlgorithms +diffie-hellman-group1-sha1,diffie-hellman-group14-sha1' >> /etc/ssh/ssh_config

COPY . /usr/src/app

RUN chgrp -R 0 . && \
    chmod -R g+rwX .

EXPOSE 8080

ENTRYPOINT ["python3"]

CMD ["-m", "swagger_server"]