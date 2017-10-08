# -*- coding:utf-8 -*-

# Retrieve talk info such as speaker, description, image, etc
new_talk_info_api = 'https://www.ted.com/services/v1/oembed.json?url={talk_url}'
search_talks_api = 'http://api.ted.com/v1/search.json?q={keywords}&categories=talks&api-key={key}'
transcript_api = 'https://www.ted.com/talks/{talk_id}/transcript.json?language={language_code}'
talk_info_api = "http://api.ted.com/v1/talks/{talk_id}.json?external=false&podcasts=true&api-key={key}"
talk_vtt_api = 'https://hls.ted.com/talks/{talk_id}/subtitles/{language_code}/full.vtt'

TALK_BASE_URL = "https://www.ted.com/talks/{slug}"
API_KEY = ['2a9uggd876y5qua7ydghfzrq',
           'r7b7vtktewzmjs29dwuvvrtk',
           'hzjevu53hy7rggd7w7rnuegf',
           'thbn678cjn86b5jtunacgque',
           "xbsdfg4uhxf6prsp8c7adrty"]