from flask import Flask, render_template, request, jsonify
from opencage.geocoder import OpenCageGeocode
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

opencage_api_key = os.getenv('OPENCAGE_API')
geocoder = OpenCageGeocode(opencage_api_key)

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
            "daily": "temperature_2m_max,temperature_2m_min,weather_code",
            "temperature_unit": "fahrenheit",
            "timezone": "EST"
        }
        response = requests.get(url, params=params)
        data = response.json()

        daily_data = data.get('daily', {})
        max_temp = daily_data.get('temperature_2m_max', [])
        min_temp = daily_data.get('temperature_2m_min', [])
        weather_code = daily_data.get('weather_code', [])

        logging.info(f"{data}")

        if max_temp and min_temp and weather_code:
            weather_forecast = []
            for i in range(len(max_temp)):
                daily_condition = get_weather_condition(weather_code[i])
                weather_forecast.append({
                    "date": daily_data['time'][i],
                    "max_temperature": max_temp[i],
                    "min_temperature": min_temp[i],
                    "condition": daily_condition
                })
            
            return weather_forecast
        else:
            logging.warning("Weather data not available.")
            return {"error": "Weather data not available."}

    except Exception as e:
        logging.error(f"Error occurred while fetching the weather data: {e}")
        return {"error": f"Error occurred while fetching the weather data: {e}"}

def get_weather_condition(code):
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
        location = geocoder.geocode(zip_code, countrycode='us')
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
