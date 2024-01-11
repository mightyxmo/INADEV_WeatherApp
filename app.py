from flask import Flask, render_template, request, jsonify
from opencage.geocoder import OpenCageGeocode

import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lat/Long API
opencage_api_key = os.getenv('OPENCAGE_API')
geocoder = OpenCageGeocode(opencage_api_key)

# Weather API Setup
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getWeather', methods=['POST'])
def get_weather():
    zip_code = request.form['zipcode']
    lat_n_lng = lat_lng_converter(zip_code)

    if lat_n_lng:
        weather_data = fetch_weather_data(lat_n_lng["lat"], lat_n_lng["lng"])
        return jsonify(weather_data)
    else:
        return jsonify({"error": "No results found for the entered ZIP Code."}), 404
    
def fetch_weather_data(lat, lng):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "temperature_2m",
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)

        if responses:
            response = responses[0]
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()[0]
            hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()[0]
            
            weather = weather_condition(hourly_weather_code)

            return {
                "temperature": hourly_temperature_2m,
                "condition": weather
            }
        else:
            logging.warning("Weather data not available.")
            return {"error": "Weather data not available."}

    except Exception as e:
        logging.error(f"Error occurred while fetching the weather data: {e}")
        return {"error": f"Error occurred while fetching the weather data: {e}"}

def weather_condition(code):
      if code == 0:
          return "clear-sky"
      elif 1 <= code <= 3:
          return "partly-cloudy"
      elif code in [45, 48]:
          return "fog"
      elif 51 <= code <= 55 or 56 <= code <= 57:
          return "drizzle"
      elif 61 <= code <= 65 or 66 <= code <= 67:
          return "rain"
      elif 71 <= code <= 75 or code == 77:
          return "snow"
      elif 80 <= code <= 82 or 85 <= code <= 86:
          return "showers"
      elif 95 <= code <= 99:
          return "thunderstorm"
      else:
          return "overcast"

def lat_lng_converter(zip_code):
    try:
        location = geocoder.geocode(zip_code)
        if location:
            logging.info(f"Geocoding was successful for ZIP code: {zip_code}")
            return {
                "lat": location[0]['geometry']['lat'],
                "lng": location[0]['geometry']['lng']
            }
        else:
            logging.warning(f"No coordinates were found for the ZIP code: {zip_code}")
            return None
    except Exception as e:
        logging.error(f"Error occurred during the geocoding of ZIP code - {zip_code}: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
