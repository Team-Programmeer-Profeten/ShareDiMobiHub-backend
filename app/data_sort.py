import datetime

today = datetime.date.today()

# Get the date from 30 days ago
thirty_days_ago = today - datetime.timedelta(days=30)

DATA_OPTIONS = {
    {
        "details": [
            {
                "amount_vehicles": True,
                "distance_travelled": True,
                "rentals": True,
                "zone_occupation": True
            }
        ],
        "areas": [
            {
                # Lijst van zones
            }
        ],
        "timeslot": [
            {
                "start-date": thirty_days_ago,
                "end-date": today
            }
        ],
        "time-format": [
            {
                "hourly": False,
                "daily": False,
                "monthly": True,
                "yearly": False
            }
        ]
    }
}