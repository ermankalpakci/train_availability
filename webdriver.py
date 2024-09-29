from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
# Start a new instance of Chrome WebDriver
# Configure Chrome options for headless mode
def webdriverrun(departure, arrival, _date, num_passengers):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=old")
    chrome_options.add_argument("--window-position=-10000,-10000")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-images")  # Disable image loading
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36")
    chrome_options.add_argument("--window-size=1920x1080")  # Set a specific window size in headless mode
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--no-first-run")
    # Start a new instance of Chrome WebDriver with headless mode enabled
    # chrome_options.add_argument("--log-path=C:/Users/erman/OneDrive/Desktop/chromedriver.log")
    # chrome_options.add_argument("--verbose")  # More detailed logging
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)    # Navigate to the webpage
    driver.get("https://ebilet.tcddtasimacilik.gov.tr/view/eybis/tnmGenel/tcddWebContent.jsf")
    driver.set_page_load_timeout(30)
    trains_info = {}

    try:
        # Use WebDriverWait to wait until the page is fully loaded
        WebDriverWait(driver, 20).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete")

        # Find and fill the 'from' field
        from_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/ul/li[1]/div/form/div[1]/p[4]/input"))
        )
        from_field.send_keys(departure)

        # Find and fill the 'to' field
        to_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/ul/li[1]/div/form/div[2]/p[4]/input"))
        )
        to_field.send_keys(arrival)

        # Find and fill the 'depart date' field
        depart_date_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/ul/li[1]/div/form/div[1]/p[6]/span/input"))
        )
        depart_date_field.clear()  # Clear existing content
        depart_date_field.send_keys(_date)
        driver.find_element(By.TAG_NAME, 'body').click()

        # Find and fill the 'number of passenger' field
        passenger_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/ul/li[1]/div/form/div[3]/p[2]/span/input"))
        )
        passenger_field.click()
        passenger_field.send_keys(Keys.DELETE)
        passenger_field.send_keys(num_passengers)

        # Find and click the 'find trains' button
        find_trains_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[2]/div/div[2]/ul/li[1]/div/form/div[3]/p[3]/button/span"))
        )
        find_trains_button.click()

        # Wait until the growl message is visible
        try:
            growl_message = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-growl-message")))
            # Capture the text of the growl message
            message_text = growl_message.text
            trains_info["Growl message"] = message_text
            # print(train_info)
            # time.sleep(5)  # Hardcoded interval if necessary

        except:
            pass
        
        # time.sleep(5)  # Hardcoded interval if necessary
        WebDriverWait(driver, 20).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete")

        if "Growl message" not in trains_info:
            # WebDriverWait(driver, 30).until(EC.url_changes(driver.current_url))
            with open("page.html", "w", encoding="utf-8") as file:
                file.write(driver.page_source)
        # Now you can scrape the results page for the information you need
        # Use BeautifulSoup or Selenium to extract the desired information from the page

    # except TimeoutException as e:
    #     raise TimeoutException from e

    finally:
        # Close the WebDriver session
        driver.quit()

    if "Growl message" not in trains_info:

        # Now you can use BeautifulSoup to parse the saved HTML page
        with open("page.html", "r", encoding="utf-8") as file:
            html_content = file.read()

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extracting the information
        rows = soup.find_all('tr', {'data-ri': True})

        for index, row in enumerate(rows):
            departure_date = row.find_all('td')[0].get_text(strip=True).split('\n')[0]
            # departure_time = row.find_all('td')[0].find('span').get_text(strip=True)
            duration = row.find_all('td')[1].find_all('label')[1].get_text(strip=True)
            arrival_date = row.find_all('td')[2].get_text(strip=True).split('\n')[0]
            # arrival_time = row.find_all('td')[2].find('span').get_text(strip=True)
            # train_type = row.find_all('td')[3].find_all('label')[1].get_text(strip=True)
            # route = row.find_all('td')[3].find_all('label')[2].get_text(strip=True)
            # availability_tag = soup.find('div', class_='ui-tooltip ui-widget ui-widget-content ui-shadow ui-corner-all').get_text(strip=True)
            # price = soup.find('label', {'class': 'ui-outputlabel seferSorguTableBuyuk'}).get_text(strip=True)
            wagon_type_options = row.find_all('option')
            wagon_types = [opt.get_text(strip=True) for opt in wagon_type_options]
            
            # Create a dictionary for the current train
            train_info = {
                'Departure Date': departure_date,
                # 'Departure Time': departure_time,
                'Duration': duration,
                'Arrival Date': arrival_date,
                # 'Arrival Time': arrival_time,
                # 'Train Type': train_type,
                # 'Route': route,
                # 'Availability': availability_tag,
                # 'Price': price,
                'Wagon Types': wagon_types
            }
            
            # Add the current train info to the main dictionary
            trains_info[f'Train {index + 1}'] = train_info

    # print(trains_info)
    # retries = 3
    # if len(trains_info) == 0:
    #     for i in range(retries):
    #         trains_info = webdriverrun()
    #         if trains_info:
    #             break
    #         time.sleep(3)

    return trains_info
# webdriverrun("Ankara", "Ankara", "29.09.2024", 4)
