# Python module to authenticate with Strava and get an access token
import requests
import configparser

# Read config file and get client id and client secret
config = configparser.ConfigParser()
config.read('strava_api_config.ini')
client_id = config['STRAVA']['client_id']
client_secret = config['STRAVA']['client_secret']

# Step 1: Check if access token is valid
# Step 2: Refresh expired access token
# Step 3: Write access token to file
client_id = client_id
client_secret = client_secret

def generate_auth_link():
    redirect_uri = 'http://localhost'
    scope = 'activity:read_all'
    auth_link = 'https://www.strava.com/oauth/authorize?client_id=' + client_id + '&redirect_uri=' + redirect_uri + '&response_type=code&scope=' + scope
    return auth_link

# Retrieve access token from local file
def get_access_token_from_file():
    access_token = ''
    try:
        with open('access_token.txt', 'r') as f:
            access_token = f.read()
    except:
        # Create access_token file
        with open('access_token.txt', 'w') as f:
            f.write('')
    return access_token

def write_access_token_to_file(access_token):
    with open('access_token.txt', 'w') as f:
        f.write(access_token)

# Retrieve refresh token from local file
def get_refresh_token_from_file():
    refresh_token = ''
    try:
        with open('refresh_token.txt', 'r') as f:
            refresh_token = f.read()
    except:
        # Create refresh_token file
        with open('refresh_token.txt', 'w') as f:
            f.write('')
    return refresh_token

def write_refresh_token_to_file(refresh_token):
    with open('refresh_token.txt', 'w') as f:
        f.write(refresh_token)

auth_link = generate_auth_link()
#print('Please visit the following link to authenticate with Strava:')
#print(auth_link)

# Use authorization code to get access token and refresh token
# OAuth takes 4 params: client_id, client_secret, code, grant_type
# grant_type = authorization_code
# code = authorization code
# client_id = client id
# client_secret = client secret
def get_access_token_and_refresh_token(client_id, client_secret, auth_code):
    url = 'https://www.strava.com/api/v3/oauth/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': auth_code,
        'grant_type': 'authorization_code',
    }
    response = requests.post(url, params)
    print(response.json())
    # Write access token to file
    write_access_token_to_file(response.json()['access_token'])
    # Write refresh token to file
    write_refresh_token_to_file(response.json()['refresh_token'])
    return response.json()

# Use OAuth refresh token to create new access token
def refresh_access_token():
    refresh_token = get_refresh_token_from_file()
    url = 'https://www.strava.com/api/v3/oauth/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }
    response = requests.post(url, params)
    # Write access token to file
    write_access_token_to_file(response.json()['access_token'])
    # Write refresh token to file
    # As per the Strava API, refresh tokens may change when new access token is generated
    write_refresh_token_to_file(response.json()['refresh_token'])
    return response.json()

# Check if refresh token exists
def check_refresh_token():
    refresh_token = get_refresh_token_from_file()
    if refresh_token == '':
        return False
    else:
        return True

# Check if access token is still valid
def check_access_token():
    access_token = get_access_token_from_file()
    url = 'https://www.strava.com/api/v3/athlete'
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False

if not check_refresh_token():
    get_access_token_and_refresh_token(client_id, client_secret, auth_code)
else:
    # check if access token is valid
    if check_access_token():
        print('Strava access token is still valid')
    else:
        # refresh access token
        refresh_token = get_refresh_token_from_file()
        refresh_access_token()
        # check if access token is valid and if not then refresh token did not work
        # user may need to re-authenticate
        if not check_access_token():
            print('Failed to refresh access token')
            print('Please re-authenticate: ')
            print(generate_auth_link())

