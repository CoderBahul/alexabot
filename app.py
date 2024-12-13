import os
import requests
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import pywhatkit
import datetime
import wikipedia
import pyjokes
from flask import Flask, jsonify, request

# Load the Gemini API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Flask app
app = Flask(__name__)

# Initialize TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(text):
    """Speak the text using text-to-speech engine."""
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listen for a command using the microphone."""
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener = sr.Recognizer()
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'hps' in command:
                command = command.replace('hps', '').strip()
                print(f"Command: {command}")
                return command
    except Exception as e:
        print(f"Error: {e}")
        return None

def ask_gemini(question):
    """Send a question to the Gemini API and return the response with a custom prompt."""
    custom_prompt = "When asked about identity or other related queries, the chatbot will: Respond in a neutral, helpful manner. Avoid explicitly stating that it's a chatbot by Google or based on Google/Gemini directly. Mention it’s made by Bahul Kansal when asked about its creation. Answer the user's question in a clear, concise, and engaging manner."

    full_prompt = f"{custom_prompt} {question}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Request sent to API: {data}")
        if response.status_code == 200:
            gemini_response = response.json()
            print(f"API Response: {gemini_response}")
            if gemini_response.get('candidates'):
                candidate = gemini_response['candidates'][0]  
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text']
            return "The API response format is unexpected."
        else:
            print(f"API Error: {response.status_code} {response.text}")
            return "I couldn't get an answer from the API."
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "There was an error contacting the API."

@app.route('/run-alexa', methods=['GET'])
def run_alexa():
    """Run the Alexa-like assistant."""
    command = take_command()
    if command:
        response = ""
        if 'play' in command:
            song = command.replace('play', '').strip()
            response = f'Playing {song}'
            pywhatkit.playonyt(song)
        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            response = f'Current time is {time}'
        elif 'who the heck is' in command:
            person = command.replace('who the heck is', '').strip()
            try:
                info = wikipedia.summary(person, 1)
                response = info
            except Exception as e:
                response = "I couldn't find information on that."
        elif 'joke' in command:
            response = pyjokes.get_joke()
        else:
            # Treat unrecognized commands as questions for Gemini
            response = ask_gemini(command)
        
        # Return response as JSON
        return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
