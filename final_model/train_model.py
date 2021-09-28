
from final_model.train_setup import TrainSetup
import time


model_config = {
    "model-name": "-",

    "dataset-name": "-",
    
    # percentage of the test and validation set
    "test-size": 0.05,

    # name of the optimizer (changing "optimizer" in this config won't make a difference, the optimizer has to be changed in the "train_setup.py" by hand)
    "optimizer": "Adam",

    # name of the loss function (changing "loss-function" in this config won't make a difference, the loss function has to be changed in the "train_setup.py" by hand)
    "loss-function": "NLLLoss",

    # amount of epochs
    "epochs": 18,

    # batch size
    "batch-size": 512,

    # initial learning rate
    "init-learning-rate": 0.001,

    # cnn parameters (idx 0: amount of layers, idx 1: kernel size, idx 2: list of feature map dimensions)
    "cnn-parameters": [1, 3, [64]],
    
    # hidden size of the LSTM
    "hidden-size": 200, 

    # amount of layers inside the LSTM
    "rnn-layers": 2,

    # learning-rate parameters (idx 0: current lr, idx 1: decay rate, idx 2: decay intervall in iterations), 
    "lr-schedule": [0.001, 0.95, 200],

    # dropout change of the LSTM output
    "dropout-chance": 0.2,

    # embedding size ("embedding-size" x 1)
    "embedding-size": 200,

    # augmentation chance (name part switching will slow down the training process when set high)
    "augmentation": 0.2,

    # when resume is true: replace the first element of "lr-schedule" (the current lr) with the learning rate of the last checkpoint
    "resume": False
}



def trainer(job_id: str=""):
    model_config["model-name"] = job_id
    model_config["dataset-name"] = job_id

    return TrainSetup(model_config, silent=True)


# train_setup.train()
# train_setup.test(print_amount=None, plot_confusion_matrix=False, plot_scores=False)