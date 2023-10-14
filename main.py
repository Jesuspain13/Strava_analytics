import requests
import yaml
from datetime import datetime, timedelta
from exceptions import NotControlledException
import time
import os

def load_yaml_config():
    print("Loading config file parameters...")
    config_filename = 'config_local.yml' if os.path.exists('./config_local.yml') else 'config.yml'
    with open(config_filename, 'r') as file:
        config: dict = yaml.safe_load(file)
    return config

def write_yaml_to_file(yaml_dict,filename='config_local.yml'):
    with open(f'{filename}', 'w',) as f :
        yaml.dump(yaml_dict,f,sort_keys=False) 
    print(f'Written to file {filename} OK')

def request():
    from strava_requests import StravaAthleteAuthentication, StravaAthleteActivities
    
    config = load_yaml_config()
    
    #Paste it in browser and copy code parameter
    #https://www.strava.com/oauth/mobile/authorize?client_id=41888&redirect_uri=https://localhost:8080&response_type=code&approval_prompt=auto&scope=activity:read
    CLIENT_ID = config['client_id']
    CLIENT_SECRET = config['client_secret']
    JESUS_ATHLETE_CODE = config['jesus_athlete_code']
    CORA_ATHLETE_CODE = config['cora_athlete_code']
    
    strava_athlete_auth = None
    try:
        tokens = {
            'refresh_token': config['refresh_token'],
            'access_token': config['access_token'],
        }
        strava_athlete_auth = StravaAthleteAuthentication(CLIENT_ID, CLIENT_SECRET, JESUS_ATHLETE_CODE, tokens)
        strava_activities = StravaAthleteActivities(strava_auth=strava_athlete_auth)
        activities = strava_activities.get_activities_from_range() # GET LAST WEEK TRAININGS
        
        print(activities)
    except NotControlledException as e:
        print("Strava consumer process: KO")
        print(e)
    finally:
        if strava_athlete_auth:
            print("Saving tokens in yaml...")
            config['refresh_token'] = strava_athlete_auth.get_refresh_token()
            config['access_token'] = strava_athlete_auth.get_bearer_token()
            write_yaml_to_file(yaml_dict=config)
        
if __name__ == '__main__':
    request()