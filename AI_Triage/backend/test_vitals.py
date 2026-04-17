import requests
import sys

try:
    with open("test.webm", "wb") as f:
        f.write(b"dummy video content")

    with open("test.webm", "rb") as f:
        files = {"video": f}
        r = requests.post("http://127.0.0.1:5000/analyze_vitals", files=files)
        print("Status code:", r.status_code)
        print("Response:", r.text)
except Exception as e:
    print("Error:", e)
