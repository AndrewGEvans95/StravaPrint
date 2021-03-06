# Use strava_auth.py to check if access token is still valid
# Import strava_auth.py
import strava_auth

import requests
import polyline
import matplotlib.pyplot as plt


# Retrieve polyline data from Strava API and return decoded polyline points
def get_polyline_data(access_token, page):
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {'per_page': '1', 'page': page}
    data = requests.get(activities_url, headers=headers, params=params).json()
    polyline_data = data[0]['map']['summary_polyline']
    polyline_data = polyline.decode(polyline_data)
    strava_activity_title = data[0]['name']
    strava_mileage = data[0]['distance']
    # Convert meters to miles
    strava_mileage = round(strava_mileage * 0.000621371, 2)
    return polyline_data, strava_activity_title, strava_mileage


# Plot polyline data using matplotlib
def plot_polyline(polyline_data, strava_activity_title, strava_mileage):
    activity_longitude = []
    activity_latitude = []
    for point in polyline_data:
        activity_longitude.append(point[0])
        activity_latitude.append(point[1])
   
    plt.plot(activity_longitude, activity_latitude, 'r-', alpha=1, linewidth=4)
    plt.axis('off')
    plt.title(strava_activity_title + ': '+ str(strava_mileage) + ' miles', fontsize=20, fontweight='bold', color='red')
    plt.savefig('map.png', bbox_inches='tight', bbox_extra_artists=[], transparent=True)
    #plt.show()
    plt.close()

def create_map_image(access_token, page):
    if not strava_auth.check_access_token():
        # If access token is not valid, use refresh token to generate new access token
        strava_auth.refresh_access_token()
    print("Retrieving polyline data from latest activity...")
    access_token = strava_auth.get_access_token_from_file()
    polyline_data, strava_activity_title, strava_mileage = get_polyline_data(access_token, 1)
    print('Polyline data retrieved')
    #print(polyline_data)
    
    plot_polyline(polyline_data, strava_activity_title, strava_mileage)