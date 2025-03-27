FROM python:3.12-alpine AS build
RUN apk add build-base python3-dev linux-headers pcre-dev jpeg-dev zlib-dev
RUN pip install --upgrade pip
RUN pip install pillow uwsgi

FROM python:3.12-alpine AS deps
WORKDIR /twitfix
COPY requirements.txt requirements.txt
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
RUN pip install -r requirements.txt
RUN pip install yt-dlp

FROM python:3.12-alpine AS runner
EXPOSE 9000
RUN apk add pcre-dev jpeg-dev zlib-dev bash nginx supervisor

COPY ./supervisord.conf /etc/supervisord.conf
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY twitfix_proxy.conf /etc/nginx/http.d/default.conf

WORKDIR /twitfix

COPY --from=build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
