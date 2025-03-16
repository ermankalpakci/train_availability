from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
from PyQt5.QtCore import pyqtSignal, QObject


@dataclass
class SearchResult:
    message: str
    success: bool

class TrainSearch(QObject):

    status_changed = pyqtSignal(str)
    result_found = pyqtSignal(object) 

    def __init__(self, departure: str, arrival: str, date: str,number_of_passengers: int,
                time_flag: bool, start_time: str, end_time: str, options: List[bool],
                email: str=None, password: str=None, last_tried: str=None,
                _result: str=None, _paused: bool=False, id: int = None,
                departure_id: int = None, arrival_id: int = None):
        
        super().__init__()
        self.id = id
        self.departure = self.validate_location(departure, "Departure")
        self.arrival = self.validate_location(arrival, "Arrival")
        self.date = self.validate_date(date)
        self.number_of_passengers = self.validate_number_of_passengers(number_of_passengers)
        self.time_flag = time_flag
        self.options = options
        self.last_tried = last_tried
        self._result = _result
        self._paused = _paused
        self.departure_id = departure_id
        self.arrival_id = arrival_id


        if time_flag:
            self.start_time: Optional[datetime] = None
            self.end_time: Optional[datetime] = None
        else:
            self.start_time = start_time
            self.end_time = end_time

        if email is not None and password is not None:
            self.email = self.validate_email(email)
            self.password = password
        else:
            self.email = None
            self.password = None
        self.result: Optional[SearchResult] = None


    @property
    def paused(self):
        return self._paused

    @paused.setter
    def paused(self, value):
        self._paused = value
        self.status_changed.emit("paused" if value else "running")

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result: SearchResult):
        self._result = result
        if hasattr(result, "success"):
            if result.success:
                self.result_found.emit(result)
                self.status_changed.emit("completed")
            else:
                self.result_found.emit(result)
                self.status_changed.emit("failed")
        


    @staticmethod
    def validate_location(location: str, field_name: str) -> str:
        if not isinstance(location, str) or not location.strip():
            raise ValueError(f"{field_name} must be a non-empty string.")
        return location.strip()

    @staticmethod
    def validate_date(date: str) -> datetime:
        try:
            return datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format.")

    @staticmethod
    def validate_time(time: str) -> datetime:
        try:
            return datetime.strptime(time, "%H:%M").time()
        except ValueError:
            raise ValueError("Time must be in HH:MM format.")

    @staticmethod
    def validate_number_of_passengers(number_of_passengers: int) -> int:
        if not isinstance(number_of_passengers, int) or number_of_passengers <= 0:
            raise ValueError("Number of passengers must be a positive integer.")
        return number_of_passengers

    @staticmethod
    def validate_email(email: str) -> str:
        if email is not None:
            if not isinstance(email, str) or "@" not in email or "." not in email:
                raise ValueError("Invalid email format.")
            return email.strip()
