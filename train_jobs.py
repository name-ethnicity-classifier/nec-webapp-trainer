import traceback
import time
from dotenv import load_dotenv
from gather_jobs import fetch_jobs
from run_next_job import run_next_job
from logger import Logging
import os

load_dotenv()


logger = Logging(log_file="nec.log")
logger.log("starting train daemon.", tag="DAEMON")

JOBS_TO_TRAIN = os.getenv("JOBS_TO_TRAIN")
TIME_BETWEEN_JOBS = os.getenv("TIME_BETWEEN_JOBS")
TRAIN_PAUSE_TIME = os.getenv("TRAIN_PAUSE_TIME")


while True:
    try:
        logger.log("fetching new jobs.", tag="DAEMON")
        fetch_jobs()
        time.sleep(10)

        logger.log("training next {} jobs.".format(JOBS_TO_TRAIN), tag="DAEMON")
        for _ in range(JOBS_TO_TRAIN):
            run_next_job()
            time.sleep(TIME_BETWEEN_JOBS)

        logger.log("fetching next jobs in {} seconds.".format(TRAIN_PAUSE_TIME), tag="DAEMON")
        time.sleep(TRAIN_PAUSE_TIME)

    except Exception as err:
        logger.error("daemon failed. \n\n\terror: \n\t{}\n".format(traceback.format_exc()))


logger.log("stopping train daemon.", tag="DAEMON")
