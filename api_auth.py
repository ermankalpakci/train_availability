from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from typing import Optional, List, Dict, Any
import json
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumDriverError(Exception):
    """Custom exception for SeleniumDriver errors."""
    pass

class SeleniumDriver:
    _instance: Optional['SeleniumDriver'] = None
    _driver: Optional[webdriver.Chrome] = None
    
    def __new__(cls) -> 'SeleniumDriver':
        if cls._instance is None:
            cls._instance = super(SeleniumDriver, cls).__new__(cls)
            cls._instance._initialize_driver()
        return cls._instance

    def _initialize_driver(self) -> None:
        try:
            options = Options()
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            options.add_argument("--headless=new")  # Enables headless mode
            options.add_argument("--disable-gpu")  # Optional: Helps on some systems
            options.add_argument("--no-sandbox")  # Optional: Avoids sandboxing issues
            options.add_argument("--disable-dev-shm-usage")  # Optional: Helps in Docker/Linux environments

            self._driver = webdriver.Chrome(options=options)
        except WebDriverException as e:
            raise SeleniumDriverError(f"Failed to initialize Chrome driver: {str(e)}")

    @property
    def driver(self) -> webdriver.Chrome:
        if self._driver is None:
            self._initialize_driver()
        return self._driver

    def navigate_to(self, url: str, timeout: int = 30) -> None:
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except TimeoutException:
            raise SeleniumDriverError(f"Timeout while loading {url}")
        except WebDriverException as e:
            raise SeleniumDriverError(f"Navigation failed: {str(e)}")

    @staticmethod
    def process_browser_log_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = json.loads(entry['message'])['message']
            return response
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to process log entry: {str(e)}")
            return {}

    def get_performance_logs(self) -> List[Dict[str, Any]]:
        try:
            browser_log = self.driver.get_log('performance')
            return [
                log for log in (self.process_browser_log_entry(entry) for entry in browser_log)
                if log
            ]
        except WebDriverException as e:
            raise SeleniumDriverError(f"Failed to get performance logs: {str(e)}")

    def find_authorization_header(self, timeout: int = 30) -> Optional[str]:
        events = self.get_performance_logs()
        for event in events:
            if (event.get('method') == 'Network.requestWillBeSent' and
                'params' in event and
                'request' in event['params'] and
                'headers' in event['params']['request']):
                
                headers = event['params']['request']['headers']
                if 'Authorization' in headers:
                    # logger.info("Authorization header found")
                    return headers['Authorization']
        
        # logger.warning("No authorization header found within timeout")
        return None

    def quit(self) -> None:
        if self._driver is not None:
            try:
                self._driver.quit()
            except WebDriverException as e:
                logger.error(f"Error while quitting driver: {str(e)}")
            finally:
                self._driver = None
                SeleniumDriver._instance = None

    @contextmanager
    def managed_session(self):
        try:
            yield self
        finally:
            self.quit()