import os

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import Code2VecCustomModel


def main() -> None:
    output_path = os.path.join(os.path.dirname(__file__), "resources", "models", "custom2", "model")

    Y = np.load("Y.npy")
    path_source_token_idxs = np.load("path_source_token_idxs.npy")
    path_idxs = np.load("path_idxs.npy")
    path_target_token_idxs = np.load("path_target_token_idxs.npy")
    context_valid_masks = np.load("context_valid_masks.npy")
    X = [path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks]

    i = 0
    #print(path_source_token_idxs[i] - path_source_token_idxs[i + 1])
    #print(path_idxs[i])
    #print(path_idxs[i] - path_idxs[i + 1])
    #print(path_target_token_idxs[i] - path_target_token_idxs[i + 1])
    #print(path_source_token_idxs[i] - context_valid_masks[i + 1])
    print(np.mean(path_source_token_idxs))
    print(np.mean(path_idxs))
    print(np.mean(path_target_token_idxs))
    print(np.mean(context_valid_masks))

    """
    config = Config(set_defaults=True)
    code2Vec = Code2VecCustomModel(config)
    code2Vec.load_weights("resources/models/custom/model")

    inputs = [
        tf.keras.layers.Input(shape=[path_source_token_idxs.shape[1]]),
        tf.keras.layers.Input(shape=[path_idxs.shape[1]]),
        tf.keras.layers.Input(shape=[path_target_token_idxs.shape[1]]),
        tf.keras.layers.Input(shape=[context_valid_masks.shape[1]]),
    ]

    outputs, _ = code2Vec(inputs)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(outputs)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    #model.save_weights(output_path)
    print(model.summary())

    model.fit(X, Y, epochs=5, batch_size=2048)

    model.save_weights(output_path)
    """

if __name__ == '__main__':
    main()