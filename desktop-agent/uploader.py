import requests
import os

API_URL = "http://localhost:8000/api/sales/upload" # Change to cloud URL later

def send_file_to_backend(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
        
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        try:
            response = requests.post(API_URL, files=files)
            if response.status_code == 200:
                print(f"✅ Successfully uploaded: {file_path}")
            else:
                print(f"❌ Upload failed: {response.text}")
        except Exception as e:
            print(f"⚠️ Connection error: {e}")

# Test call
# send_file_to_backend("C:/Medivision/Reports/DailySales.csv")