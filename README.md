# INADEV_WeatherApp

I was going to initially do JavaScript for the project's back end because I typically only used Python for data focused projects, however I decided to do something new and experiment with Flask and a Python back end so that you guys can see me use multiple languages. Since JavaScript was already going to be used in the front end, I decided to make a separate branch for a Python set up, in case I wanted to go the safe route and the initial set up wouldn't be compromised.

This Weather App takes in a US zip code and gives the weather of the past hour to be displayed to the user.

The user types in the zip code and sends a POST request to the server.

![image](https://github.com/mightyxmo/INADEV_WeatherApp/assets/46232003/229ae0f7-c29d-45fd-85f0-e57312ac7221)

Once the server recieves the zip code, it accesses the OpenCage API and transforms it into a lattitude and longitude:
```
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
```

After we have the coordinate data, we then access the Open-Meteo API to take in the daily weather data:

```
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
```
Open-Meteo uses WMO weather codes for categorizing weather conditions, so readable text is needed to understand the results:

```
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
```
 
When the data is fetched by the front end, the screen will display the max and min daily temperature (in fahrenheit) and the weather condition using an icon (also a fun little background change for today's weather).

<img width="1239" alt="Screenshot 2024-01-17 at 6 32 15 PM" src="https://github.com/mightyxmo/INADEV_WeatherApp/assets/46232003/c7b73ff3-6de1-442e-bf74-1f09cae1e291">
