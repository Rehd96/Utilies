# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 17:38:42 2024

@author: Ion
"""
from datetime import datetime, timedelta
from collections import defaultdict

# Assume the dictionary is in the following format
data = {
    "dates": ["2022-01-01 06:30", "2022-01-01 07:00", "2022-01-01 07:30", "2022-01-01 08:00", "2022-01-01 14:00"],
    "bools": [True, False, True, True, False]
}

# Convert the dates to datetime objects
data["dates"] = [datetime.strptime(date, "%Y-%m-%d %H:%M") for date in data["dates"]]

# Initialize a dictionary to store the counts
counts = defaultdict(int)

# Iterate over the dates and bools
for date, bool in zip(data["dates"], data["bools"]):
    # If the time is within the range 06:00 to 14:00 and the bool is True
    if date.time() >= datetime.strptime("06:00", "%H:%M").time() and date.time() <= datetime.strptime("14:00", "%H:%M").time() and bool:
        # Increment the count for the hour
        counts[date.hour] += 1

# Print the counts
for hour in range(6, 15):
    print(f"Hour {hour}: {counts[hour]} occurrences")
