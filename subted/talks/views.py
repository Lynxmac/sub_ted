from django.shortcuts import render
from random import randint
# Create your views here.

from core.parse_talk_subtitle import process_two_vtt_files_to_one
from api.views import get_talks_info
from django.shortcuts import render,get_object_or_404, HttpResponseRedirect

def play_talks_video(request):
    return render(request, "talks.html")


def talk_page(request, talk_id=None, slug=None):
    result = {"talks": get_talks_info(talk_id)}
    return render(request, "talks.html", result)


def random_talk(request):
    result = None
    while not result:
        talk_id = randint(1,3000)
        result = get_talks_info(talk_id)
    url = "/talks/{talk_id}/{slug}".format(
        talk_id=result['id'],
        slug=result['slug'])
    return HttpResponseRedirect(url)