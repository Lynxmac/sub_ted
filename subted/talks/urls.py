#-*-coding:utf-8-*-

from django.conf.urls import url

from .views import (
    random_talk,
    talk_page
    )

urlpatterns = [
    url(r'^$', random_talk, name='random_talk'),
    url(r'^(?P<talk_id>[\d-]+)/(?P<slug>[\w-]+)$', talk_page, name='talk_page'),
]