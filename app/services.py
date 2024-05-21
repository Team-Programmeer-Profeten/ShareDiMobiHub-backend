import requests
import json
from datetime import datetime
from collections import defaultdict
from pdf_generator import create_pdf

def data_sort(json_data):
  details = select_details(json_data)
  report = create_pdf(details)
  return report

def select_details(json_data):
    chosen_details = {}

    municipality = json_data.get("municipality")
    chosen_details["municipality"] = municipality

    start_date = json_data.get("timeslot")["start_date"]
    end_date = json_data.get("timeslot")["end_date"]

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

    # Format the dates as "DD-MM"
    start_date_str = start_date_obj.strftime("%d-%m")
    end_date_str = end_date_obj.strftime("%d-%m")
    chosen_details["time_period"] = f"{start_date_str} | {end_date_str}"

    chosen_details["date"] = datetime.now().strftime("%d-%m-%Y")

    chosen_details["topics"] = []

    chosen_details["amount_hubs"] = total_amount_hubs(json_data)

    chosen_details["service_providers"] = get_service_providers()

    json_details = json_data.get("details")
    for key, value in json_details.items():
      if(value):
        match(key):
          case "amount_vehicles":
            chosen_details["topics"].append("Hoeveelheid Voertuigen")
            chosen_details["amount_vehicles"] = vehicles_in_zone_per_day() # Mock data
            # chosen_details["amount_vehicles"] = amount_vehicles(json_data)
          case "distance_travelled":
            chosen_details["topics"].append("Afstand Afgelegd")
            chosen_details["distance_travelled"] = location_distance_moved(json_data.get("zone_ids"), json_data.get("start_time"), json_data.get("end_time")) # Mock data
            # chosen_details["distance_travelled"] = distance_travelled(json_data)
          case "rentals":
            chosen_details["topics"].append("Verhuringen")
            chosen_details["rentals"] = total_vehicles_rented_per_time_period() # Mock data
          case "zone_occupation":
            chosen_details["topics"].append("Zone Bezetting")
            chosen_details["zone_occupation"] = park_events(json_data.get("zone_ids"), json_data.get("timestamp")) # Mock data
            # TODO: zone occupation
          case "hubs":
            chosen_details["topics"].append("Hubs")
            chosen_details["hubs"] = hubs_by_municipality(json_data.get("municipality")) # Mock data
          case _:
            pass

    return chosen_details

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

def total_amount_hubs(json_data):
  return len(hubs_by_municipality(json_data.get("municipality")))

def get_service_providers():
  # TODO: Implement service providers
  return [{ 'name': 'Cargoroo', 'type': 'Fiets' }, { 'name': 'Tier', 'type': 'Fiets'}, { 'name': 'Check', 'type': 'Scooter, Auto' }, { 'name': 'Donkey', 'type': 'Fiets' }, { 'name': 'Felyx', 'type': 'Scooter' }] # Mock data

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

def total_vehicles_rented():
  vehiclesRentedPerDay = vehicle_rented_in_zone_per_day()["rentals_aggregated_stats"]["values"]
  for item in vehiclesRentedPerDay:
    item.pop("start_interval")
  total = sum(sum(item.values()) for item in vehiclesRentedPerDay)
  newJson = {"total": total}
  return newJson

def total_vehicles_rented_per_time_period():
  vehiclesRentedPerDay = vehicle_rented_in_zone_per_day()["rentals_aggregated_stats"]["values"] 
  sumPerVehicleType = defaultdict(int) # https://www.geeksforgeeks.org/defaultdict-in-python/
  for item in vehiclesRentedPerDay:
    item.pop("start_interval", None)
    for key, value in item.items():
      sumPerVehicleType[key] += value
  return dict(sumPerVehicleType)

  
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

def distance_travelled(json_data):
  data = json.loads(json_data)
  zone_ids = zone_ids_by_gmcode(data.get("municipality"))
  start_time = data.get("timeslot")["start_date"]
  end_time = data.get("timeslot")["end_date"]
  request = f'https://api.dashboarddeelmobiliteit.nl/dashboard-api/v2/trips/origins?zone_ids={zone_ids}&start_time={start_time}&end_time={end_time}'
  response_str = requests.get(request)
  response = json.loads(response_str.content)

  distance_per_brand = {}
  for trip in response:
    if trip["system_id"] not in distance_per_brand:
      distance_per_brand[trip["system_id"]] = 0
    distance_per_brand[trip["system_id"]] += trip["distance"]
  return distance_per_brand

###---------------------------------------------API calls---------------------------------------------------###

def gm_codes():
  response = requests.get("https://api.dashboarddeelmobiliteit.nl/dashboard-api/public/filters")
  codes = response.content
  return codes

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

def hubs_by_municipality(GM_code):
  # remove no parking from actual request when in prod
  # request = "https://mds.dashboarddeelmobiliteit.nl/admin/zones?municipality=GM0599&geography_types=no_parking&geography_types=stop&geography_types=monitoring"
  mockRequest = "https://www.stoopstestdomein.nl/mock-api/10.json"
  response_str = requests.get(mockRequest)
  response = json.loads(response_str.content)
  return response


# print(data_sort({
#   "municipality": "Rotterdam",
#   "details": {
#     "amount_vehicles": True,
#     "distance_travelled": True,
#     "rentals": True,
#     "zone_occupation": True,
#     "hubs": False
#   },
#     "areas": [],
#     "timeslot": {
#         "start_date": "2024-03-03",
#         "end_date": "2024-04-02"
#     },
#     "time_format": "daily"
# }))