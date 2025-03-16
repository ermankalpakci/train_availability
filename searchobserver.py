from datetime import datetime, timedelta
import threading
import time
from api_request import TrainAPI
from user import TrainSearch
from filter_api_response import extractTrainDetails, availability_decider
from user import SearchResult
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtCore import pyqtSignal, QObject, QMutex, QMutexLocker
from concurrent.futures import ThreadPoolExecutor

class NotificationError(Exception):
    pass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    timeout: int = 30

class EmailSendError(Exception):
    pass



class TrainSearchObserver(QObject):
    _instance = None
    _lock = threading.Lock()
    _qt_lock = QMutex()


    search_started = pyqtSignal(object)  # TrainSearch
    search_completed = pyqtSignal(object, object)  # TrainSearch, SearchResult
    error_occurred = pyqtSignal(object, object)
    search_last_tried = pyqtSignal(object,str)

    def __new__(cls, auth_header: str):
        with cls._lock:
            if cls._instance is None:
                # Create instance and initialize QObject once
                cls._instance = super().__new__(cls)
                super(TrainSearchObserver, cls._instance).__init__()
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, auth_header: str):
        # Prevent reinitialization
        if self._initialized:
            return
            
        self._initialized = True
        self.auth_header = auth_header
        self.searches = []
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._running = True


    def add_search(self, search: TrainSearch):
        with QMutexLocker(self._qt_lock):
            self.searches.append(search)
            
        future = self.executor.submit(self._process_search, search)

        future.add_done_callback(
            lambda f: self._handle_completion(search, f)
        )
        self.search_started.emit(search)


    def _process_search(self, search: TrainSearch):
        try:
            while not search.paused and self._running and search in self.searches:
                with QMutexLocker(self._qt_lock):

                    api = TrainAPI(
                        unit_id="3895",
                        auth_token=self.auth_header,
                        timeout=30  # Add timeout
                    )
                    search.last_tried = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    self.search_last_tried.emit(search, search.last_tried)
                    response = api.search_availability(search)
                    extracted_details = extractTrainDetails(response)
                    result = availability_decider(search, extracted_details)
                    if result:
                        search.paused = True
                        search.result = SearchResult(
                            message=self.format_train_results(result),
                            success=True)
                        return search.result
                    
                    time.sleep(30)
        except Exception as e:
            search.result = SearchResult(message=f"Error: {str(e)}", success=False)
            return search.result



    def _handle_completion(self, search, future):
        try:
            result = future.result()
            with QMutexLocker(self._qt_lock):
                if search in self.searches:
                    self.searches.remove(search)
                    # search.paused = False                    
                if result.success:
                    self.search_completed.emit(search, result)
                    if search.email is not None and search.password is not None:
                        self.send_email(search)
                else:
                    self.error_occurred.emit(search, result)

        except Exception as e:
            search.result = SearchResult(message=f"Error: {str(e)}", success=False)
            self.error_occurred.emit(search, future)

    def shutdown(self):
        with QMutexLocker(self._qt_lock):
            self._running = False
        self.executor.shutdown(wait=True) 
        
    @classmethod
    def reset_instance(cls):
        with cls._lock:
            if cls._instance:
                cls._instance.shutdown()
                cls._instance = None

    def send_email(self, search: TrainSearch, test: bool = False) -> None:
        config = EmailConfig()
        
        try:
            subject = "Train Availability Notification Test" if test else "Train Availability Notification"
            body = "This is a test email." if test else search.result.message

            message = MIMEMultipart()
            message["From"] = search.email
            message["To"] = search.email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))
            email = search.email
            password = search.password

            with smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=config.timeout) as server:
                server.starttls()
                server.login(email, password)
                server.sendmail(email, email, message.as_string())
                

        except smtplib.SMTPAuthenticationError as e:
            search.result = SearchResult(message=f"Error: {str(e)}", success=True)
            self.error_occurred.emit(search, search.result)
        except smtplib.SMTPConnectError as e:
            search.result = SearchResult(message=f"Error: {str(e)}", success=True)
            self.error_occurred.emit(search, search.result)
        except smtplib.SMTPException as e:
            search.result = SearchResult(message=f"Error: {str(e)}", success=True)
            self.error_occurred.emit(search, search.result)
        except Exception as e:
            search.result = SearchResult(message=f"Error: {str(e)}", success=True)
            self.error_occurred.emit(search, search.result)

    def format_train_results(self, result):
        formatted = []
        for group in result:
            trains = group.get('trains', [])
            for i, train in enumerate(trains):
                departure = datetime.fromisoformat(train['departure_time'].replace('Z', '')) + timedelta(hours=3)
                formatted.append(
                    f"🚂 {train['commercial_name']} ({train['type']})\n"
                    f"⏰ Departure: {departure.strftime('%A, %B %d, %Y at %H:%M')}\n"
                )
                # Add cabin classes
                for cabin in train['cabin_classes']:
                    formatted.append(
                        f"• {cabin['name'].title()}: {cabin['availability_count']} seats available"
                    )
                if len(trains) > 1 and i < len(trains) - 1:
                    formatted.append("🔄 +++++Transfer+++++")
            formatted.append("\n")
            formatted.append("-------------------------\n")

        return "\n".join(formatted)