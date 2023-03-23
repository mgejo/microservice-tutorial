import os, requests
from requests.auth import HTTPBasicAuth

def login(request):
    auth = request.authorization

    basic = HTTPBasicAuth(None, None)

    if auth:
        basic = HTTPBasicAuth(auth.get("username"), auth.get("password"))

    response = requests.post(f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basic)

    result = {"error": {"text": response.text, "status_code": response.status_code}}
    if response.status_code == 200:
        result.pop("error")
        result["token"] = response.text

    return result
