import logging
import datetime

def log_info(msg):
    timestamp = "[" +  datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.%f') + "]"
    logging.info(timestamp + " " + msg)
    print("INFO:", timestamp, msg)

def log_warn(msg):
    timestamp = "[" + datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.%f') + "]"
    logging.warning(timestamp + " " + msg)
    print("WARN:", timestamp, msg)

def log_error(msg):
    timestamp = "[" + datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.%f') + "]"
    logging.error(timestamp + " " + msg)
    print("ERROR:", timestamp, msg)
