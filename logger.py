"""
from https://gist.github.com/wassname/d17325f36c36fa663dd7de3c09a55e74
Setup simple logging in python. This logs info message to stdout and debug messages to file.
Sure it's long but this is as simple as I could make it for this outcome.
Note: We must set the root logger at DEBUG level, since it must be higher than it's children to pass them on.
Then set filehandler at debug and stream handler at info.
"""
import logging
import sys
import os
import datetime
import tempfile

# To use differen't log level for file and console
timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H-%M-%S')
filename ='./outputs/bitlit_log_{}.log'.format(timestamp)
formatter = logging.Formatter('[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

file_handler = logging.FileHandler(filename=filename)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

import datadog
from datadog_logger import DatadogLogHandler


json_formatter = logging.Formatter('{ "loggerName":"%(name)s", "asciTime":"%(asctime)s", "fileName":"%(filename)s", "logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s", "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}')

datadog.initialize(api_key="4bc53c4318964cd97489b3c1c5401c50", app_key="c07cf0fb03e363228c67f695cc957422a2763d65")

datadog_handler = DatadogLogHandler(level=logging.INFO)


# The handlers have to be at a root level since they are the final output
logging.basicConfig(
    level=logging.DEBUG, 
    format='[{%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        stream_handler,
    ]
)

logger = logging.getLogger('bitlit')
logger.addHandler(datadog_handler)
logger.info('Logging to STDOUT and {}'.format(filename))
