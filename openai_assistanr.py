import streamlit as st
import openai
import json
import time
import os
import sounddevice as sd
import soundfile as sf
import io
from scipy.io.wavfile import write
import base64
import requests
import sounddevice as sd
from scipy.io.wavfile import write
import sounddevice as sd
from scipy.io.wavfile import write
import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
from time import sleep




os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

client = openai.OpenAI()


# Description: "Create a new Assistant"

def create_assistant(name, description, instructions, tools=[], model="gpt-3.5-turbo-1106"):
    assistant = client.beta.assistants.create(
    name=name,
    description=description,
    instructions=instructions,
    tools=tools,
    model=model
    )
    return assistant

# Description: "Get an already made assistant"

def get_assistant(assistant_id):
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

# Description: "Start a new chat with a user"

def start_new_chat():
    empty_thread = client.beta.threads.create()
    return empty_thread

# Description: "Get thread by id"

def get_thread(account):
    if account.thread_id:
        return account.thread_id
    else:
        id = start_new_chat().id
        account.thread_id = id
        account.save()
        return id
    

def get_chat(thread_id):
    thread = client.beta.threads.retrieve(thread_id)
    return thread

# Description: "Add a message to a chat/Thread" 

def add_message(thread, content):
    thread_message = client.beta.threads.messages.create(
    thread_id = thread.id,
    role="user",
    content=content,
    )
    return thread_message

# Description: "Get the previous messages in a chat/Thread"
def get_messages_in_chat(client, thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages

# Description: "Run the thread with the assistant"
def run_chat(thread, assistant):
    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    )
    return run

#get status of the run

def get_run_status(run):
    status = client.beta.threads.runs.retrieve(
    thread_id=run.thread_id,
    run_id=run.id,
    )
    print(status)
    return status


#retive the messages from message id
def get_message(message_id, thread):
    #message = client.beta.threads.messages.retrieve(message_id=message_id,thread_id=thread.id)
    thread_messages = client.beta.threads.messages.list(thread.id,limit=10)
    #return 1st message
    print(thread_messages.data[0].content[0].text.value)
    message = thread_messages.data[0].content[0].text.value
    return message



def text_to_speech(text):
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=text,
    )
    return response



def get_speech(audio_file):

    transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    )

    return transcript


def get_assistant_response(assistant_id, thread_id, message_content):
    assistant = get_assistant(assistant_id)
    thread = get_chat(thread_id)
    message = add_message(thread, message_content)
    run = run_chat(thread, assistant)
    status = get_run_status(run)
    while status.status != "completed":
        time.sleep(5)
        print("waiting for response")
        status = get_run_status(run)
    message = get_message(message.id,thread)
    return message




assistant_id = '' #assistant_id
thread_id = '' #thread_id

recording_started = False
recording_stopped = False

def start_recording():
    recording_started = True
    recording_stopped = False
    fs = 44100
    seconds = 10
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write('output.wav', fs, myrecording)
    st.write("Recording started.")
    recording_started = False
    recording_stopped = True
    sd.stop()
    st.write("Recording stopped.")
    try:
        audio_file = open('output.wav', 'rb')
        print(audio_file)
    except:
        print("No audio file")
        audio_file = None

    print(recording_started, recording_stopped)
    if audio_file is not None and  recording_stopped == True:
        transcript_text = get_speech(audio_file)
        transcript_text = transcript_text.text
        st.write(f"User: {transcript_text}")
        response = get_assistant_response(assistant_id, thread_id, transcript_text)
        #text_to_speech(response)
        speaking = text_to_speech(response)
        speaking.stream_to_file("output.mp3")
        st.audio("output.mp3")
        audio_file = None
        recording_stopped = False

        st.write(f"Assistant: {response}")
    

def main():
    st.title("Voice and Text Chat")


    recording_started = False
    recording_stopped = False

    # Text chat
    user_input = st.text_input("User: ")

    if st.button("Send"):
        #create a thread
        response = get_assistant_response(assistant_id, thread_id, user_input)
        st.write(f"Assistant: {response}")

    # Voice chat
    audio_file = st.file_uploader("Upload an audio file")

    
    #start recording
    st.button("Start Recording", key="start", on_click=start_recording)

        
if __name__ == "__main__":
    main()
