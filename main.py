import json
import os

import src.exceptions as exceptions
from src.strava_requests import StravaAthleteAuthentication, StravaAthleteActivities
import src.strava_processing as strava_svc
from src import utils
from src.mongodb_connection import MongoDBConnection


class StravaETL:

    def __init__(self):
        self.config_filename = './config_local.yml' if os.path.exists('./config_local.yml') else './config.yml'
        self.config = utils.load_yaml_config(filename=self.config_filename)
        self.strava_client_id = self.config['strava']['client_id']
        self.strava_client_secret = self.config['strava']['client_secret']

    def request_athlete_activities(self, athlete_name, athlete_data: dict) -> dict:
        strava_athlete_auth = None
        activities_processed = None
        try:
            print(f"Selected athlete is: {athlete_name}: {athlete_data}")
            tokens = athlete_data['tokens']
            strava_code_id = athlete_data['strava_code']
            # tokens = {
            #    'refresh_token': config['refresh_token'],
            #    'access_token': config['access_token'],
            # }
            strava_athlete_auth = StravaAthleteAuthentication(self.strava_client_id, self.strava_client_secret,
                                                              strava_code_id, tokens)
            strava_activities = StravaAthleteActivities(strava_auth=strava_athlete_auth)
            activities = strava_activities.get_activities_from_range()  # GET LAST WEEK TRAININGS
            activities_processed = strava_svc.process_activities(activities)
            return activities_processed
        except exceptions.NotControlledException as e:
            print("Strava consumer process: KO")
            print(e)
        finally:
            if strava_athlete_auth:
                print("Saving tokens in yaml...")
                self.config['athletes'][athlete_name]['tokens']['refresh_token'] = strava_athlete_auth.get_refresh_token()
                self.config['athletes'][athlete_name]['tokens']['access_token'] = strava_athlete_auth.get_bearer_token()

    def request(self, to_save_as_json=False, to_save_in_mongo=True):
        import os
        config_filename = './config_local.yml' if os.path.exists('./config_local.yml') else './config.yml'
        config = utils.load_yaml_config(filename=config_filename)

        # Paste it in browser and copy code parameter
        # https://www.strava.com/oauth/mobile/authorize?client_id=41888&redirect_uri=https://localhost:8080&response_type=code&approval_prompt=auto&scope=activity:read
        data = list()
        try:
            mongodb_connection = MongoDBConnection(config=config) if to_save_in_mongo else None
            print("Requesting activities for every athelete")
            for athlete_name, athlete_data in config['athletes'].items():
                activities_processed = self.request_athlete_activities(athlete_name, athlete_data)
                data.extend(activities_processed)
            if to_save_in_mongo and data:
                mongodb_connection.insert_data(data_dict=data)

            if to_save_as_json:
                utils.write_in_json(data)

        except exceptions.MongoDBConnectionException as e:
            print("Error creating Mongo DB client")
            print(e)
        except exceptions.MongoDBOperationException as e:
            print("Error during Mongo DB client")
            print(e)
        finally:
            utils.write_yaml_to_file(yaml_dict=self.config)


if __name__ == '__main__':
    StravaETL().request(False, True)
