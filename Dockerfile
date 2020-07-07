FROM python:3.7

RUN echo "Asia/Shanghai" > /etc/timezone
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

RUN groupadd --system supervisord && useradd --system --gid supervisord supervisord

COPY ./util/sources.list /etc/apt/sources.list

RUN cat /etc/apt/sources.list
RUN rm -Rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y supervisor\
    && mkdir -p /var/log/supervisord/ \
    && chown -R supervisord:supervisord /var/log/supervisord

RUN mkdir -p /opt/ssl-cert-exporter

WORKDIR /opt/ssl-cert-exporter

COPY . .

ADD supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN export PYTHONPATH=$PYTHONPATH:/opt/ssl-cert-exporter

EXPOSE 8800

CMD ["/usr/bin/supervisord","-c","/etc/supervisor/supervisord.conf"]
