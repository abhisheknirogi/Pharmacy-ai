import time
import os
import requests

WATCH_FOLDER = "C:/MedivisionExports"

while True:
    for f in os.listdir(WATCH_FOLDER):
        if f.endswith(".csv"):
            print("Found sales file:", f)
            # Upload to FastAPI
    time.sleep(10)
