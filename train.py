import argparse
import os
import time

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import Code2VecCustomModel
from models.CustomModel import CustomModel

parser = argparse.ArgumentParser()
parser.add_argument(
    "-t", "--trainset", default="data/train_",
    help="path to the train data set of format: <path>/<prefix>. It auto reads in all sub components at that path"
)
parser.add_argument(
    "-v", "--valset", default="data/val_",
    help="path to the val data set of format: <path>/<prefix>. It auto reads in all sub components at that path"
)
parser.add_argument(
    "-b", "--batch_size", default="1024", help="path to the output folder"
)
parser.add_argument(
    "-w", "--pre_trained_weights", default="resources/models/custom/model", help="path to the pre trained weights of the trained network"
)
parser.add_argument(
    "-f", "--freeze", default="False", choices=["False", "True"], help="path to the pre trained weights of the trained network"
)
parser.add_argument(
    "-o", "--output", default="", help="output path for the weights"
)
parser.add_argument(
    "-s", "--shutdown", default="True", choices=["False", "True"], help="output path for the weights"
)
args = parser.parse_args()


def main() -> None:
    # config
    batch_size = int(args.batch_size)
    output_path = args.output
    X_train, Y_train = load_data(args.trainset)
    X_val, Y_val = load_data(args.valset)
    freeze = args.freeze == "True"
    shutdown = args.shutdown == "True"

    config = Config(set_defaults=True)
    code2Vec = Code2VecCustomModel(config)

    # Setup transfer learning if enabled.
    if args.pre_trained_weights != "":
        code2Vec.load_weights(args.pre_trained_weights)
    if freeze:
        code2Vec.token_embedding_layer.trainable = freeze
        code2Vec.path_embedding_layer.trainable = freeze

    # Create model
    model = CustomModel(code2Vec)
    metrics = ['binary_accuracy']
    optimizer = tf.keras.optimizers.Adam()
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=metrics)

    # Training callbacks
    callbacks = []
    callbacks.append(tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=1, restore_best_weights=True))
    callbacks.append(tf.keras.callbacks.ModelCheckpoint(filepath=output_path, save_weights_only=True, save_best_only=True, monitor='val_loss'))

    # Start training
    model.fit(X_train, Y_train, validation_data=[X_val, Y_val], epochs=100, batch_size=batch_size, callbacks=callbacks)

    # Store the results.
    model.save_weights(output_path)

    # Automatic shut down after long training time
    if shutdown:
        print("shutting down")
        time.sleep(120)
        os.system("shutdown -s")


def load_data(path_to):
    """
    Loads all the sub part in of the data set at onces.
    :param path_to: <PathToFolder>/<Prefix>
    :return:
    """
    Y = np.load(path_to + "Y.npy")
    path_source_token_idxs = np.load(path_to + "path_source_token_idxs.npy")
    path_idxs = np.load(path_to + "path_idxs.npy")
    path_target_token_idxs = np.load(path_to + "path_target_token_idxs.npy")
    context_valid_masks = np.load(path_to + "context_valid_masks.npy")
    X = path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks

    return X, Y


if __name__ == '__main__':
    main()
