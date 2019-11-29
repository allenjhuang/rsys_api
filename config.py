# Responsys API
"""Below URLs and API version were last checked to be up to date on 11/3/2019.
LOGIN_BASE_URL:
    Pod2: "https://login2.responsys.net"
    Pod5: "https://login5.responsys.net"
"""
LOGIN_BASE_URL = "https://login2.responsys.net"
API_VERSION = "v1.3"
BASE_RESOURCE_PATH = f"/rest/api/{API_VERSION}/"

TRY_REQUEST_SETTINGS = {
    # Number of attempts made for an API call before giving up
    'times_to_try': 3,
    # Amount of time in seconds to wait between each try
    'wait_before_next_attempt': 30,
    # Try an API call until one of the listed status codes is returned
    'target_status_codes': [200],  # Can add acceptable status codes here.
    # Seconds to wait for an API call before timing out
    'request_timeout': 20.0
}
