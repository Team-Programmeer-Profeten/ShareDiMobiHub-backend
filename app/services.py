import json
from datetime import datetime
import datetime as dt
from collections import defaultdict
from pdf_generator import create_pdf

from api_calls import *

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

    start_date_str = start_date_obj.strftime("%d-%m")
    end_date_str = end_date_obj.strftime("%d-%m")
    chosen_details["time_period"] = f"{start_date_str} | {end_date_str}"

    chosen_details["date"] = datetime.now().strftime("%d-%m-%Y")

    chosen_details["topics"] = []

    chosen_details["amount_hubs"] = total_amount_hubs(json_data)

    chosen_details["service_providers"] = get_service_providers()

    json_details = json_data.get("details")

    chosen_details["avg_parking_time"] = average_parkingtime_per_vehicletype_in_hours(json_data)
    chosen_details["avg_distance_travelled"] = average_distance_travelled_per_vehicletype_in_meters(json_data)

    chosen_details["top_5_zones_rented"] = top_5_zones_rented(json_data)
    chosen_details["top_5_hubs"] = top_5_hubs_rented(json_data)

    chosen_details["total_amount_vehicles"] = total_amount_vehicles()
    chosen_details["total_vehicles_rented"] = total_vehicles_rented()

    # optional details
    for key, value in json_details.items():
      if(value):
        match key:
          case "amount_vehicles":
            chosen_details["topics"].append("Hoeveelheid Voertuigen")
            chosen_details["amount_vehicles"] = vehicles_in_zone_per_day()
          case "distance_travelled":
            chosen_details["topics"].append("Afstand Afgelegd")
            chosen_details["distance_travelled"] = location_distance_moved(json_data.get("zone_ids"), json_data.get("start_time"), json_data.get("end_time"))
          case "rentals":
            chosen_details["topics"].append("Verhuringen")
            chosen_details["rentals"] = total_vehicles_rented_per_time_period()
          case "zone_occupation":
            chosen_details["topics"].append("Zone Bezetting")
            chosen_details["zone_occupation"] = park_events(json_data.get("zone_ids"), json_data.get("timestamp"))
          case "hubs":
            chosen_details["topics"].append("Hubs")
            chosen_details["hubs"] = hubs_by_municipality(json_data.get("municipality"))
          case _:
            chosen_details = None

    return chosen_details

def park_events_per_municipality(municipality, timeslot):
  ids = zone_ids_per_municipality(municipality)
  events = park_events(','.join(map(str, ids)), timeslot)
  return events

def zone_ids_per_municipality(municipality):
  zones = zones_by_gmcode(find_municipality_gmcode(municipality))
  ids = [zone.get("zone_id") for zone in zones]
  return ids

def average_parkingtime_per_vehicletype_in_hours(selectedDetails):
  park_event_data = park_events_per_municipality(selectedDetails.get("municipality"), selectedDetails.get("timeslot"))
  vehicleTypeCount = defaultdict(int)
  sumPerVehicleType = defaultdict(dt.timedelta)
  for parkEvent in park_event_data["park_events"]:
    if(parkEvent["end_time"] is None or parkEvent["start_time"] is None):
      continue
    start_time = dt.datetime.strptime(parkEvent["start_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    end_time = dt.datetime.strptime(parkEvent["end_time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    sumPerVehicleType[parkEvent["form_factor"]] += end_time - start_time
    vehicleTypeCount[parkEvent["form_factor"]] += 1

  averagePerVehicleType = defaultdict(dt.timedelta)
  for vehicleType in sumPerVehicleType:
    average_seconds = round(sumPerVehicleType[vehicleType].total_seconds() / vehicleTypeCount[vehicleType], 3)
    average_minutes = average_seconds / 60
    average_hours = round(average_minutes / 60, 1)
    averagePerVehicleType[vehicleType] = average_hours
  return dict(averagePerVehicleType)

def average_distance_travelled_per_vehicletype_in_meters(selectedDetails):
    municipality_ids = zone_ids_per_municipality(selectedDetails.get("municipality"))
    distance_travelled_data = location_distance_moved(municipality_ids, selectedDetails.get("timeslot").get("start_date"), selectedDetails.get("timeslot").get("end_date")).get("trip_destinations")
    vehicleTypeCount = defaultdict(int)
    sumPerVehicleType = defaultdict(int)
    for distance_data in distance_travelled_data:
      vehicleTypeCount[distance_data["form_factor"]] += 1 #  system_id  is the brand
      sumPerVehicleType[distance_data["form_factor"]] += distance_data["distance_in_meters"]

    averagePerVehicleType = defaultdict(int)
    for vehicleType in sumPerVehicleType:
        averagePerVehicleType[vehicleType] = round(sumPerVehicleType[vehicleType] / vehicleTypeCount[vehicleType], 2)
    return dict(averagePerVehicleType)

def validate_municipality(municipality):
  codes = gm_codes()
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
  operators = user_info().get("operators")
  operator_names = [operators["name"] for operators in operators]
  return operator_names

def total_amount_vehicles():
  json_data = vehicles_in_zone_per_day()
  sum_dict = {}
  for item in json_data["available_vehicles_aggregated_stats"]["values"]:
    for key, value in item.items():
        if key != "start_interval":
          if key in sum_dict:
            sum_dict[key] += value
          else:
            sum_dict[key] = value
  return sum_dict

def total_vehicles_rented():
  vehiclesRentedPerDay = vehicle_rented_in_zone_per_day()["rentals_aggregated_stats"]["values"]
  for item in vehiclesRentedPerDay:
    item.pop("start_interval")
  total = sum(sum(item.values()) for item in vehiclesRentedPerDay)
  newJson = {"total": total}
  return newJson

def top_5_zones_rented(json_data):
  zones = zones_by_gmcode(validate_municipality(json_data.get("municipality")))

  zones = list(filter(lambda zone: zone["zone_type"] == "neighborhood", zones))
  top5 = {}

  zone_ids = []
  for zone in zones:
    zone_ids.append(zone["zone_id"])

  for zone in zones:
    vehiclesRentedPerDay = vehicle_rented_in_zone_per_day()["rentals_aggregated_stats"]["values"][0]
    vehiclesRentedPerDay.pop("start_interval")
    total_rentals = sum(vehiclesRentedPerDay.values())
    top5[zone['name']] = total_rentals

  top5 = dict(sorted(top5.items(), key=lambda item: item[1], reverse=True)[:5])

  newJson = {"top5": top5}
  return newJson

def top_5_hubs_rented(json_data):
  zones = zones_by_gmcode(validate_municipality(json_data["municipality"]))
  top5 = {}

  for zone in zones:
    if(zone["zone_type"] == "custom" and not "no_park" in zone["name"]):
        vehiclesRentedPerDay = vehicle_rented_in_zone_per_day()["rentals_aggregated_stats"]["values"][0]
        vehiclesRentedPerDay.pop("start_interval")
        total_rentals = sum(vehiclesRentedPerDay.values())
        top5[zone['name']] = total_rentals

  top5 = dict(sorted(top5.items(), key=lambda item: item[1], reverse=True)[:5])
  return {"top5": top5}

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


data = {
  "municipality": "Rotterdam",
  "details": {
    "amount_vehicles": True,
    "distance_travelled": True,
    "rentals": True,
    "zone_occupation": True,
    "hubs": False
  },
  "areas": [],
  "timeslot": {
    "start_date": "2024-03-03",
    "end_date": "2024-04-02"
  },
  "time_format": "daily"
}


# print(data_sort({
#   "municipality": "Rotterdam",
#   "details": {
#     "amount_vehicles": True,
#     "distance_travelled": True,
#     "rentals": True,
#     "zone_occupation": True,
#     "hubs": True
#   },
#     "areas": [],
#     "timeslot": {
#         "start_date": "2024-03-03",
#         "end_date": "2024-04-02"
#     },
#     "time_format": "daily"
# }))
