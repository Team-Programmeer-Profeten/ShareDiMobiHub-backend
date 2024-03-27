import requests
from flask import Flask
import json
from typing import TypedDict

class Zone(TypedDict):
  municipality: str
  name:         str
  owner:        any
  zone_id:      int
  zone_type:    str

def gm_codes():
  response = requests.get("https://api.dashboarddeelmobiliteit.nl/dashboard-api/public/filters")
  codes = response.content
  return codes

def zones_by_gmcode(gmcode: str) -> list[Zone]: 
  # request = "https://api.dashboarddeelmobiliteit.nl/dashboard-api/zones?gm_code={gmcode}".format(gmcode = gmcode)
  request = "https://www.stoopstestdomein.nl/mock-api/1.json"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response["zones"]

print(zones_by_gmcode("GM0599"))