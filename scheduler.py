#!/usr/bin/env python2

import schedule
import time
import requests
from datetime import datetime

def check():
    r = requests.get('http://127.0.0.1:8001/check')
    print datetime.now(), r.text

def notify():
    r = requests.get('http://127.0.0.1:8001/notify')
    print datetime.now(), r.text

schedule.every(1).minutes.do(check)
schedule.every().day.at("07:30").do(notify)

while True:
    schedule.run_pending()
    time.sleep(1)
