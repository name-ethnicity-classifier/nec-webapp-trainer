
import os
import uuid
import shutil
from datetime import datetime
from run_next_job import create_job_space
from utils import connect_to_db, load_json, write_json


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
    model_name = "20_most_occuring_nationalities"

    model_config = {
        "model-name": model_name,
        "dataset-name": model_name,
        "test-size": 0.2,
        "optimizer": "Adam",
        "loss-function": "NLLLoss",
        "epochs": 4,
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
        "dropout-chance": 0.3,
        "embedding-size": 200,
        "augmentation": 0.2,
        "resume": False
    }

    nationalities = {
        "british": 0,
        "norwegian": 1,
        "indian": 2,
        "irish": 3,
        "spanish": 4,
        "american": 5,
        "german": 6,
        "polish": 7,
        "bulgarian": 8,
        "turkish": 9,
        "pakistani": 10,
        "italian": 11,
        "romanian": 12,
        "french": 13,
        "australian": 14,
        "chinese": 15,
        "swedish": 16,
        "nigerian": 17,
        "dutch": 18,
        "filipino": 19
    }

    accuracy = 74.99
    scores = [ [0.36707, 0.83376, 0.75889, 0.6412, 0.79855, 0.45995, 0.70518, 0.92881, 0.94288, 0.89543, 0.77127, 0.83323, 0.91462, 0.69721, 0.32094, 0.93804, 0.70131, 0.82266, 0.73316, 0.77938], 
               [0.37027, 0.74202, 0.87621, 0.68428, 0.78559, 0.37891, 0.6915, 0.94768, 0.95234, 0.94977, 0.93293, 0.78988, 0.92743, 0.73524, 0.24303, 0.9776, 0.67293, 0.91383, 0.63855, 0.81792], 
               [0.36866, 0.78522, 0.81334, 0.66204, 0.79202, 0.41552, 0.69827, 0.93815, 0.94759, 0.9218, 0.84443, 0.81098, 0.92098, 0.71572, 0.2766, 0.95741, 0.68683, 0.86585, 0.68259, 0.79819]
             ]
    
    push_standard_model(model_name, model_config, nationalities, accuracy, scores)
