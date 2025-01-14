FROM docker.io/python:3.11-alpine
EXPOSE 8080
WORKDIR /src

# python stuff
RUN apk add --no-cache bash gcompat py3-setuptools
RUN apk add --no-cache --virtual certbot-build gcc libc-dev libffi-dev \
 && pip install --no-cache-dir --upgrade pip wheel \
 && pip install --no-cache-dir 'certbot==2.11.0' \
 && certbot --version \
 && apk del certbot-build
 
# get oc
RUN apk add --no-cache --virtual oc-build wget tar \
 && wget -qO- --no-check-certificate https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable-4.14/openshift-client-linux.tar.gz | tar -zxvf - -C /usr/local/bin \
                                    
 && apk del oc-build
 
# clean up
RUN rm -rf /var/cache/apk/*
 
RUN pip install --no-cache-dir 'openshift-client'

# copy scripts
COPY src/maxcert.py /src
COPY src/cron.py /src

# copy ocp stuff
COPY ocp/maxcert_np.yaml /ocp/maxcert_np.yaml
COPY ocp/maxcert_svc.yaml /ocp/maxcert_svc.yaml
COPY ocp/maxcert-route.yaml /ocp/maxcert-route.yaml

# copy cerbot settings
COPY bot/certbot.ini /bot/certbot.ini

CMD ["/bin/sh", "-c", "python -u cron.py"]
