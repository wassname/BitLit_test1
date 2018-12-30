####  RUNNING THE MODEL
# Michels-MacBook-Pro:~ ShebMichel$ cd documents/pmlg/wake/decoder
# Michels-MacBook-Pro:decoder ShebMichel$ python demo.py resources/HiBitLit.pmdl
import os
import sys

import snowboydecoder
import signal

import numpy as np
import time

import BitLit_main

t0 = time.time()  ## Time counter
interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


detector = snowboydecoder.HotwordDetector(model, sensitivity=0.75)
print("Listening for hotword (Hi BitLit)... Press Ctrl+C to exit")
snowboydecoder.play_audio_file()


detector.start(
    detected_callback=BitLit_main.generate_poem,
    interrupt_check=interrupt_callback,
    sleep_time=0.03,
)

detector.terminate()
t1 = time.time()
total = t1 - t0
print(("Time spent is about:", np.round(total), "seconds"))
