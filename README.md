
# Available Train Seat Finder - TCDD

A PyQt5-based desktop application to search for available seats on Turkish State Railways (TCDD) high-speed trains, with email notification support. Let’s say you want to travel somewhere tomorrow, but there are no vacant seats available for your desired date and time. This app continuously searches for seat availability and notifies when found.

## Features
- **Interactive GUI**: Search for trains with customizable criteria
- **Smart Search Parameters**:
  - Departure/arrival stations with auto-complete
  - Date selection with calendar widget
  - Time range or "any time" option
  - Passenger count (1-11)
  - Train type preferences (YHT only, transfers, etc.)
  - Seat class options (business, sleeper, etc.)
- **Email Notifications**: Receive alerts via Gmail (app password required, not your gmail password)(https://myaccount.google.com/apppasswords)
- **Background Processing**: Asynchronous Selenium authentication
- **Search Management**:
  - Multiple simultaneous searches
  - Pause/resume/remove functionality
  - Search history tracking(last tried)
- **Real-time Status Updates**: Visual indicators for search progress

## Installation

## Installation
**Prerequisites**:
   - Python 3.8+
   - Chrome browser installed
   - [ChromeDriver](https://chromedriver.chromium.org/) in system PATH

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

## Screenshots

![Screenshot From 2025-03-16 19-21-57](https://github.com/user-attachments/assets/e5cc4fc7-d822-4972-be92-62c6be4aa5f3)
