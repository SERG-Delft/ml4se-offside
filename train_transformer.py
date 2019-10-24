import argparse
import os
import time

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2VecAttention import Code2VecAttention
from models.Code2VecEmbedding import Code2VecEmbedding
from models.Code2VecTransformerBased import Code2VecTransformerBased


class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
    """
    Custom lr as described in https://arxiv.org/abs/1706.03762
    """

    def __init__(self, d_model, warmup_steps=4000):
        super(CustomSchedule, self).__init__()

        self.d_model = d_model
        self.d_model = tf.cast(self.d_model, tf.float32)

        self.warmup_steps = warmup_steps

    def __call__(self, step):
        arg1 = tf.math.rsqrt(step)
        arg2 = step * (self.warmup_steps ** -1.5)

        return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)


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
    "-b", "--batch_size", default="data/", help="path to the output folder"
)
parser.add_argument(
    "-w", "--weights", default="resources/models/pre_trained/model", help="path to the weights of the trained network"
)
parser.add_argument(
    "-e", "--embedding", default="resources/models/code2vec/embedding/model", help="path to the embeding weights of the of code2vec"
)
parser.add_argument(
    "-o", "--output", default="", help="output path for the weights"
)
parser.add_argument(
    "-s", "--shutdown", default="True", help="output path for the weights"
)
args = parser.parse_args()


def main() -> None:
    batch_size = args.batch_size
    output_path = args.output
    X_train, Y_train = load_data(args.trainset)
    X_val, Y_val = load_data(args.valset)

    config = Config(set_defaults=True)
    code2vec_emb = Code2VecEmbedding(config)
    code2vec_emb.load_weights(args.embedding)
    code2vec_att = Code2VecAttention(config)

    model = Code2VecTransformerBased(config, code2vec_emb, code2vec_att)
    # Freeze code2vec embedding layer
    code2vec_emb.token_embedding_layer.trainable = False
    code2vec_emb.path_embedding_layer.trainable = False

    metrics = ['binary_accuracy']
    optimizer = tf.keras.optimizers.Adam(CustomSchedule(d_model=config.CODE_VECTOR_SIZE, warmup_steps=4000), beta_1=0.9, beta_2=0.98,
                                         epsilon=1e-9)
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=metrics)

    callbacks = []
    callbacks.append(tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=1, restore_best_weights=True))
    callbacks.append(
        tf.keras.callbacks.ModelCheckpoint(filepath=output_path, save_weights_only=True, save_best_only=True, monitor='val_loss'))

    model.fit(X_train, Y_train, validation_data=[X_val, Y_val], epochs=100, batch_size=batch_size, callbacks=callbacks)

    model.save_weights(output_path)

    # Automatic shut down after long training time
    if args.shutdown == "True":
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
