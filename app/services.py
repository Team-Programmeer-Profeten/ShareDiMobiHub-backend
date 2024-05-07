import requests
import json
from datetime import datetime

json_data = {
    "municipality": "Amersfoort",
    "details": {
        "amount_vehicles": False,
        "distance_travelled": False,
        "rentals": False,
        "zone_occupation": True
    },
    "areas": [],
    "timeslot": {
        "start_date": "2024-03-03",
        "end_date": "2024-04-02"
    },
    "time_format": "daily"
}

park_event_data = {
    "park_events": [
        {
            "bike_id": "check:3f6f6d76-261f-4635-a83d-cdfd6adb10fd",
            "end_time": None,
            "form_factor": "moped",
            "location": {
                "latitude": 51.90950318883196,
                "longitude": 4.424026220523164
            },
            "start_time": "2023-12-01T10:03:48.996584Z",
            "system_id": "check"
        },
        {
            "bike_id": "donkey:35396",
            "end_time": None,
            "form_factor": "bicycle",
            "location": {
                "latitude": 51.916123890724094,
                "longitude": 4.454881834110924
            },
            "start_time": "2023-12-31T22:51:00.128967Z",
            "system_id": "donkey"
        },
        {
            "bike_id": "donkey:14357",
            "end_time": None,
            "form_factor": "bicycle",
            "location": {
                "latitude": 51.920390191591004,
                "longitude": 4.4739769810402805
            },
            "start_time": "2024-01-08T20:06:09.451316Z",
            "system_id": "donkey"
        },
        {
            "bike_id": "check:ed1a7953-ee2c-4ed9-85c6-77551987a68e",
            "end_time": None,
            "form_factor": "moped",
            "location": {
                "latitude": 51.910317103396935,
                "longitude": 4.425207440463481
            },
            "start_time": "2024-01-08T18:33:32.671667Z",
            "system_id": "check"
        },
        {
            "bike_id": "donkey:26839",
            "end_time": None,
            "form_factor": "bicycle",
            "location": {
                "latitude": 51.91410173233142,
                "longitude": 4.522598000166812
            },
            "start_time": "2024-01-09T18:21:44.168253Z",
            "system_id": "donkey"
        },
        {
            "bike_id": "gosharing:ik8i",
            "end_time": "2024-02-19T19:56:41.368516Z",
            "form_factor": "bicycle",
            "location": {
                "latitude": 51.97035638060694,
                "longitude": 4.563827475798044
            },
            "start_time": "2024-01-13T16:43:49.500090Z",
            "system_id": "gosharing"
        },
        {
            "bike_id": "check:1d658939-3dfb-40f4-8e36-e48ac1ee2aee",
            "end_time": None,
            "form_factor": "moped",
            "location": {
                "latitude": 51.91882091600405,
                "longitude": 4.501299485979865
            },
            "start_time": "2024-01-13T17:40:01.830909Z",
            "system_id": "check"
        },
        {
            "bike_id": "gosharing:6rtv",
            "end_time": "2024-02-15T16:00:32.075300Z",
            "form_factor": "moped",
            "location": {
                "latitude": 51.872732085468414,
                "longitude": 4.425197317861058
            },
            "start_time": "2023-07-29T22:59:27.853381Z",
            "system_id": "gosharing"
        },
        {
            "bike_id": "check:6a986f5e-f8a8-44f9-86d8-f66379654dab",
            "end_time": "2024-02-14T14:33:52.734607Z",
            "form_factor": "moped",
            "location": {
                "latitude": 51.90919389137176,
                "longitude": 4.424884021801983
            },
            "start_time": "2023-09-04T13:06:10.476429Z",
            "system_id": "check"
        }]
}

def data_sort(json_data):
  details = select_details(json_data)
  return details  

def select_details(json_data):
    chosen_details = {}
    json_details = json_data.get("details")
    for key, value in json_details.items():
      if(value):
        match(key):
          case "amount_vehicles":
            chosen_details = vehicles_in_zone_per_day() # In development we use this mock, but in production we use amount_vehicles(json_data)
            # chosen_details = amount_vehicles(json_data)
          case "distance_travelled":
            chosen_details = None
            # TODO: distance travelled
          case "rentals":
            chosen_details = None
            # TODO: rentals
          case "zone_occupation":
            chosen_details = park_events_per_municipality(json_data.get("municipality", json_details.get("timeslot")))
            # TODO: zone occupation
          case _:
            chosen_details = None

      return chosen_details

def park_events_per_municipality(municipality):
  '''
  functie duurt mega lang want elke zone heeft heel veel json aan park events die opgehaald wordt via api park_events(id, timeslot)
  als je dan door elke zone van een grote gemeente gaat is dat pijn
  '''
  zones = zones_by_gmcode(find_municipality_gmcode(municipality))
  eventsPerMunicipality = {"park_events" : []}
  for zone in zones:
    id = zone.get("zone_id")
    eventsPerMunicipality["park_events"].append(park_events(id))
  return eventsPerMunicipality

def average_parkingtime_per_vehicletype_and_municipality():
  for parkEvent in park_event_data["park_events"]:
    print(parkEvent["end_time"])
    start_time = parkEvent["start_time"]
    end_time = parkEvent["end_time"]
    if(start_time or end_time == None):
      print("is none")
      continue
    print(parkEvent)

def validate_municipality(municipality):
  codes = json.loads(gm_codes())
  for gm in codes["filter_values"]["municipalities"]:
    if gm["name"] == municipality:
      return gm["gm_code"]
  raise ValueError("Municipality not found")

def zone_ids_by_gmcode(gmcode):
  zones = []
  for zone in zones_by_gmcode(gmcode):
    zones.append(zone["zone_id"])
  return zones

# Amount of vehicles available in a municipality
def amount_vehicles(json_data):
    aggr_lvl = json_data.get("time_format")
    zone_ids = zone_ids_by_gmcode(json_data.get("municipality"))
    start_time = json_data.get("timeslot")["start_date"]
    end_time = json_data.get("timeslot")["end_date"]

    request = f"https://api.dashboarddeelmobiliteit.nl/dashboard-api/stats_v2/availability_stats?aggregation_level={aggr_lvl}&group_by=operator&aggregation_function=MAX&zone_ids={zone_ids}&start_time={start_time}&end_time={end_time}"
    response_str = requests.get(request)
    response = json.loads(response_str.content)

    return response
  
  
def areas_from_json(json_str):
  data = json.loads(json_str)
  areas = data["areas"]
  return areas


def timeslot_from_json(json_str):
  data = json.loads(json_str)
  json_timeslot = data["timeslot"]
  start_date = datetime.strptime(json_timeslot["start_date"], "%Y-%m-%d")
  end_date = datetime.strptime(json_timeslot["end_date"], "%Y-%m-%d")
  timeslot = [start_date, end_date]
  return timeslot

def time_format_from_json(json):
  data = json.loads(json)
  time_format = data["time_format"]
  return time_format

###---------------------------------------------API calls---------------------------------------------------###
def find_municipality_gmcode(municipality):
  if(municipality == None):
    raise ValueError("No municipality given")
  codes = gm_codes().get("filter_values")
  for i in codes.get("municipalities"):
    if i.get("name") == municipality:
      return i.get("gm_code")
  raise Exception("gm code could not be found")

def gm_codes():
  response = requests.get("https://api.dashboarddeelmobiliteit.nl/dashboard-api/public/filters")
  codes = response.content
  return json.loads(codes)

def zones_by_gmcode(gmcode): 
  # request = "https://api.dashboarddeelmobiliteit.nl/dashboard-api/zones?gm_code={gmcode}".format(gmcode = gmcode)
  request = "https://www.stoopstestdomein.nl/mock-api/1.json"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response["zones"]

# Points on map (public api)
def points_on_map():
  request = "https://api.dashboarddeelmobiliteit.nl/dashboard-api/public/vehicles_in_public_space"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response

# Park events, per zone per timestamp
def park_events(zone_ids, timestamp):
  request = "https://www.stoopstestdomein.nl/mock-api/3.json"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response

# User info
def user_info():
  request = "https://www.stoopstestdomein.nl/mock-api/4.json"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response

# Origins from vehicle and how far has it moved
def origin_distance():
  request = "https://www.stoopstestdomein.nl/mock-api/5.json"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response

# Destinations from vehicle and how far has it moved
def location_distance_moved(zone_ids, start_time, end_time):
  request = "https://www.stoopstestdomein.nl/mock-api/6.json"
  response_str = requests.get(request)
  response = json.loads(response_str.content)
  return response

# How many vehicles are in a zone per hour
def vehicles_in_zone_per_hour():
  # request = https://api.dashboarddeelmobiliteit.nl/dashboard-api/stats_v2/availability_stats?aggregation_level=hour&group_by=operator&aggregation_function=MAX&zone_ids=52098&start_time=2024-02-27T00:00:00Z&end_time=2024-02-28T00:00:00Z
  mockRequest = "https://www.stoopstestdomein.nl/mock-api/7.json"
  response_str = requests.get(mockRequest)
  response = json.loads(response_str.content)
  return response

# How many vehicles are in a zone per day
def vehicles_in_zone_per_day():
  # request = "https://api.dashboarddeelmobiliteit.nl/dashboard-api/aggregated_stats/available_vehicles?aggregation_level=day&aggregation_time=undefined&zone_ids=34234&start_time=2024-01-28T16:27:45Z&end_time=2024-02-28T16:27:45Z"
  mockRequest = "https://www.stoopstestdomein.nl/mock-api/8.json"
  response_str = requests.get(mockRequest)
  response = json.loads(response_str.content)
  return response

# How much is a vehicle rented in a zone per day
def vehicle_rented_in_zone_per_day():
  # request = https://api.dashboarddeelmobiliteit.nl/dashboard-api/aggregated_stats/rentals?aggregation_level=day&aggregation_time=undefined&zone_ids=49562&start_time=2022-11-16T00:00:00Z&end_time=2022-11-20T00:00:00Z
  mockRequest = "https://www.stoopstestdomein.nl/mock-api/9.json"
  response_str = requests.get(mockRequest)
  response = json.loads(response_str.content)
  return response

print(average_parkingtime_per_vehicletype_and_municipality())
