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

from snowboydecoder import play_ding, play_dong

import speech_recognition as sr  ## Packages for voice recognizer
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    logger.debug("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))

from poem_generator import poem


snowboy_configuration = ('./snowboy', os.listdir('hotwords'))

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
    print(mp3_file, source.duration)
    time.sleep(source.duration + 2)  # must be a better way to wait untill the media has played
    print(mp3_file, source.duration)

def cache_gtts(text, lang="en-nz", cache_file=None):
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
    logger.debug('say: %s', text)
    if not cache_file:
        hash_filename = hashlib.md5(text.encode()).hexdigest() + '.mp3'
        cache_file = os.path.join(tempfile.gettempdir(), hash_filename)
    if not os.path.isfile(cache_file):
        tts = gTTS(text=text, lang=lang)
        tts.save(cache_file)
    return cache_file

def speak(text):
    mp3_file = cache_gtts(text)
    play_mp3(mp3_file)


def generate_poem():


    ############ AUDIO CONVERSION TO TEST
    play_dong()
    t0 = time.time()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('mic', source)
        speak('please be quiet while I calibrate the microphones. I will ding when I am finished')
        time.sleep(5)
        r.pause_threshold = 5
        r.adjust_for_ambient_noise(source) 
        print('calibrate mic energy_threshold to', r.energy_threshold)
        speak('Thanks. When you want to talk to me say "Hi BitLit"')
        play_ding()

        while True:
            print('waiting for hotword "Hi BitLit" or Alexa or SnowBoy')
            audio_null = r.listen(source, snowboy_configuration=snowboy_configuration)
            play_dong()

            speak(text="Hi! My Name is BIT-LIT. PLEASE SPEAK SOME IDEAS FOR A POEM AFTER THE DING.")
            play_ding()

            print('speak now', time.time())
            try:
                audio = r.listen(source, timeout=30, phrase_time_limit=30)
            except sr.WaitTimeoutError as e:
                print('WaitTimeoutError', e)
                continue
            logger.debug('done recording %s', time.time())
            logger.info('recorded %s s', len(audio.frame_data)/audio.sample_rate)

            play_dong()
            speak(text="BEEP. THANK YOU! GIVE ME A MINUTE TO GENERATE AND READ YOUR POEM")

            t1 = time.time()
            logger.debug('listen took %s', t1 - t0)

            try:
                logger.debug("using google speech to text...")
                USER_INPUT = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
                logger.info("Google thinks you said: " + USER_INPUT)
            except sr.UnknownValueError as e:
                logger.error("Could not understand audio. {}".format(e))
                return 
            except sr.RequestError as e:
                logger.error("Could not request results; {0}".format(e))
                return

            t1b = time.time()
            logger.debug('transcribe took %s', t1b - t1)

            # Generate poem from user seed
            text_generated = poem(USER_INPUT)
            t2 = time.time()
            logger.info("ML POEM is: %s", text_generated)
            logger.debug('poem and rhyme generation took %s', t2 - t1)

            # FEED POEM TO TRANSCRIBER
            tts = gTTS(text=text_generated)
            poem_mp3 = "outputs/BitLit_poem.mp3"
            tts.save(poem_mp3)
            play_mp3(poem_mp3)

            speak(text="THANK YOU! BEEP.")

            ######
            t3 = time.time()
            logger.debug('Poem to speech took %s', t3 - t2)
            logger.debug("Total time spent is about: %s seconds", np.round(t3 - t0))


if __name__ == "__main__":
    generate_poem()
