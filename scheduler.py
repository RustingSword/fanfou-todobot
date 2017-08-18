#!/usr/bin/env python2

import schedule
import time
import requests
import sys
from datetime import datetime

def check():
    try:
        r = requests.get('http://127.0.0.1:8001/check')
        print datetime.now(), r.text
    except Exception as e:
        print datetime.now(), 'error checking:' + repr(e)

def notify():
    try:
        r = requests.get('http://127.0.0.1:8001/notify')
        print datetime.now(), r.text
    except Exception as e:
        print datetime.now(), 'error notifying:' + repr(e)

schedule.every(1).minutes.do(check)
schedule.every().day.at("07:30").do(notify)

while True:
    schedule.run_pending()
    sys.stdout.flush()
    time.sleep(1)
