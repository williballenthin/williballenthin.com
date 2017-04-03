FROM jekyll/jekyll

RUN echo "" >> /etc/apk/repositories && \
    echo "http://dl-cdn.alpinelinux.org/alpine/v3.4/community" >> /etc/apk/repositories && \
    apk update && \
    apk add openjdk8 && \
    gem install s3_website && \
    s3_website install

RUN mkdir /code && \
    cd /code && \
    git clone https://github.com/williballenthin/williballenthin.com.git

ADD ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
