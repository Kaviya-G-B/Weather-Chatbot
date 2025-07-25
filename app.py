from flask import Flask, request, jsonify, render_template
import requests
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
app = Flask(__name__)
API_KEY = '7d572bb48809142b288eb8bd26ab2c1a'
def handle_general_conversation(user_input):
    greetings = ["hello", "hi", "hey"]
    farewells = ["bye", "goodbye", "see you"]
    thanks = ["thank you", "thanks"]
    user_input_lower = user_input.lower()
    if any(greet in user_input_lower for greet in greetings):
        return "Hello! How can I assist you with the weather today?"
    elif any(farewell in user_input_lower for farewell in farewells):
        return "Goodbye! Have a great day!"
    elif any(thank in user_input_lower for thank in thanks):
        return "You're welcome! Happy to help."
    elif "help" in user_input_lower:
        return ("You can ask me about the weather in any city. For example, you can say: "
                "'Weather in [city name]', 'Tell me about the wind in [city name]', or 'What's the humidity in [city name]'.")
    else:
        return None
def extract_city(user_input):
    tokens = word_tokenize(user_input.lower())
    city_keywords = ['what','is','the','weather','tommorrow', 'in', 'at', 'temperature', 'humidity', 'wind', 'pressure']
    city_name = [word for word in tokens if word not in city_keywords]
    return " ".join(city_name).strip()
def get_weather_info_type(user_input):
    if "temperature" in user_input.lower():
        return "temperature"
    elif "humidity" in user_input.lower():
        return "humidity"
    elif "wind" in user_input.lower():
        return "wind"
    elif "pressure" in user_input.lower():
        return "pressure"
    else:
        return "general"
def get_weather(city, info_type="general"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        pressure = data['main']['pressure']
        if info_type == "temperature":
            return f"The temperature in {city} is {temperature}°C."
        elif info_type == "humidity":
            return f"The humidity in {city} is {humidity}%."
        elif info_type == "wind":
            return f"The wind speed in {city} is {wind_speed} meters/second."
        elif info_type == "pressure":
            return f"The atmospheric pressure in {city} is {pressure} hPa."
        else:
            return (f"The weather in {city} is {weather_description} with a temperature of {temperature}°C, "
                    f"humidity of {humidity}%, wind speed of {wind_speed} meters/second, "
                    f"and atmospheric pressure of {pressure} hPa.")
    elif response.status_code == 404:
        return "Sorry, I couldn't find the weather information for that location. Please check the city name."
    else:
        return "Sorry, there seems to be a problem fetching the weather information."
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/weather", methods=["POST"])
def weather():
    user_input = request.json.get("message")
    general_response = handle_general_conversation(user_input)
    if general_response:
        return jsonify({"response": general_response})
    info_type = get_weather_info_type(user_input)
    city = extract_city(user_input)
    if city:
        weather_info = get_weather(city, info_type)
    else:
        weather_info = "Please provide a valid city name."

    return jsonify({"response": weather_info})
if __name__ == "__main__":
    app.run(debug=True)
