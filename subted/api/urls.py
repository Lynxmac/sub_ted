#-*-coding:utf-8-*-

from django.conf.urls import url

from .views import (
    talk_transcripts,
    search_box,
    download_transcript
    )

urlpatterns = [
    url(r'^transcript/(?P<talk_id>[\d-]+)$', talk_transcripts, name='transcript'),
    url(r'^download/transcript/(?P<talk_id>[\d-]+)/(?P<file_type>[\w-]+)/$', download_transcript, name='download_transcripts'),
    url(r'^search/$', search_box, name='search'),
]