#-*- coding:utf-8 -*-

import requests

from api.ted_apis import  (
    transcript_api,
    talk_vtt_api
)
from subted.settings import HEADERS
from parse_talk_subtitle import  process_two_vtt_to_one

ends = (',', '.', '"', "?", "-", "!", "、",
            ";", ")", ">", "_", "，", "？",
            "。", "！", "；", "》", "——", "…",
            "）", "）", "’", "：", "。", "；", "，", "；", "：")


def extrange_dict_key_value(dic, less, threhold=4):
    hit_count = 0
    for p,val in less.iteritems():
        for paragraph in val:
            for idx,text in enumerate(paragraph['cues']):
                if text['text'] in dic:
                    hit_count += 1
                    if hit_count > threhold:
                        return dic
    tmp = {}
    for k,v in dic.iteritems():
        tmp[v] = k
    dic = tmp
    del tmp
    return dic

def count_transcript_text(transcript_json):
    length = 0
    paragraph_length = 0
    for p,val in transcript_json.iteritems():
        for paragraph in val:
            paragraph_length += 1
            for idx,text in enumerate(paragraph['cues']):
                length += 1
    return length, paragraph_length

def extract_transcripts(json_1, json_2, vtt_pairs):

    length_1, paragraph_length_1 = count_transcript_text(json_1)
    length_2, paragraph_length_2 = count_transcript_text(json_2)
    print paragraph_length_1, paragraph_length_2
    extranged = False
#     print length_1, paragraph_length_1, length_2, paragraph_length_2, vtt_pairs, json_1, json_2
    if length_1 <= length_2 and paragraph_length_1 <= paragraph_length_2:
        less, more = json_1, json_2
    elif length_1 <= length_2 and paragraph_length_1 > paragraph_length_2:
        less, more = json_2, json_1
        vtt_pairs = extrange_dict_key_value(vtt_pairs, less)
        extranged = True
    elif length_1 > length_2 and paragraph_length_1 <= paragraph_length_2:
        less, more = json_1, json_2
    elif length_1 > length_2 and paragraph_length_1 > paragraph_length_2:
        less, more = json_2, json_1
        vtt_pairs = extrange_dict_key_value(vtt_pairs, less)
        extranged = True
    paragraphs_less = []
    paragraphs_more = []
#     print vtt_pairs
#   print less == more
    for p,val in less.iteritems():
        for paragraph in val:
            p_less_text = ''
            p_more_text = ''
            for idx,text in enumerate(paragraph['cues']):
                format_text = text['text'].replace('\n', '').replace('  ', ' ')
#                 print format_text
                if more:
                    for vtt, ptt in vtt_pairs.iteritems():
                        if format_text in vtt and ptt not in p_more_text:
                            if not ptt.encode("utf-8").endswith(ends):
                                p_more_text += ptt + ","
                            else:
                                p_more_text += ptt
                            break
                if not format_text.encode("utf-8").endswith(ends):
                    p_less_text += format_text + ","
                else:
                    p_less_text += format_text
            paragraphs_less.append(p_less_text)
            paragraphs_more.append(p_more_text)
    print extranged
    if extranged:
        return paragraphs_more, paragraphs_less
    return paragraphs_less, paragraphs_more


def talk_transcripts_to_text(talk_id, lang_code_1, lang_code_2=None):
    if lang_code_2 == None:
        transcript_1 = requests.get(transcript_api.format(talk_id=talk_id,
                                             language_code=lang_code_1),
                        headers=HEADERS)
        trans_json_1 = transcript_1.json()
        paragraphs = []
        for p,val in trans_json_1.iteritems():
            for paragraph in val:
                p_text = ''
                for idx,text in enumerate(paragraph['cues']):
                    format_text = text['text'].replace('\n', '').replace('  ', ' ')
                    if not format_text.encode("utf-8").endswith(ends):
                        p_text += format_text + ","
                    else:
                        p_text += format_text
                paragraphs.append(p_text)
        return paragraphs
    vtt_1 = requests.get(talk_vtt_api.format(talk_id=talk_id,
                                             language_code=lang_code_1),
                        headers=HEADERS).text
    vtt_2 = requests.get(talk_vtt_api.format(talk_id=talk_id,
                                             language_code=lang_code_2),
                        headers=HEADERS).text
    transcript_1 = requests.get(transcript_api.format(talk_id=talk_id,
                                             language_code=lang_code_1))
    trans_json_1 = transcript_1.json()
    transcript_2 = requests.get(transcript_api.format(talk_id=talk_id,
                                             language_code=lang_code_2))
    trans_json_2 = transcript_2.json()
    vet_pairs = process_two_vtt_to_one(vtt_1, vtt_2, file_type=None)
    trans_text_1, trans_text_2 = extract_transcripts(trans_json_1, trans_json_2, vet_pairs)
    return {lang_code_1: trans_text_1, lang_code_2: trans_text_2}


if __name__ == '__main__':
    pass