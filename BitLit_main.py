"""
Voice to text to poem to speech
Credits: Michel, Lauren, Thomas
"""

# https://pythonprogramminglanguage.com/text-to-speech/
## cmd 1::::  sudo pip install gTTS
## cmd 2::::  sudo pip install pyttsx
import sys
from gtts import gTTS  ## Packages for Text to voice
import os


import numpy as np
import re
from textblob import TextBlob
import random
import pyglet
import json
import time
import datetime
import hashlib
import tempfile
from logger import logger

from snowboydecoder import play_audio_file

import speech_recognition as sr  ## Packages for voice recognizer
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    logger.debug("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

from poem_generator import poem


# Load credentials
try:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = open("secrets/google_cloud_credentials.json").read()
except:
    print('you should place google cloud json credentials at "secrets/google_cloud_credentials.json", make sure you enable the speech recognition api')
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = None


def play_mp3(mp3_file):
    """Play mp3 file with pyglet."""
    source = pyglet.media.load(filename=mp3_file, streaming=False)
    source.play()
    time.sleep(source.duration + 2)  # must be a better way to wait untill the media has played


def cache_gtts(text, lang="en-au", cache_file=None):
    """
    Cache calls to gtts.
    
    Saves each to a temporary file

    languages 
      en-au: English (Australia)
        en-ca: English (Canada)
        en-gb: English (UK)
        en-gh: English (Ghana)
        en-ie: English (Ireland)
        en-in: English (India)
        en-ng: English (Nigeria)
        en-nz: English (New Zealand)
        en-ph: English (Philippines)
        en-tz: English (Tanzania)
        en-uk: English (UK)
        en-us: English (US)
        en-za: English (South Africa)
        en: English

    """
    if not cache_file:
        hash_filename = hashlib.md5(text.encode()).hexdigest() + '.mp3'
        cache_file = os.path.join(tempfile.gettempdir(), hash_filename)
    if not os.path.isfile(cache_file):
        tts = gTTS(text=text, lang=lang)
        tts.save(cache_file)
    return cache_file


def generate_poem():


    ############ AUDIO CONVERSION TO TEST
    play_audio_file()
    t0 = time.time()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        outfile1 = cache_gtts(text="Hi! My Name is BIT-LIT. PLEASE SPEAK. You have 20 seconds before the beep.")
        play_mp3(outfile1)

        print("SPEAK NOW-SPEAK:", source)
        audio = r.listen(source, phrase_time_limit=20)
        # speech_recognition.WaitTimeoutError
        print('Recorded audio', audio)

        outfile2 = cache_gtts(text="BEEP. THANK YOU! GIVE ME A SECOND TO READ OUT YOUR POEM")
        play_mp3(outfile2)

    t1 = time.time()
    print('listen took', t1 - t0)

    try:
        print("using google speech to text...")
        USER_INPUT = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        print("Google thinks you said: " + USER_INPUT)
    except sr.UnknownValueError as e:
        print("Could not understand audio. {}".format(e))
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    t1b = time.time()
    print('transcribe took', t1b - t1)

    # Generate poem from user seed
    text_generated = poem(USER_INPUT)
    t2 = time.time()
    print("ML POEM is:", text_generated, 'in', t2 - t1)

    # TEXT CONVERSION IN AUDIO
    # FEED POEM TO TRANSCRIBER
    tts = gTTS(text=text_generated, lang="en")
    ts = datetime.datetime.utcnow().strftime('%Y%m%d_%H-%M-%S')
    poem_mp3 = "outputs/BitLit_{}.mp3".format(ts)
    tts.save(poem_mp3)
    play_mp3(poem_mp3)

    print("BIT-LIT ENDING STATEMENT:")
    outfile = cache_gtts(text="THANK YOU! BEEP.", lang="en")
    play_mp3(outfile)

    ######
    t3 = time.time()
    print('Poem to speech took', t3 - t2)
    print("Time spent is about:", np.round(t3 - t0), "seconds")


if __name__ == "__main__":
    generate_poem()
