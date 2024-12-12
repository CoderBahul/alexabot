import os
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import pydub.playback
from pydub import AudioSegment
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Set ffmpeg path explicitly if necessary
AudioSegment.ffmpeg = "E:/Gemini/ffmpeg/bin/ffmpeg.exe"

# Load environment variables
load_dotenv()

# Initialize Google Gemini model (using ChatGoogleGenerativeAI)
api_key = os.getenv("GEMINI_API_KEY")
chat_model = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-pro", temperature=0.7)

# Helper Functions
def text_to_speech(text):
    """Convert text to speech and play it instantly."""
    if not text.strip():
        return
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        audio = AudioSegment.from_file(temp_audio.name)
        fast_audio = audio.speedup(playback_speed=1.3)
        pydub.playback.play(fast_audio)

def speech_to_text():
    """Convert speech to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            return query
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand. Please try again."
        except sr.RequestError:
            return "Error with the speech recognition service."

def detect_wakeword():
    """Continuously listen for the wake word 'UP'."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                query = recognizer.recognize_google(audio)
                if "UP" in query.upper():
                    return True
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                st.error("Microphone or recognition service error.")
                break
    return False

def general_chatbot_response(query):
    """Generate intelligent response using Gemini (ChatGoogleGenerativeAI)."""
    try:
        # Log the query being sent
        print(f"Sending query to Gemini: {query}")
        
        # Send the query to the model
        response = chat_model.predict(query)
        
        # Log the raw response to check its structure
        print(f"Raw response from Gemini: {response}")
        
        return response
    except Exception as e:
        return f"Sorry, an error occurred: {e}"

# Main App
def main():
    st.set_page_config(page_title="Alexa-like Bot", layout="wide")
    st.title("Alexa-like Bot")

    # Select bot type
    bot_type = st.sidebar.radio(
        "Choose Bot",
        ["Alexa-like Bot"],
        index=0
    )

    if bot_type == "Alexa-like Bot":
        st.subheader("Alexa-like Bot: Always Listening")
        while True:
            if detect_wakeword():
                st.success("Wake word detected: 'UP'")
                st.info("Listening for your query...")
                voice_query = speech_to_text()
                if voice_query:
                    with st.spinner("Thinking..."):
                        answer = general_chatbot_response(voice_query)
                        st.write("Response:", answer)
                        text_to_speech(answer)

if __name__ == "__main__":
    main()
