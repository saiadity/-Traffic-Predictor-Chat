import pandas as pd
from datetime import datetime
import os
import re

# Load dataset once
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'traffic_data.csv')
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

# Parse datetime column
df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d-%m-%Y %H:%M', dayfirst=True, errors='coerce')
df['Hour'] = df['Datetime'].dt.hour


def predict_traffic(hour_query: int, rounded: bool = True) -> str:
    """
    Predict average traffic based on nearby hours (hour-1, hour, hour+1)
    """
    hours = [(hour_query - 1) % 24, hour_query % 24, (hour_query + 1) % 24]
    filtered = df[df['Hour'].isin(hours)]
    avg_traffic = filtered['Count'].mean()

    if pd.isna(avg_traffic):
        return "Sorry, I don't have enough data to predict traffic at that hour."

    avg_display = round(avg_traffic) if rounded else f"{avg_traffic:.2f}"

    if round(avg_traffic)<= 100:
        status = "less than 50 units  you will likely reach your destination on time."
    elif round(avg_traffic) <= 200:
        status = "moderate  consider leaving a bit early."
    else:
        status = "heavy  expect delays and plan ahead."

    return f"Based on nearby hours, the average traffic around {hour_query}:00 is {avg_display} units. It's {status}"

def predict_traffic_by_date_hour(date_str: str, hour_query: int, rounded: bool = True) -> str:
    """
    Predict traffic based on a specific date and hour.
    """
    try:
        date_obj = pd.to_datetime(date_str).date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    hours = [(hour_query - 1) % 24, hour_query % 24, (hour_query + 1) % 24]
    filtered = df[(df['Datetime'].dt.date == date_obj) & (df['Hour'].isin(hours))]

    if filtered.empty:
        return f"No data found for {date_str} at {hour_query}:00 or nearby hours."

    avg_traffic = filtered['Count'].mean()
    avg_display = round(avg_traffic) if rounded else f"{avg_traffic:.2f}"

    # Corrected logic
    if round(avg_traffic) <= 100:
        status = "low — you will likely reach your destination on time."
    elif round(avg_traffic) <= 200:
        status = "moderate — consider leaving a bit early."
    else:
        status = "heavy  expect delays and plan ahead."

    return f"On {date_str}, around {hour_query}:00, the average traffic is {avg_display} units. It's {status}"


def handle_user_query(message: str) -> str:
    """
    Handle user message and decide which function to call.
    """
    # Try to extract date (YYYY-MM-DD)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
    date_str = date_match.group(1) if date_match else None

    # Try to extract hour in 12-hour format
    hour_match = re.search(r'(\d{1,2})\s*(am|pm)', message, re.IGNORECASE)
    if hour_match:
        hour = int(hour_match.group(1))
        meridian = hour_match.group(2).lower()
        if meridian == 'pm' and hour != 12:
            hour += 12
        elif meridian == 'am' and hour == 12:
            hour = 0

        if date_str:
            return predict_traffic_by_date_hour(date_str, hour)
        else:
            return predict_traffic(hour)

    # Try 24-hour format like "14" or "14:00"
    hour_match_24 = re.search(r'\b(\d{1,2})(?::\d{2})?\b', message)
    if hour_match_24:
        hour = int(hour_match_24.group(1))
        if 0 <= hour < 24:
            if date_str:
                return predict_traffic_by_date_hour(date_str, hour)
            else:
                return predict_traffic(hour)

    return "Please mention a valid hour (e.g., 10am, 17:00) and optionally a date (e.g., 2015-07-24)."
