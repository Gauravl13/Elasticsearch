from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import youtube_dl
from .forms import DownloadForm
import re
from .models import UserDocument
from elasticsearch import Elasticsearch
from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login,logout
import requests
from .utils import get_hotels


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Retrieve the user from Elasticsearch
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        search_body = {
            "query": {
                "match": {
                    "username": username
                }
            }
        }
        response = es.search(index='users', body=search_body)
        hits = response['hits']['hits']

        if len(hits) == 1:
            user = hits[0]['_source']
            if check_password(password, user['password']):
                # User is authenticated
                # Perform the necessary operations after successful login

                return redirect('home')

        # Invalid credentials
        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = make_password(request.POST['password'])

        user = User(username=username, password=password)
        user.save()

        # Index the user data in Elasticsearch
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        user_doc = UserDocument(username=user.username, password=user.password)
        user_doc.save(using=es)

        # Perform the necessary operations after successful registration
        return redirect('login')

    return render(request, 'register.html')

def download_video(request):
    global context
    form = DownloadForm(request.POST or None)

    if form.is_valid():
        video_url = form.cleaned_data.get("url")
        regex = r'^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+'
        # regex = (r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$\n")
        print(video_url)
        if not re.match(regex, video_url):
            print('nhi hoa')
            return HttpResponse('Enter correct url.')

        # if 'm.' in video_url:
        #     video_url = video_url.replace(u'm.', u'')

        # elif 'youtu.be' in video_url:
        #     video_id = video_url.split('/')[-1]
        #     video_url = 'https://www.youtube.com/watch?v=' + video_id

        # if len(video_url.split("=")[-1]) < 11:
        #     return HttpResponse('Enter correct url.')

        ydl_opts = {}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                video_url, download=False)
        video_audio_streams = []
        for m in meta['formats']:
            file_size = m['filesize']
            if file_size is not None:
                file_size = f'{round(int(file_size) / 1000000, 2)} mb'

            resolution = 'Audio'
            if m['height'] is not None:
                resolution = f"{m['height']}x{m['width']}"
            video_audio_streams.append({
                'resolution': resolution,
                'extension': m['ext'],
                'file_size': file_size,
                'video_url': m['url']
            })
        video_audio_streams = video_audio_streams[::-1]
        context = {
            'form': form,
            'title': meta['title'], 'streams': video_audio_streams,
            'description': meta['description'], 'likes': meta['like_count'],
            'dislikes': meta['dislike_count'], 'thumb': meta['thumbnails'][3]['url'],
            'duration': round(int(meta['duration']) / 60, 2), 'views': f'{int(meta["view_count"]):,}'
        }
        return render(request, 'home.html', context)
    return render(request, 'home.html', {'form': form})


def home(request):
    context = {}
    if request.method == 'POST':
        address = request.POST.get('address', '')
        context['address'] = address
        context['places'] = get_nearby_places(address)
        print(context)

    return render(request, 'index.html', context)


def get_nearby_places(address):
    places_url = "https://dev.virtualearth.net/REST/v1/Locations?addressLine=" + address + "&key=AnRNicGadpqWZhntIcPHtRyNh-RLVUlurcE2UYWnxTpHdWMaHCed9lbG0HulN5WR"
    response = requests.get(places_url,verify=False)
    data = response.json()
    print(data)
    if 'resourceSets' in data and len(data['resourceSets']) > 0:
        resource_set = data['resourceSets'][0]
        print('resource ***',resource_set)
        if 'resources' in resource_set and len(resource_set['resources']) > 0:
            resource = resource_set['resources'][0]
            if 'geocodePoints' in resource and len(resource['geocodePoints']) > 0:
                location = resource['geocodePoints'][0]['coordinates']
                latitude = location[0]
                longitude = location[1]
            else:
                # Handle the case when geocodePoints is empty
                latitude = None
                longitude = None
        else:
            # Handle the case when resources is empty
            latitude = None
            longitude = None
    else:
        # Handle the case when resourceSets is empty
        latitude = None
        longitude = None

    search_url = f"https://dev.virtualearth.net/REST/v1/LocalSearch/?query=hotels&userMapView={latitude},{longitude},15&key=AnRNicGadpqWZhntIcPHtRyNh-RLVUlurcE2UYWnxTpHdWMaHCed9lbG0HulN5WR"
    response = requests.get(search_url,verify=False)
    data = response.json()
    if 'resourceSets' in data and len(data['resourceSets']) > 0:
        resource_set = data['resourceSets'][0]
        if 'resources' in resource_set:
            places = resource_set['resources']
        else:
            # Handle the case when resources is missing or empty
            places = []
    else:
        # Handle the case when resourceSets is missing or empty
        places = []

    print('places are *******',places)



def display_map(request):
    return render(request, 'map.html')

def search_hotels(request):
    if request.method == "POST":
        location = request.POST.get("location", "")
        hotels = get_hotels(location)

        context = {
            "location": location,
            "hotels": hotels
        }
        print(context)
        return render(request, "hotels.html", context)

    return render(request, "search.html")