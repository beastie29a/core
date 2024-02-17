"""Constants for the Home Connect v2 integration."""
import os
from typing import Final

DOMAIN = "home_connect_v2"
API_ENDPOINT = "https://api.home-connect.com"

if os.getenv("HOMECONNECT_DEV"):
    API_ENDPOINT = "https://simulator.home-connect.com"

OAUTH2_AUTHORIZE: Final = f"{API_ENDPOINT}/security/oauth/authorize"
OAUTH2_TOKEN: Final = f"{API_ENDPOINT}/security/oauth/token"
