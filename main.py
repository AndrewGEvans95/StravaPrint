# Retrieve map data from Strava API and create an image of the map

import requests
import json
import folium
import polyline
import numpy as np
import pandas as pd
from IPython.display import display
import imgkit as imgkit
import configparser

# Read config file and get client id and client secret
config = configparser.ConfigParser()
config.read('strava_api_config.ini')
client_id = config['STRAVA']['client_id']
client_secret = config['STRAVA']['client_secret']

refresh_token = ''
# Need to retrieve auth code from Strava API manually (see comment below)
auth_code = ''
scope = 'activity:read_all'

access_token = ''

# Manually access auth code from Strava API
# https://www.strava.com/oauth/authorize?client_id=37207&redirect_uri=http://localhost&response_type=code&scope=activity:read_all

# Get new access token from Strava API
def get_access_token(client_id, client_secret, refresh_token):
    url = 'https://www.strava.com/oauth/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
    }
    response = requests.post(url, params)
    return response.json()['access_token']

def get_map_data(access_token, page):
    print(access_token)
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {'per_page': '200', 'page': 1}

    data = requests.get(activities_url, headers=headers, params=params).json()
    return data

#print('Retrieving access token...')
#access_token = get_access_token(client_id, client_secret, refresh_token)
print('Access token retrieved: ' + access_token)
map_data = get_map_data(access_token, 1)
print('Map data retrieved')
print(map_data)

summary_polyline_list = []

# Create list of all polylines
for activity in map_data:
    if activity['map']['summary_polyline']:
        summary_polyline_list.append(polyline.decode(activity['map']['summary_polyline']))

# Retrieve summary_polyline from map_data
summary_polyline = map_data[0]['map']['summary_polyline']
print('Summary polyline retrieved')
print(summary_polyline)

# Decode summary_polyline to get list of lat/long coordinates
polyline_coords = polyline.decode(summary_polyline)

# plot ride on map
centroid = [
    np.mean([coord[0] for coord in polyline_coords]), 
    np.mean([coord[1] for coord in polyline_coords])
]

print(centroid)

m = folium.Map(location=centroid, tiles="Stamen Toner", zoom_start=15)

folium.PolyLine(polyline_coords, color='red').add_to(m)

# Add all polylines to map
for polyline in summary_polyline_list:
    folium.PolyLine(polyline, color='blue').add_to(m)

# Display map
m.save('map.html')


display(m)