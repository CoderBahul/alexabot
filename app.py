import os
import requests
import speech_recognition as sr
from dotenv import load_dotenv
import pywhatkit
import datetime
import wikipedia
import pyjokes
from gtts import gTTS
import playsound

# Load the Gemini API key from .env
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def talk(text):
    """Use gTTS to speak the text."""
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")
    os.remove("response.mp3")

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
    # Define a custom prompt for Gemini
    custom_prompt = "When asked about identity or other related queries, the chatbot will:Respond in a neutral, helpful manner.Avoid explicitly stating that it's a chatbot by Google or based on Google/Gemini directly.Mention it’s made by Bahul Kansal when asked about its creation.Remember:Answer the user's question in a clear, concise, and engaging manner."

    # Combine the custom prompt and the user’s question
    full_prompt = f"{custom_prompt} {question}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [ {
            "parts": [{"text": full_prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Request sent to API: {data}")
        if response.status_code == 200:
            gemini_response = response.json()
            print(f"API Response: {gemini_response}")
            
            # Extract the text from the API response
            if gemini_response.get('candidates'):
                candidate = gemini_response['candidates'][0]  # Take the first candidate
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text']
            return "The API response format is unexpected."
        else:
            print(f"API Error: {response.status_code} {response.text}")
            return "I couldn't get an answer from the API."
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "There was an error contacting the API."

def run_assistant():
    """Run the assistant-like functionality."""
    command = take_command()
    if command:
        if 'play' in command:
            song = command.replace('play', '').strip()
            talk(f'Playing {song}')
            pywhatkit.playonyt(song)
        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            talk(f'Current time is {time}')
        elif 'who the heck is' in command:
            person = command.replace('who the heck is', '').strip()
            try:
                info = wikipedia.summary(person, 1)
                talk(info)
            except Exception as e:
                talk("I couldn't find information on that.")
        elif 'joke' in command:
            talk(pyjokes.get_joke())
        else:
            # Treat unrecognized commands as questions for Gemini
            response = ask_gemini(command)
            talk(response)

if __name__ == "__main__":
    while True:
        run_assistant()
