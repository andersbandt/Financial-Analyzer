

import requests


def is_connected():
    try:
        # Try connecting to a reliable website
        requests.get("https://www.google.com", timeout=5)
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


# Usage
if is_connected():
    print("Internet connection is active.")
else:
    print("No internet connection.")