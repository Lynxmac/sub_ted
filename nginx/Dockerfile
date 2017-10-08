FROM nginx


COPY ./sites-enabled/ /etc/nginx/conf.d/

ENV DJANGO_HOST django
ENV DJANGO_PORT 8000

CMD envsubst < /etc/nginx/conf.d/default > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'