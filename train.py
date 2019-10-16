import os
import time

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import Code2VecCustomModel
from models.CustomModel import CustomModel


def main() -> None:
    batch_size = 1024 * 4
    output_path = os.path.join(os.path.dirname(__file__), "resources", "models", "frozen", "model")
    X_train, Y_train = load_data("train_large_")
    X_val, Y_val = load_data("val_large_")


    config = Config(set_defaults=True)
    code2Vec = Code2VecCustomModel(config)
    code2Vec.load_weights("resources/models/custom/model")
    code2Vec.token_embedding_layer.trainable = False
    code2Vec.path_embedding_layer.trainable = False

    model = CustomModel(code2Vec)
    metrics = ['binary_accuracy']
    optimizer = tf.keras.optimizers.Adam()
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=metrics)


    callbacks = []
    callbacks.append(tf.keras.callbacks.EarlyStopping(monitor='val_binary_accuracy', min_delta=0, patience=1, restore_best_weights=True))
    callbacks.append(tf.keras.callbacks.ModelCheckpoint(filepath=output_path, save_weights_only=True, save_best_only=True, monitor='val_binary_accuracy'))

    
    model.fit(X_train, Y_train, validation_data=[X_val, Y_val], epochs=100, batch_size=batch_size, callbacks=callbacks)


    model.save_weights(output_path)

    print("shutting down")
    time.sleep(120)
    os.system("shutdown -s")


def load_data(prefix):
    Y = np.load("data/" + prefix + "Y.npy")
    path_source_token_idxs = np.load("data/" + prefix + "path_source_token_idxs.npy")
    path_idxs = np.load("data/" + prefix + "path_idxs.npy")
    path_target_token_idxs = np.load("data/" + prefix + "path_target_token_idxs.npy")
    context_valid_masks = np.load("data/" + prefix + "context_valid_masks.npy")
    X = [path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks]

    return X, Y


if __name__ == '__main__':
    main()