from dataclasses import dataclass
from typing import Dict, Optional
import requests
from user import TrainSearch

@dataclass
class TrainAPIError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TrainAPI:
    BASE_URL = "https://web-api-prod-ytp.tcddtasimacilik.gov.tr/tms/train/train-availability?environment=dev&userId=1"
    
    def __init__(self, auth_token: str, unit_id: str="3895", timeout: Optional[int] = None):
        self.headers = {
            'unit-id': unit_id,
            'Authorization': auth_token
        }
        self.timeout = timeout
    
    def search_availability(self, route: TrainSearch) -> Dict:
        url = self.BASE_URL
        
        payload = {
            "searchRoutes": [
                {
                    "departureStationId": route.departure_id,
                    "departureStationName": route.departure,
                    "arrivalStationId": route.arrival_id,
                    "arrivalStationName": route.arrival,
                    "departureDate": route.date.strftime("%d-%m-%Y") + " 21:00:00"
                }
            ],
            "passengerTypeCounts": [
                {
                    "id": 0,
                    "count": route.number_of_passengers
                }
            ],
            "searchReservation": False
        }
        try:
            response = requests.post(url,
                                    json=payload,
                                    headers=self.headers,
                                    timeout=self.timeout)
            response.raise_for_status()
            response_data = response.json()

            return response_data
        except requests.exceptions.HTTPError as http_err:
            # Handle specific HTTP errors here.
            raise TrainAPIError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.RequestException as req_err:
            # This catches all other requests-related errors.
            raise TrainAPIError(f"Request error occurred: {req_err}") from req_err
        except Exception as e:
            # Catch any other exceptions.
            raise TrainAPIError(f"An unexpected error occurred: {e}") from e