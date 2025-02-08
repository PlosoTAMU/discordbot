import datetime
current_time = datetime.datetime.now().time()
if not (datetime.time(5, 0) <= current_time < datetime.time(6, 0)):
    print("Current time is not between 5am and 6am. Exiting.")
    exit()
import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import openmeteo_requests
import pandas as pd
from retry_requests import retry
import requests_cache


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
# Check if the current time is between 5am and 6am




url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 30.628,
	"longitude": -96.3344,
	"hourly": "temperature_2m",
    "temperature_unit": "fahrenheit",
	"timezone": "America/Chicago",
	"forecast_days": 1,
	"models": "best_match"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Extract the temperature at 7am
temperature_at_7am = hourly_dataframe.loc[hourly_dataframe['date'].dt.hour == 12, 'temperature_2m'].values
if temperature_at_7am.size > 0:
    print(f"Temperature at 6am: {temperature_at_7am[0]}")
else:
    print("No temperature data available for 6am")
    temperature_at_7am = "None"



load_dotenv()

# Get the API token from the .env file.
TOKEN = os.getenv("TOKEN")
SERVER = os.getenv("SERVER")
CHANNEL = int(os.getenv("CHANNEL"))  # Add the channel ID to your .env file

if TOKEN is None:
    raise ValueError("No TOKEN found in environment variables")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == SERVER:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    send_message.start()

@tasks.loop(seconds=3)
async def send_message():
    channel = client.get_channel(CHANNEL)
    if channel:
        await channel.send(f"Temp @6am: {temperature_at_7am[0]:.2f}°F")
        await client.close()  # Exit after sending the message

client.run(TOKEN)
