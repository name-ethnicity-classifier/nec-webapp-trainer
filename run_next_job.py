import os
import time
from typing import Union
import shutil
import traceback

from logger import Logging
from utils import connect_to_db, load_json, write_json
from preprocessing import preprocess
from final_model.train_model import trainer


logger = Logging(log_file="nec.log")


def get_next_job(queue_file: str="") -> Union[int, tuple]:
    if os.stat(queue_file).st_size == 0:
        return -1

    open_jobs = load_json(queue_file)

    next_job_id = list(open_jobs.keys())[0]
    next_job = open_jobs[next_job_id]

    if next_job["ready"] == False:
        return -2

    return (next_job_id, next_job["nationalities"])


def create_job_space(job_id: str=""):
    directory = "nec_user_models/" + job_id

    if os.path.exists(directory):
        logger.warn("job directory with id [{}] does already exist! Reinitializing.".format(job_id))
        shutil.rmtree(directory)

    os.mkdir(directory)
    os.mkdir(directory + "/dataset")
    write_json(directory + "/results.json", 
        {
            "accuracy": 0.0,
            "precision-scores": [],
            "recall-scores": [],
            "f1-scores": []
        }
    )


def finish_job(queue_file: str="", job_id: str="") -> None:
    open_jobs = load_json(queue_file)

    # remove the just train job
    open_jobs.pop(job_id, None)

    # mark the next job as read if there is one
    if len(open_jobs) > 0:
        open_jobs[list(open_jobs.keys())[0]]["ready"] = True
        write_json(queue_file, open_jobs)
    else:
        open(queue_file, "w").close()


def push_job_to_db(job_id: str) -> None:
    job_directory = "nec_user_models/" + job_id
    scores = load_json(job_directory + "/results.json")

    accuracy = scores["accuracy"]
    f1_scores = scores["f1-scores"]
    score_string_list = "{" + ", ".join([str(s) for s in f1_scores]) + "}"

    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        UPDATE "model" 
        SET accuracy='{accuracy}', scores='{score_string_list}', mode=1 
        WHERE model_id='{job_id}'
        """
    )

    connection.commit()
    connection.close()


def run_next_job():
    next_job = get_next_job("job_queue.json")

    if next_job == -1:
        logger.warn("queue empty.", br=True)

    elif next_job == -2:
        logger.warn("next job not ready yet.", br=True)

    else:
        job_id, nationalities = next_job[0], next_job[1]
        logger.info("starting next job: [{}]".format(job_id), br=True)

        try:
            # create a directory to store the next job
            logger.info("creating directory for next job [{}]".format(job_id))
            create_job_space(job_id)

            # preprocess the data for the next job
            logger.info("started preprocessing job [{}].".format(job_id))
            start = time.time()
            preprocess(job_id=job_id, nationalities=nationalities, raw_dataset_path="dataset/total_names_dataset.pickle")
            logger.log("-> finished preprocessing job [{}] (took: {} seconds).".format(job_id, round(time.time() - start, 3)), show_time=False, tab=1)

            # initialize train setup
            train_job = trainer(job_id=job_id)

            # train job
            logger.info("started training job [{}].".format(job_id))
            start = time.time()
            train_job.train()
            logger.log("-> finished training job [{}] (took: {} seconds).".format(job_id, round(time.time() - start, 3)), show_time=False, tab=1)

            # evaluate job
            logger.info("starting evaluting job [{}].".format(job_id))
            start = time.time()
            train_job.test()
            logger.log("-> finished evaluting job [{}] (took: {} seconds).".format(job_id, round(time.time() - start, 3)), show_time=False, tab=1)

            # mark model as trained in the database by setting 'mode=1' and insert the scores
            push_job_to_db(job_id=job_id)
            logger.info("updated the database entry of job [{}].".format(job_id))

            # pop finished job and get next one ready
            finish_job(job_id=job_id, queue_file="job_queue.json")
            logger.info("job [{}] finished.".format(job_id))

        except Exception as err:
            logger.error("failed to run job [{}]. \n\n\terror: \n\t{}\n".format(job_id, traceback.format_exc())) # old error message: str(err).replace("\n", "\n\t")
            shutil.rmtree("nec_user_models/" + job_id)
            logger.error("job [{}] aborted, removed job directory.".format(job_id))