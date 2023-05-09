FROM python:3.9-slim-buster
COPY requirements.txt /root/
WORKDIR /root
RUN apt-get update && apt-get install -y gcc \
git \
musl-dev \
openrc \
libxslt-dev \
libxml2-dev \
apache2 \
apache2-dev && \
pip3 install --upgrade pip && \
pip3 install -r requirements.txt
ARG CACHE_BUST
RUN pip3 install git+https://github.com/hed-standard/hed-python/@master && \
mkdir -p /var/www/localhost/htdocs && \
cp /etc/mime.types /var/www/mime.types && \
mkdir -p /var/log/hedtools && \
chown -R www-data:www-data /var/log/hedtools && \
mkdir -p /var/cache/schema_cache && \
chown -R www-data:www-data /var/cache/schema_cache
COPY httpd.conf /etc/apache2/apache2.conf
COPY ./hedtools /var/www/hedtools/
COPY ./hedtools/hedweb /var/www/hedtools/hedweb/
ENTRYPOINT /usr/sbin/apache2 -D FOREGROUND -f /etc/apache2/apache2.conf
ENV HEDTOOLS_CONFIG_CLASS=config.ProductionConfig
