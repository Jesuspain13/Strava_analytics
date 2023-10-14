import requests
from abc import abstractmethod
from exceptions import TokenExpiredException, NotControlledException
from datetime import datetime, timedelta
import time

class ApiConsumer():
    def __init__(self, url):
        self.url = url
        
    @abstractmethod
    def process_response(self, request_token_response, operation: str):
        pass
        

class StravaAthleteAuthentication(ApiConsumer):
    
    def __init__(self, client_id, client_secret, athlete_code, tokens):
        super().__init__(url="https://www.strava.com/api/v3/oauth/token")
        self.token_request_body: dict = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code"
        } 
        self.athlete_code = athlete_code
        self._access_token = tokens['access_token']
        self._refresh_token = tokens['refresh_token']
        if not self._access_token:
            self._get_new_athlete_bearer_token()
        else:
            print("Bearer token from yaml")
        
    def get_bearer_token(self):
        return self._access_token
    
    def get_refresh_token(self):
        return self._refresh_token
    
    def process_response(self, request_token_response, operation: str):
        if request_token_response.status_code == 200:
            print(f"{operation} bearer token: OK...")
            token_response = request_token_response.json()
            self._refresh_token = token_response['refresh_token']
            self._access_token = token_response['access_token']
        else:
            print(f"{operation} bearer token: KO...")
            raise NotControlledException(request_token_response.text)
        

    def _get_new_athlete_bearer_token(self):
        print("Getting new access token from API...")
        new_token_request_body = self.token_request_body.copy()
        new_token_request_body["code"] = self.athlete_code

        response = requests.post(self.url, data=new_token_request_body)
        self.process_response(response, operation="Getting new")
        
        
    def refresh_athlete_bearer_token(self):
        print("Refreshing access token...")
        new_token_request_body = self.token_request_body.copy()
        new_token_request_body["refresh_token"] = self.refresh_token

        response = requests.post(self.url, data=new_token_request_body)
        self.process_response(response, operation="Refreshing")


class StravaAthleteActivities(ApiConsumer):
    def __init__(self, strava_auth: StravaAthleteAuthentication):
        # 20 trainings per week by default
        super().__init__(url="""
            https://www.strava.com/api/v3/activities?before={date_end}&after={date_start}&page=1&per_page=20
        """)
        self.strava_auth = strava_auth

        
    def process_response(self, actvity_req_response, operation: str):
        status_code = actvity_req_response.status_code
        response_body = actvity_req_response.json()

        if status_code == 200:
            return response_body
        else:
            error = response_body[0]
            if status_code == 401 and (error['field'] == 'access_token' and error['code'] == 'invalid'):
                print(f"{operation}: KO because of token...")
                raise TokenExpiredException("Access token expired", actvity_req_response.text)
            else:
                print(f"{operation}: KO...")
                raise NotControlledException(actvity_req_response.text)
        
    
    def get_activities_from_range(self, date_until=datetime.now(), time_range_in_days: int=7, is_retry= False):
        """
            Returns request response as dictionary
            
            Exceptions
        """
        print("Gettings activities...")
        dt_until = datetime.now() if not date_until else date_until
        dt_from = dt_until - timedelta(days=time_range_in_days)
        url = self.url.format(date_end=time.mktime(dt_until.timetuple()), 
                              date_start=time.mktime(dt_from.timetuple()))
        try:
            headers = {'Authorization': f'Bearer {self.strava_auth.get_bearer_token()}'}
            
            response = requests.get(url, headers=headers)
            response_body = self.process_response(response, "Getting activities")
            print("Gettings activities OK...")
        except TokenExpiredException as e:
            print("Launching request again refreshing token...")
            if not is_retry:
                self.strava_auth.refresh_athlete_bearer_token()
                response_body = self.get_activities_from_range(date_until, time_range_in_days, is_retry=True)
        except NotControlledException as e:
            raise e
        
        return response_body