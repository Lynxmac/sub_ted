from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from ted_apis import  (
    API_KEY,
    TALK_BASE_URL,
    new_talk_info_api,
    talk_info_api,
    transcript_api,
    search_talks_api,
    talk_vtt_api
)
from subted.settings import HEADERS
import re
import json
import codecs
import random
import requests
from urlparse import urlparse
from core.parse_talk_transcripts import talk_transcripts_to_text
from core.parse_talk_subtitle import process_two_vtt_to_one

with open('./data/support_language_now.json', 'rb') as f:
    r = f.read()
    support_languages_now = json.loads(r)


def talk_transcripts(request, talk_id):
    langs = request.GET.getlist('lang')
    check_request_languages(langs)
    if len(langs) == 1:
        lang_code = langs[0]
        if lang_code in support_languages_now:
            transcript_1 = talk_transcripts_to_text(talk_id, lang_code)
            return JsonResponse({"transcripts": {lang_code: transcript_1}})
    if len(langs) == 2:
        transcripts = talk_transcripts_to_text(talk_id, langs[0], langs[1])
        return JsonResponse({"transcripts": transcripts})
    # print HttpResponselanguages


def download_transcript(request, talk_id, file_type):
    print file_type, talk_id
    support_file_type = ['srt', 'txt', 'vtt']
    langs = request.GET.getlist('lang')
    check_request_languages(langs)
    if file_type not in support_file_type:
        return JsonResponse({"error": "Not a supported file type!"})
    slug = get_talk_slug(talk_id)
    if len(langs) == 1:
        if file_type == 'txt':
            result = talk_transcripts_to_text(talk_id,langs[0])
            transcript_1 = '\n\n'.join(result)
        else:
            r = requests.get(talk_vtt_api.format(
                talk_id=talk_id,
                language_code=langs[0]
            ))
            vtt = r.text
            if file_type == 'srt':
                transcript_1 = '\n\n'.join(vtt.split('\n\n')[1:])
            else:
                transcript_1 = vtt
        file_path = "/download/{file_type}/{slug}_{lang_code}.{file_type}".format(
            file_type=file_type,
            slug=slug,
            lang_code=langs[0]
        )
        with codecs.open("." + file_path, 'wb', 'utf-8') as f:
            f.write(transcript_1)
        with codecs.open("." + file_path, 'rb', 'utf-8') as f:
            return HttpResponse(f, content_type="text/{file_type}".format(file_type=file_type))
    if len(langs) == 2:
        file_path = "/download/{file_type}/{slug}_{lang_code_1}_{lang_code_2}.{file_type}".format(
            file_type=file_type,
            slug=slug,
            lang_code_1=langs[0],
            lang_code_2=langs[1]
        )
        if file_type == 'txt':
            transcripts = talk_transcripts_to_text(talk_id, langs[0], langs[1])
            zip_list = []
            for idx, val in enumerate(transcripts[langs[0]]):
                zip_list.append(val + "\n" + transcripts[langs[1]][idx])
            with codecs.open("." + file_path, 'wb', 'utf-8') as f:
                f.write("\n\n".join(zip_list))
        else:
            vtt_1 = requests.get(talk_vtt_api.format(
                talk_id=talk_id,
                language_code=langs[0]
            )).text
            vtt_2 = requests.get(talk_vtt_api.format(
                talk_id=talk_id,
                language_code=langs[1]
            )).text
            process_two_vtt_to_one(vtt_1, vtt_2, '.' + file_path, file_type)

        with codecs.open("." + file_path, 'rb', 'utf-8') as f:
            return HttpResponse(f, content_type="text/{file_type}".format(file_type=file_type))


def search_box(request):
    q_string = request.GET['q']
    try:
        limit = request.GET['limit']
        limit = int(limit)
    except:
        limit = 5
    if re.match(r'[htps]+://[^\s]*', q_string):
        response = parse_slug_or_url(url=q_string, limit=limit)
    else:
        response = parse_slug_or_url(keywords=q_string, limit=limit)
    ret = {"result": response}
    return JsonResponse(ret, safe=False)


def parse_slug_or_url(keywords=None, url=None, limit=None):
    if url:
        p = urlparse(url)
        path = p.path
        path_list = path.split('/')
        for d in path_list:
            if "_" in d:
                keywords = '%20'.join(d.split('_'))
                break

    if keywords:
        keywords = '%20'.join(keywords.split('_'))
        res = requests.get(search_talks_api.format(keywords=keywords,
                                             key=random.choice(API_KEY)),
                           headers=HEADERS)

        r_json = res.json()
        ret_data_with_image_url = []
        if r_json['results']:
            count = 0
            for result in r_json['results']:
                extract_dict = get_talks_info(result['talk']['id'])
                if not extract_dict:
                    continue
                extract_dict.update(result['talk'])
                extract_dict['talk_url'] = TALK_BASE_URL.format(slug=extract_dict['slug'])
                ret_data_with_image_url.append(extract_dict)
                count += 1
                if count == limit:
                    break
        return ret_data_with_image_url


def get_talk_slug(talk_id):
    r = requests.get(talk_info_api.format(key=random.choice(API_KEY),
                                          talk_id=talk_id),
                     headers=HEADERS)
    r_json = r.json()
    talk_info = r_json['talk']
    return talk_info['slug']


def check_request_languages(langs):
    if len(langs) == 0 or len(langs) > 2:
        return JsonResponse({'error': "Languages must be less than 3 languages and more than 0!"})


def get_api_info(api_url, retry_times=3):
    for i in xrange(retry_times):
        r = requests.get(api_url,
                         headers=HEADERS)
        r_json = r.json()
        print r_json.keys()
        if 'error' in r_json:
            continue
        else:
            return r_json
    return r_json


def get_talks_info(talk_id):
    talk_info_url =  talk_info_api.format(key=random.choice(API_KEY),
                         talk_id=talk_id)
    r_json = get_api_info(talk_info_url)
    if "error" in r_json:
        return
    talk_info = r_json['talk']
    languages = {}
    for k in talk_info['languages']:
        language = support_languages_now.get(k)
        if not language:
            name = orig_name = talk_info['languages'][k]['name']
            language = {'name': name, 'orig_name': orig_name}
        languages[k] = language
    # print talk_info
    extract_dict = dict(description=talk_info['description'],
                        id=talk_info['id'],
                        event=talk_info['event'],
                        images=talk_info['images'],
                        languages=languages,
                        media=[{"288P": talk_info['media']['internal']['320k']},
                               {'360P': talk_info['media']['internal']['600k']},
                               {'480P': talk_info['media']['internal']['950k']},
                               {'720P': talk_info['media']['internal']['950k']}],
                        name=talk_info['name'],
                        published_at=talk_info['published_at'],
                        updated_at=talk_info['updated_at'],
                        slug=talk_info['slug'],
                        speakers=talk_info['speakers'],
                        viewed_count=talk_info['viewed_count']
                        )
    extract_dict['media'][3]['720P']['uri'] = extract_dict['media'][3]['720P']['uri'].replace('950k.', '1500k.')
    extract_dict['media'][3]['720P']['filesize_bytes'] = extract_dict['media'][3]['720P']['filesize_bytes'] * (1500 / 950)
    extract_dict['transcripts_count'] = len(extract_dict['languages'])
    extract_dict['talk_url'] = TALK_BASE_URL.format(slug=extract_dict['slug'])
    return extract_dict


if __name__ == '__main__':
    pass
    # lang_code_1, lang_code_2 = 'zh-cn', 'zh-cn'
    # ret = talk_transcripts_to_text(1821, lang_code_1, lang_code_2)
    # print len(ret[lang_code_1]), len(ret[lang_code_2])
    # # print ret['en']
    # # ret['ja']
    # for idx, p in enumerate(ret[lang_code_1]):
    #     print p, '\n', ret[lang_code_2][idx]