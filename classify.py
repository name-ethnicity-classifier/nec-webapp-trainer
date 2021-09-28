
import torch
import torch.utils.data
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence
import argparse
import numpy as np
import json
import pandas as  pd
import string
from typing import Union
import os
import time
import traceback
from utils import load_json, write_json

import sys
sys.path.insert(1, "/final_model/")

from final_model.model import ConvLSTM as Model


def preprocess_names(names: list=[str], batch_size: int=128) -> torch.tensor:
    """ create a pytorch-usable input-batch from a list of string-names
    
    :param list names: list of names (strings)
    :param int batch_size: batch-size for the forward pass
    :return torch.tensor: preprocessed names (to tensors, padded, encoded)
    """

    sample_batch = []
    for name in names:

        # create index-representation from string name, ie: "joe" -> [10, 15, 5], indices go from 1 ("a") to 28 ("-")
        alphabet = list(string.ascii_lowercase.strip()) + [" ", "-"]
        int_name = []
        for char in name:
            int_name.append(alphabet.index(char.lower()) + 1)
        
        name = torch.tensor(int_name)
        sample_batch.append(name)

    padded_batch = pad_sequence(sample_batch, batch_first=True)

    padded_to = list(padded_batch.size())[1]
    padded_batch = padded_batch.reshape(len(sample_batch), padded_to, 1).to(device=device)

    if padded_batch.shape[0] == 1 or batch_size == padded_batch.shape[0]:
        padded_batch = padded_batch.unsqueeze(0)
    else:
        padded_batch = torch.split(padded_batch, batch_size)

    return padded_batch
    

def predict(input_batch: torch.tensor, model_config: dict, device: torch.device) -> str:
    """ load model and predict preprocessed name

    :param torch.tensor input_batch: input-batch
    :param str model_path: path to saved model-paramters
    :param dict classes: a dictionary containing all countries with their class-number
    :return str: predicted ethnicities
    """

    # prepare model (map model-file content from gpu to cpu if necessary)
    model = Model(
                class_amount=model_config["amount-classes"], 
                embedding_size=model_config["embedding-size"],
                hidden_size=model_config["hidden-size"],
                layers=model_config["rnn-layers"],
                kernel_size=model_config["cnn-parameters"][1],
                channels=model_config["cnn-parameters"][2]
            ).to(device=device)


    model_path = model_config["model-file"]

    if device != "cuda:0":
        model.load_state_dict(torch.load(model_path, map_location={"cuda:0": "cpu"}))
    else:
        model.load_state_dict(torch.load(model_path))

    model = model.eval()

    # classify names    
    total_predicted_ethncitities = []

    for batch in input_batch:
        predictions = model(batch.float())

        # convert numerics to country name
        predicted_ethnicites = []
        for idx in range(len(predictions)):
            prediction = predictions.cpu().detach().numpy()[idx]
            prediction_idx = list(prediction).index(max(prediction))
            ethnicity = list(classes.keys())[list(classes.values()).index(prediction_idx)]
            predicted_ethnicites.append(ethnicity)

        total_predicted_ethncitities += predicted_ethnicites

    return total_predicted_ethncitities
    

if __name__ == "__main__":
    # read flag arguments
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--id", required=True)
        parser.add_argument("-f", "--fileName", required=True)
        args = vars(parser.parse_args())

        # get input and output path

        model_id = args["id"]

        csv_in_path = "nec-model/tmp-csv/" + args["fileName"].split(".")[0] + "_in_" + model_id + ".csv"
        csv_out_path = "src/data/output-files/" + args["fileName"].split(".")[0] + "_out_" + model_id + ".csv" 

        # get the train configurations
        model_config = load_json("nec-model/nec_user_models/" + model_id + "/config.json")
        classes = load_json("nec-model/nec_user_models/" + model_id + "/dataset/nationalities.json")
        model_file = "nec-model/nec_user_models/" + model_id + "/model.pt"
        names = pd.read_csv(csv_in_path)["names"].tolist()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        batch_size = 32

        # preprocess inputs
        input_batch = preprocess_names(names=names, batch_size=batch_size)

        model_config = {
            "model-file": model_file,
            "amount-classes": len(classes),
            "embedding-size": model_config["embedding-size"],
            "hidden-size": model_config["hidden-size"],
            "rnn-layers": model_config["rnn-layers"],
            "cnn-parameters": model_config["cnn-parameters"]
        }

        # predict ethnicities
        ethnicities = predict(input_batch, model_config, device)

        df = pd.DataFrame()
        df["names"] = names
        df["ethnicities"] = ethnicities

        open(csv_out_path, "w+").close()
        df.to_csv(csv_out_path, index=False)

        # remove temporary csv file
        os.remove(csv_in_path)

        print("\n-> classified names using the model with id {}.".format(model_id))
    except Exception as e:
        print(traceback.format_exc())



    




