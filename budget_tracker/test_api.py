import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/"

def login(username, password):
    url = f"{BASE_URL}login/"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    print(f"Login Response: {response.status_code} {response.json()}")
    if response.status_code == 200:
        return response.json()["token"]
    return None

def get_summary(token):
    url = f"{BASE_URL}summary/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print(f"Summary Response Status: {response.status_code}")
    try:
        print(f"Summary Response JSON: {response.json()}")
    except json.JSONDecodeError:
        print(f"Summary Response (raw): {response.text}")
    return response

def get_profile(token):
    url = f"{BASE_URL}profile/"
    headers = {"Authorization": f"Token {token}"}
    response = requests.get(url, headers=headers)
    print(f"Profile Response Status: {response.status_code}")
    try:
        print(f"Profile Response JSON: {response.json()}")
    except json.JSONDecodeError:
        print(f"Profile Response (raw): {response.text}")
    return response

# Test flow with superuser
username = "root"
password = "rootpassword"

# Log in with superuser
token = login(username, password)

if token:
    print(f"Obtained Token: {token}")
    # Get summary
    get_summary(token)
    # Get profile
    get_profile(token)
else:
    print("Login failed for superuser. Cannot proceed with authenticated requests.")