# -*- coding:utf-8 -*-

import codecs

# translate '00:00:12.544' like string into integer
def strtime_to_int(strtime):
    hours, minutes, seconds_milesec = strtime.split(':')
    seconds, milesecs = seconds_milesec.split('.')
    return int(hours) * (3600 * 1000) + int(minutes) * (60 * 1000) + int(seconds) * 1000 + int(milesecs)


# Break down the "00:04:56.659 --> 00:04:58.675 if I give you something that belongs to me"
# like text into start_time, end_time, start_time_int, end_time_int, text.
def process_text_to_int_and_text(string_time):
    time_text_split = string_time.split('\n')
    time_stamp = time_text_split[0]
    text = ' '.join(time_text_split[1:]).replace('  ', ' ')
    start_time, end_time = time_stamp.split(' --> ')
    start_time_int = strtime_to_int(start_time)
    end_time_int = strtime_to_int(end_time)
    return start_time, end_time, start_time_int, end_time_int, text


# Check if last start_time_int or end_time_int compare result is fitted.
# If there's no fit translation, put it into latest compress_result.
def check_hit(hit_list):
    for i in hit_list:
        if i:
            return True
    return False


def compress_vtts(vtt_less, vtt_more):
    compress_results = []
    last_time_start_int_less = last_time_end_int_less = 0
    last_end_time_less = last_end_time_less = '00:00:00.000'
    last_time_text_less = ''
    next_start = 0
    last_time_hit = False
    hit_list = []
    for time_text_less in vtt_less:
        if last_time_start_int_less != 0:
            #             print hit_list, last_time_start_int_less
            if check_hit(hit_list) == False:
                compress_results[-1]['less']['text'] = (compress_results[-1]['less']['text']
                                                        + ' ' + last_time_text_less).replace('  ', ' ')
                compress_results[-1]['less']['end_time'] = last_end_time_less
                compress_results[-1]['less']['end_time_int'] = last_time_end_int_less
                #                 print compress_results[-1]['less']['text']
                #                 next_start -= 1
        hit_list = []
        #         print next_start
        start_time_less, \
        end_time_less, \
        start_time_int_less, \
        end_time_int_less, \
        text_less = process_text_to_int_and_text(time_text_less)
        #         print start_time_int_less, end_time_int_less, end_time_int_less - start_time_int_less, text_less
        meta_less = meta_more = {'start_time_int': start_time_int_less,
                                 'end_time_int': end_time_int_less,
                                 'start_time': start_time_less,
                                 'end_time': end_time_less,
                                 'text': text_less}
        for time_text_more in vtt_more[next_start:]:
            start_time_more, \
            end_time_more, \
            start_time_int_more, \
            end_time_int_more, \
            text_more = process_text_to_int_and_text(time_text_more)
            if next_start == 0:
                next_start += 1
                last_time_hit = True
                hit_list.append(last_time_hit)
                meta_more = {'start_time_int': start_time_int_more,
                             'end_time_int': end_time_int_more,
                             'start_time': start_time_more,
                             'end_time': end_time_more,
                             'text': text_more}
                compress_results.append({'less': meta_less, 'more': meta_more})
                # print text_more, text_less
                #                 print start_time_int_more, end_time_int_more ,end_time_int_more - start_time_int_more, text_more
                # break
            if start_time_int_more >= end_time_int_less or start_time_int_less >= end_time_int_more:
                #                 print '-->excluded', start_time_int_more, end_time_int_more ,end_time_int_more - start_time_int_more, text_more
                last_time_start_int_less = start_time_int_less
                last_time_end_int_less = end_time_int_less
                last_start_time_less = start_time_less
                last_end_time_less = end_time_less
                last_time_hit = False
                hit_list.append(last_time_hit)
                break
            # print start_time_int_more, end_time_int_more ,end_time_int_more - start_time_int_more, text_more
            if len(hit_list) >= 1:
                meta_more['end_time_int'] = end_time_int_more
                meta_more['start_time'] = start_time_more
                meta_more['end_time'] = end_time_more
                meta_more['text'] = (meta_more['text'] + ' ' + text_more).replace('  ', ' ')
            else:
                meta_more = {'start_time_int': start_time_int_more,
                             'end_time_int': end_time_int_more,
                             'start_time': start_time_more,
                             'end_time': end_time_more,
                             'text': text_more}
            last_time_hit = True
            hit_list.append(last_time_hit)
            if last_time_hit:
                next_start += 1
            compress_results.append({'less': meta_less, 'more': meta_more})

        last_time_text_less = text_less
    return compress_results


def process_two_vtt_to_one(vtt_raw_1, vtt_raw_2, dst_path=None, file_type='vtt'):
    vtt_list_1 = vtt_raw_1.split('\n\n')[1:]
    vtt_list_2 = vtt_raw_2.split('\n\n')[1:]
    extranged = False
    # compare the length of two vtt list
    if len(vtt_list_1) <= len(vtt_list_2):
        vtt_less, vtt_more = vtt_list_1, vtt_list_2
    else:

        vtt_less, vtt_more = vtt_list_2, vtt_list_1

    compressed_vtts = compress_vtts(vtt_less=vtt_less, vtt_more=vtt_more)
    #     print len(compressed_vtts)
    deduplication = []
    ret_pair = {}
    last_compare_time_start = last_compare_time_end = 0
    count = 1
    for i in compressed_vtts:
        start_time_int_less, end_time_int_less = i['less']['start_time_int'], i['less']['end_time_int']
        if start_time_int_less != last_compare_time_start and end_time_int_less != last_compare_time_end:
            less_time = ' --> '.join([i['less']['start_time'], i['less']['end_time']])
            more_time = ' --> '.join([i['more']['start_time'], i['more']['end_time']])
            less_text = i['less']['text']
            more_text = i['more']['text']
            #             print less_time, less_text
            #             print more_time, more_text, '\n'
            if file_type == 'vtt' or file_type == 'srt':
                deduplication.append(u'{count}\n{less_time}\n{more_time}\n{less_text}\n{more_text}'.format(
                    count=count,
                    less_time=less_time,
                    more_time=more_time,
                    less_text=less_text,
                    more_text=more_text))
            elif file_type == 'txt':
                deduplication.append(u'{count}\n{less_text}\n{more_text}'.format(
                    count=count,
                    less_time=less_time,
                    more_time=more_time,
                    less_text=less_text,
                    more_text=more_text))
            elif file_type == None:
                if less_text in ret_pair and len(ret_pair[less_text]) < more_text :
                    pass
                else:
                    ret_pair[less_text] = more_text
            count += 1
        last_compare_time_start, last_compare_time_end = start_time_int_less, end_time_int_less
    # print len(deduplication)
    if file_type is None:
        return ret_pair
    with codecs.open(dst_path, 'wb', 'utf-8') as f:
        if file_type == 'vtt':
            header = "WEBVTT"
            deduplication.insert(0, header)
            content = '\n\n'.join(deduplication)
        elif file_type == 'srt':
            content = '\n\n'.join(deduplication)
        elif file_type == 'txt':
            content = '\n\n'.join(deduplication)
        f.write(content)
    print "[INFO] New {file_type} file generated: {new_file}".format(file_type=file_type,
                                                                     new_file=dst_path.split('/')[-1])


def process_two_vtt_files_to_one(vtt_path_1, vtt_path_2, dst_path, file_type='vtt'):
    print "[INFO] Processing vtt files: {file_1}, {file_2}".format(file_1=vtt_path_1.split('/')[-1],
                                                                   file_2=vtt_path_2.split('/')[-1])
    with codecs.open(vtt_path_1, 'rb', 'utf-8') as f:
        vtt_raw_1 = f.read()
    with codecs.open(vtt_path_2, 'rb', 'utf-8') as f:
        vtt_raw_2 = f.read()
        # print len(deduplication)
    return process_two_vtt_to_one(vtt_raw_1, vtt_raw_2, dst_path, file_type)

if __name__ == '__main__':
    # vtt_path_1 = '../../tests/apollo_robbins_the_art_of_misdirection_en.vtt'
    # vtt_path_2 = '../../tests/apollo_robbins_the_art_of_misdirection_ru.vtt'
    import requests
    talk_vtt_api = 'https://hls.ted.com/talks/{talk_id}/subtitles/{language_code}/full.vtt'
    vtt_1 = requests.get(talk_vtt_api.format(talk_id=66,language_code='zh-cn')).text
    vtt_2 = requests.get(talk_vtt_api.format(talk_id=66, language_code='en')).text
    file_type = 'srt'
    vtt_dst = '../download/{file_type}/ken_robinson_says_schools_kill_creativity_en_zh-cn.{file_type}'.format(file_type=file_type)
    # process_two_vtt_files_to_one(vtt_path_1, vtt_path_2, vtt_dst, file_type='txt')
    process_two_vtt_to_one(vtt_1, vtt_2, vtt_dst, file_type='vtt')

