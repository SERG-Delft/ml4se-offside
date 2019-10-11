import os

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import Code2VecCustomModel
from models.CustomModel import CustomModel

from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score



def main() -> None:
    X_test, Y_test = load_data("data/test_")


    config = Config(set_defaults=True)
    code2Vec = Code2VecCustomModel(config)


    model = CustomModel(code2Vec)
    model.load_weights("resources/models/custom3/model")
    metrics = ['binary_accuracy']
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=metrics)

    batch_size = 1024 * 4

    test_loss, accuracy = model.evaluate(X_test, Y_test, batch_size=batch_size)

    Y_pred = model.predict(X_test, batch_size=batch_size)
    #TODO fine tune based on val
    Y_pred = np.where(Y_pred >= 0.5, np.ones_like(Y_pred), np.zeros_like(Y_pred))

    print("confusion_matrix")
    print(confusion_matrix(Y_test, Y_pred))

    print("test_loss")
    print(test_loss)

    print("accuracy")
    print(accuracy)

    print("f1_score")
    print(f1_score(Y_test, Y_pred))

    print("precision_score")
    print(precision_score(Y_test, Y_pred))

    print("recall_score")
    print(recall_score(Y_test, Y_pred))




def load_data(prefix):
    Y = np.load(prefix + "Y.npy")
    path_source_token_idxs = np.load(prefix + "path_source_token_idxs.npy")
    path_idxs = np.load(prefix + "path_idxs.npy")
    path_target_token_idxs = np.load(prefix + "path_target_token_idxs.npy")
    context_valid_masks = np.load(prefix + "context_valid_masks.npy")
    X = [path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks]

    return X, Y

if __name__ == '__main__':
    main()