####  RUNNING THE MODEL
# cd documents/pmlg/wake/decoder
# python demo.py resources/HiBitLit.pmdl
from __future__ import print_function
import os
import sys

import snowboydecoder
from snowboydecoder import play_ding, play_dong
import signal

import time
import numpy as np

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

play_ding()
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print("Listening... Press Ctrl+C to exit")


detector.start(
    detected_callback=BitLit_main.generate_poem,
    interrupt_check=interrupt_callback,
    sleep_time=0.03,
)

detector.terminate()
t1 = time.time()
total = t1 - t0
print(("Time spent is about:", np.round(total), "seconds"))
