import urllib.request
import json

# Test health endpoint
try:
    with urllib.request.urlopen('http://localhost:5000/api/health') as response:
        data = json.loads(response.read().decode())
        print("Health endpoint response:", data)
except Exception as e:
    print("Health endpoint error:", e)

# Test contracts endpoint
try:
    with urllib.request.urlopen('http://localhost:5000/api/contracts') as response:
        data = json.loads(response.read().decode())
        print("Contracts endpoint response:", data)
except Exception as e:
    print("Contracts endpoint error:", e)