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

After we have the coordinate data, we then access the Open-Meteo API to take in the weather data:

```
def fetch_weather_data(lat, lng):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "temperature_2m,weather_code",
            "temperature_unit": "fahrenheit",
            "timezone": "EST"
        }
        response = requests.get(url, params=params)
        data = response.json()
        logging.info(f"data: {data}")

        hourly_data = data.get('hourly', {})
        temperatures = hourly_data.get('temperature_2m', [])
        weather_codes = hourly_data.get('weather_code', [])

        if temperatures and weather_codes:
            temperature = temperatures[0]
            weather_code = weather_codes[0]
            weather_condition = get_weather_condition(weather_code)

            return {
                "temperature": temperature,
                "condition": weather_condition
            }
        else:
            logging.warning("Weather data not available.")
            return {"error": "Weather data not available."}

    except Exception as e:
        logging.error(f"Error occurred while fetching the weather data: {e}")
        return {"error": f"Error occurred while fetching the weather data: {e}"}
```
When the data is fetched by the front end, the screen will display the temperature (in fahrenheit) and the weather condition (with a fun little background change).

![image](https://github.com/mightyxmo/INADEV_WeatherApp/assets/46232003/bd9dc079-4cf5-440e-96db-ac13fd2c7e68)
