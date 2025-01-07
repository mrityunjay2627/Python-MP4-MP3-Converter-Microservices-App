import os, requests # Different from Flask "request". This "requests" will be used to make HTTP calls to our "auth" service

def login(request):
    auth = request.authorization

    if not auth:
        return None, ("missing credentials", 401)

    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    )

    if response.status_code==200:
        return response.text, None
    else:
        return None, (response.text,response.status_code)