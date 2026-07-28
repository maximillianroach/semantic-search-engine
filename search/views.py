from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests

import os
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:5001")

# Create your views here.
def page(request):
    return render(request, "search/page.html")

def search(request):
    # extract the data from query
    query = request.GET.get("query", "")
    style = request.GET.get("style")
    genre = request.GET.get("genre")
    artist = request.GET.get("artist")
    mode = request.GET.get("mode")

    # get the response from fastapi server
    resp = requests.post(url=f"{FASTAPI_URL}/search", 
                         json={"query": query, "style": style, "genre": genre, "artist": artist, "mode": mode})

    # convert response to json
    resp = resp.json()

    # return json to browser
    return JsonResponse(resp)

def styles(request):
    resp = requests.get(url=f"{FASTAPI_URL}/styles")
    return JsonResponse(resp.json(), safe=False)

def genres(request):
    resp = requests.get(url=f"{FASTAPI_URL}/genres")
    return JsonResponse(resp.json(), safe=False)

def artists(request):
    resp =  requests.get(url=f"{FASTAPI_URL}/artists")
    return JsonResponse(resp.json(), safe=False)


    


