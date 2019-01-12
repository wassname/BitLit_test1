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

# The handlers have to be at a root level since they are the final output
logging.basicConfig(
    level=logging.DEBUG, 
    format='[{%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        stream_handler
    ]
)

logger = logging.getLogger('bitlit')
logger.info('Logging to STDOUT and {}'.format(filename))
