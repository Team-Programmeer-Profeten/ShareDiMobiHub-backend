import requests
import json

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
    # zone_ids komen binnen met , als separator
    # gebruik in de echte api de data uit de timestamp dict die binnenkomt om de data per timestamp op te halen, we hebben deze mogelijk niet met de geleverde mock-api dus dit kunnen we niet testen.
    # real request = f"https://api.dashboarddeelmobiliteit.nl/dashboard-api/park_events?zone_ids={zone_ids}&timestamp={timestamp.get("start_date")}"
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

def vehicle_rented_in_zonelist_per_day(zone_ids):
    ids = ",".join(zone_ids)
    # request = https://api.dashboarddeelmobiliteit.nl/dashboard-api/aggregated_stats/rentals?aggregation_level=day&aggregation_time=undefined&zone_ids=ids&start_time=2022-11-16T00:00:00Z&end_time=2022-11-20T00:00:00Z
    mockRequest = "https://www.stoopstestdomein.nl/mock-api/9.json"
    response_str = requests.get(mockRequest)
    response = json.loads(response_str.content)
    return response

def hubs_by_municipality(GM_code):
    # remove no parking from actual request when in prod
    # request = "https://mds.dashboarddeelmobiliteit.nl/admin/zones?municipality={GM_code}&geography_types=no_parking&geography_types=stop&geography_types=monitoring"
    mockRequest = "https://www.stoopstestdomein.nl/mock-api/10.json"
    response_str = requests.get(mockRequest)
    response = json.loads(response_str.content)
    return response

def vehicles_in_municipality(GM_code, aggregation, start_time, end_time):
    # hubs = hubs_by_municipality(GM_code)
    # ids = map(lambda x: x.get("zone_id"))
    # request = f"https://api.dashboarddeelmobiliteit.nl/dashboard-api/aggregated_stats/available_vehicles?aggregation_level={aggregation}&aggregation_time=undefined&zone_ids={ids}&start_time={start_time}&end_time={end_time}"
    mockRequest = "https://www.stoopstestdomein.nl/mock-api/8.json"
    response_str = requests.get(mockRequest)
    response = json.loads(response_str.content).get("available_vehicles_aggregated_stats").get("values")
    print(type(response))
    return response