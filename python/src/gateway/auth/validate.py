import os, requests

def token(request):
    token = request.headers.get("Authorization")
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token}
    )

    result = {"error": {"text": response.text, "status_code": response.status_code}}
    if response.status_code == 200:
        result.pop("error")
        result["access"] = response.text

    return result
