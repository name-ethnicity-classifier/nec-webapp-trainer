
import os
import uuid
import shutil
from datetime import datetime
import psycopg2 as pg
import json
from db_config import *


def connect_to_db() -> pg.extensions.connection:
    connection = pg.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )

    return connection


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def write_json(file_path: str, content: dict) -> None:
    with open(file_path, "w") as f:
            json.dump(content, f, indent=4)



def push_standard_model(model_name: str, model_config: dict, nationalities: dict, accuracy: float, scores: list):
    model_id = "std_" + str(uuid.uuid4()).split("-")[-1]
    directory = "nec_user_models/" + model_id + "/"

    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        if os.path.exists(directory):
            logger.warn("job directory with id [{}] does already exist! Reinitializing.".format(job_id))
            shutil.rmtree(directory)

        os.mkdir(directory)
        os.mkdir(directory + "dataset/")
        write_json(directory + "results.json", 
            {
                "accuracy": accuracy,
                "precision-scores": [scores[0]],
                "recall-scores": [scores[1]],
                "f1-scores": [scores[2]]
            }
        )
        write_json(directory + "config.json", model_config)
        write_json(directory + "dataset/nationalities.json", nationalities)

        description = "-"
        f1_scores = scores[2]
        nationality_string_list = "{" + ", ".join(nationalities)[:-1] + "}"
        score_string_list = "{" + ", ".join([str(s) for s in f1_scores])[:-1] + "}"
        creation_time = str(datetime.now().strftime("%d/%m/%Y %H:%M"))
        mode = 1        # = already trained
        type_ = 1       # = standard model type

        cursor.execute(
            f"""
            INSERT INTO "model" (model_id, name, accuracy, description, nationalities, scores, creation_time, mode, type) 
            VALUES ('{model_id}', '{model_name}', '{accuracy}', '{description}', '{nationality_string_list}', '{score_string_list}', '{creation_time}', '{mode}', '{type_}')
            """
        )

        connection.commit()
        connection.close()

    except Exception as e:
        print("Couldn't push standard model '{}' to the database. Error message:\n{}".format(model_name, e))

        if os.path.exists(directory):
            shutil.rmtree(directory)


if __name__ == "__main__":
    model_name = "8_nationality_groups"

    model_config = {
        "model-name": model_name,
        "dataset-name": model_name,
        "test-size": 0.1,
        "optimizer": "Adam",
        "loss-function": "NLLLoss",
        "epochs": 5,
        "batch-size": 512,
        "cnn-parameters": [
            1,
            3,
            [
                256
            ]
        ],
        "hidden-size": 200,
        "rnn-layers": 2,
        "lr-schedule": [
            0.001,
            0.95,
            100
        ],
        "dropout-chance": 0.35,
        "embedding-size": 200,
        "augmentation": 0.0,
        "resume": False
    }

    nationalities = { "african": 0, "celtic": 1, "eastAsian": 2, "european": 3, "hispanic": 4, "muslim": 5, "nordic": 6, "southAsian": 7 }

    accuracy = 83.55
    scores = [ 
                [
                    0.78027,
                    0.77587,
                    0.92084,
                    0.79832,
                    0.89376,
                    0.76134,
                    0.91953,
                    0.85903
                ], 
               [
                    0.74547,
                    0.75585,
                    0.94174,
                    0.796,
                    0.87667,
                    0.92604,
                    0.77413,
                    0.86783
            ], 
               [
                    0.76247,
                    0.76573,
                    0.93117,
                    0.79716,
                    0.88513,
                    0.83565,
                    0.84059,
                    0.86341
            ]
        ]
    
    push_standard_model(model_name, model_config, nationalities, accuracy, scores)
