import requests


def get_google_user_info(access_token: str = ""):
    if access_token == "":
        return None
    endpoint = "https://www.googleapis.com/userinfo/v2/me"
    headers = {"Authorization": "Bearer {}".format(access_token)}
    try:
        response = requests.get(url=endpoint, headers=headers)
        if response.ok:
            return response.json()
        else:
            print(response.reason)
            return None
    except Exception as e:
        print("get_google_user_info EXCEPTION:", e)
        return None
