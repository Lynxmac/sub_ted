#-*-coding:utf-8-*-

from django.conf.urls import url

from .views import (
    index,
    search
    )

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^search/$', search, name='search'),
]