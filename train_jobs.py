from gather_jobs import fetch_jobs
from run_next_job import run_next_job
from logger import Logging
import traceback
import time


logger = Logging(log_file="nec.log")
logger.log("starting train daemon.", tag="DAEMON")

JOBS_TO_TRAIN = 5
SECONDS_TO_WAIT = 10800

while True:
    try:
        logger.log("fetching new jobs.", tag="DAEMON")
        fetch_jobs()
        time.sleep(10)

        logger.log("training next {} jobs.".format(JOBS_TO_TRAIN), tag="DAEMON")
        for _ in range(JOBS_TO_TRAIN):
            run_next_job()
            time.sleep(10)

        logger.log("fetching next jobs in 3 hours.", tag="DAEMON")
        time.sleep(SECONDS_TO_WAIT)

    except Exception as err:
        logger.error("daemon failed. \n\n\terror: \n\t{}\n".format(traceback.format_exc()))


logger.log("stopping train daemon.", tag="DAEMON")
