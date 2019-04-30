import sys
import os
from os.path import dirname
sys.path.extend([x[0] for x in os.walk(dirname(dirname(__file__)))])

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile

from map.models import Event
import json
from django.views.decorators.csrf import csrf_exempt
import base64


# Create your views here.

def index(request):
    return render(request, 'map/map_base.html')


# On document ready, get the nearby events.
#
# Required:
#     request: {'this_position'}
@csrf_exempt
def nearby(request):
    # Get location. 
    if request.is_ajax():
        if request.method == 'POST':
            position = json.loads(request.body).get('this_position')
    else: 
        position = {'lng':104.0668,'lat':30.5728} # Default: TODO: this is chengdu position
    
    # Get nearby events.
    lng, lat = position['lng'], position['lat']
    low_lng, high_lng, low_lat, high_lat = get_position_range(lng, lat)
    nearbys = get_nearby_events(Event, low_lng, high_lng, low_lat, high_lat)
    
    # Format nearby events. Send JSON. 
    # If empty nearbys, return an empty json array.
    response = [format_event(nearby) for nearby in nearbys]
    response = json.dumps(response)

    return HttpResponse(response)

# On event adding request, add the event.
#
# Required:
#     request: {'event'}
#     large request maximum size:
#       https://stackoverflow.com/questions/41408359/requestdatatoobig-request-body-exceeded-settings-data-upload-max-memory-size
@csrf_exempt
def upload(request):
    response = {}
    if request.is_ajax():
        if request.method == 'POST':
            event = json.loads(request.body).get('event')
            response['status'] = '0'
    else: 
        response['status'] = '1'
        response = json.dumps(response)
        return HttpResponse(response)
    
    # If request valid, add the event
    add_event(Event, event)

    response = json.dumps(response)
    return HttpResponse(response)
    

# Compute a range for "nearby" events. TODO: range
RANGE = 0.1  # Approximately half of a central city.
RADIUS = RANGE / 2
def get_position_range(lng, lat):
    return lng - RADIUS, lng + RADIUS, lat - RADIUS, lat + RADIUS


# Given an event object, return the dict format (ready for JSON)
def format_event(event):
    return \
    {
        'id': str(event.id),
        'lng': str(event.lng),  # json needs utf-8
        'lat': str(event.lat),  
        'summary': event.summary,
        'content': event.content,
        'name': event.name,
        # base64: https://stackoverflow.com/questions/3715493/encoding-an-image-file-with-base64
        'imagebase64': base64.b64encode(event.image.read()).decode('utf-8'),  # json needs utf-8
    }


# Given a range and DB, return the nearby events
def get_nearby_events(db, low_lng, high_lng, low_lat, high_lat):
    return db.objects.filter(lng__range=(low_lng, high_lng)).filter(lat__range=(low_lat, high_lat))  # Get nearby


def add_event(db,event):
    image_type = event['imagebase64_and_type']['type']
    new_event = db(
        name = event['name'],
        image = SimpleUploadedFile(
            name=event['name']+'.'+image_type,
            content=base64.b64decode(event['imagebase64_and_type']['imagebase64']), 
            content_type='image/'+image_type),
        summary = event['summary'],
        content = event['content'],
        lng = event['lng'],
        lat = event['lat']
    )
    new_event.save()

