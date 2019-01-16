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
import random
import pyglet
import json
import logging
import time
import datetime
import hashlib
import tempfile
import glob
from logger import logger
import argparse
from snowboydecoder import play_ding

## Packages for voice recognizer
import speech_recognition as sr  
from poem_generator import poem

DEBUG = False
lang="en-nz"
snowboy_configuration = ('./snowboy', glob.glob('hotwords/*'))

# Load credentials
try:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = open("secrets/google_cloud_credentials.json").read()
except:
    print('you should place google cloud json credentials at "secrets/google_cloud_credentials.json", make sure you enable the speech recognition api')
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = None


def play_ding():
    speak('ding')

def play_mp3(mp3_file):
    """Play mp3 file with pyglet."""
    source = pyglet.media.load(filename=mp3_file, streaming=False)
    logger.debug('playing %s second file', source.duration)
    source.play()
    time.sleep(source.duration + 0.5)  # must be a better way to wait untill the media has played

def cache_gtts(text, lang=lang, cache_file=None):
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
    logger.info('bitlit says: %s', text)
    if not cache_file:
        hash_filename = hashlib.md5(text.encode()).hexdigest() + lang + '.mp3'
        cache_file = os.path.join(tempfile.gettempdir(), hash_filename)
    if not os.path.isfile(cache_file):
        tts = gTTS(text=text, lang=lang)
        tts.save(cache_file)
    return cache_file

def speak(text, lang=lang, cache_file=None):
    mp3_file = cache_gtts(text, lang=lang, cache_file=cache_file)
    play_mp3(mp3_file)

def record_audio(audio, output_file, play=False):
    # write audio to a WAV file for debugging
    with open(output_file, "wb") as f:
        f.write(audio.get_flac_data())
    logger.info('recorded %s s. Saved as %s', len(audio.frame_data)/audio.sample_rate, output_file)
    if play:
        speak("DEBUG: I recorded the following")
        play_mp3(output_file)


def generate_poem(args):

    if DEBUG:
        speak("I'm in debug mode")

    ############ AUDIO CONVERSION TO TEST
    play_ding()
    t0 = time.time()
    r = sr.Recognizer()

    if args.pre_calib:
        # This section could use work. But since I'm frequently initialising the mic, 
        # I don't think it has time to dynamically adapt, so I'm doing a specific auto calibrate here first
        speak("Hi I'm bit-lit. Silence puny Humans. I must calibrate the microphone. I will make a dong sound when I am finished")
        time.sleep(1)
        r.dynamic_energy_threshold = False
        with sr.Microphone() as source:
            logger.debug('microphone source is %s', source)
            print(dir(source))
            r.adjust_for_ambient_noise(source, duration=4) 
        # https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instanceenergy_threshold--300---type-float
        logger.info('calibrate mic energy_threshold to %s. This should be between 150 and 3500 for speaking. If its higher you should turn down your mic', r.energy_threshold)
        r.energy_threshold = max(r.energy_threshold, 150)
        r.energy_threshold = min(r.energy_threshold, 3500)
        logger.info('maxmin mic energy_threshold to %s', r.energy_threshold)
        play_ding()
    elif args.energy_threshold:
        r.dynamic_energy_threshold = False
        r.energy_threshold = args.energy_threshold
        logger.info("setting constant energy_threshold to %s", args.energy_threshold)
    else:
        logger.info("using dynamic background energy_threshold calibration")

    while True:
        try:
            if not args.woke:
                speak('When you want me to make a poem summon me with "Hi BitLit" or "computer"')
                logger.info('mic energy_threshold to %s', r.energy_threshold)
                time.sleep(1)
                with sr.Microphone() as source:
                    time.sleep(1)
                    play_ding()
                    audio_hotword = r.listen(source, snowboy_configuration=snowboy_configuration)
                if DEBUG:
                    record_audio(audio_hotword, "outputs/hotword-results.flac", play=DEBUG)
                play_ding()

            speak(text="Hi Humans! My Name is BIT-LIT. Inspire me with the first line of a poem: You may speek for 10 seconds after the bing.")
            
            play_ding()
            with sr.Microphone() as source:
                audio = r.record(source, duration=10)
            play_ding()

            # write audio to a WAV file for debugging
            if DEBUG:
                record_audio(audio, "outputs/record-results.flac", play=DEBUG)

            logger.debug('done recording %s', time.time())
            logger.info('recorded %s s', len(audio.frame_data)/audio.sample_rate)

            # Text to speech
            speak(text="Thank you! Give me a minute to generate and reed your poem")

            t1 = time.time()
            logger.debug('listen took %s', t1 - t0)

            try:
                logger.debug("using google speech to text...")
                USER_INPUT = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
                logger.info("Google thinks you said: " + USER_INPUT)
            except sr.UnknownValueError as e:
                logger.error("Could not understand audio. {}".format(e))
                speak("I could not understand that audio")
                continue 
            except sr.RequestError as e:
                logger.error("Could not request results; {0}".format(e))
                speak("I'm sorry I could not communicate with the speech to text the internet'")
                continue

            t1b = time.time()
            logger.debug('transcribe took %s', t1b - t1)

            speak('I think you said %s' % USER_INPUT)

            # Generate poem from user seed
            text_generated, rhymes = poem(USER_INPUT)
            t2 = time.time()
            logger.info("rhymes: %s", rhymes)
            logger.info("ML POEM is: %s", text_generated)
            logger.debug('poem and rhyme generation took %s', t2 - t1)

            if DEBUG:
                speak('DEBUG: your rhymes are: '+ ' '.join(rhymes))

            # FEED POEM TO TRANSCRIBER
            cache_file = "outputs/BitLit_last_poem.mp3"
            tts = gTTS(text=text_generated, lang=lang)
            tts.save(cache_file)
            play_mp3(cache_file)

            if random.random()>0.90:
                speak(text="THANK YOU!")
            else:
                speak(text="THANK YOU PUNY HUMANS.")

            ######
            t3 = time.time()
            logger.debug('Poem to speech took %s', t3 - t2)
            logger.debug("Total time spent is about: %s seconds", np.round(t3 - t0))

            play_ding()
        except KeyboardInterrupt as e:
            raise 
        except Exception as e:
            speak("Oh no I had an error I will try again in one minute")
            speak("The error was %s" % e)
            time.sleep(60)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="increase output verbosity",
                    action="store_true")
    parser.add_argument("-e", "--energy-threshold", help="Instead of using dynamic or pre calibration, set an integer for the level of background noise. Ideally between 40-4000.",  default=None)
    parser.add_argument("-p", "--pre-calib", help="Pre calibration instead of the default deynamic calibration",  action='store_true')
    parser.add_argument("-w", "--woke", help="Woke youself. In this mode bitlit will be so woke it wont need a wokeword.",  action='store_true')
    args = parser.parse_args()

    DEBUG = args.debug
    if DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)
        for handler in logging.getLogger().handlers:
            handler.setLevel(logging.DEBUG)

        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            logger.debug("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))


    generate_poem(args)
