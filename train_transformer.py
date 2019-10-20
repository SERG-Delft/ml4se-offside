import os
import time

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2Vec import Code2Vec
from models.Code2VecAttention import Code2VecAttention
from models.Code2VecEmbedding import Code2VecEmbedding
from models.Code2VecTransformerBased import Code2VecTransformerBased
from models.CustomModel import CustomModel


class CustomSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
    def __init__(self, d_model, warmup_steps=4000):
        super(CustomSchedule, self).__init__()

        self.d_model = d_model
        self.d_model = tf.cast(self.d_model, tf.float32)

        self.warmup_steps = warmup_steps

    def __call__(self, step):
        arg1 = tf.math.rsqrt(step)
        arg2 = step * (self.warmup_steps ** -1.5)

        return tf.math.rsqrt(self.d_model) * tf.math.minimum(arg1, arg2)

def main() -> None:
    batch_size = 256 * 1
    output_path = os.path.join(os.path.dirname(__file__), "resources", "models", "transformer", "model")
    X_train, Y_train = load_data("train_")
    X_val, Y_val = load_data("val_")
    #X_train, Y_train = load_data("train_large_")
    #X_val, Y_val = load_data("val_large_")

    config = Config(set_defaults=True)

    code2vec_emb = Code2VecEmbedding(config)
    code2vec_emb.load_weights("resources/models/code2vec/embedding/model")
    code2vec_att = Code2VecAttention(config)
    code2vec_att.load_weights("resources/models/code2vec/attention/model")

    model = Code2VecTransformerBased(config, code2vec_emb, code2vec_att)

    code2vec_emb.token_embedding_layer.trainable = False
    code2vec_emb.path_embedding_layer.trainable = False


    metrics = ['binary_accuracy']
    optimizer = tf.keras.optimizers.Adam(CustomSchedule(d_model=config.CODE_VECTOR_SIZE, warmup_steps=4000), beta_1=0.9, beta_2=0.98,
                                     epsilon=1e-9)
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=metrics)
    """
    path_source_token_idxs = np.ones(shape=[10, config.MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
    path_idxs = np.ones(shape=[10, config.MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
    path_target_token_idxs = np.ones(shape=[10, config.MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
    context_valid_masks = np.ones(shape=[10, config.MAX_CONTEXTS, ], dtype=np.float32)  # (batch, max_contexts)
    code_vector = np.ones(shape=[10, config.MAX_CONTEXTS, config.CODE_VECTOR_SIZE])
    inputs = [path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks]
    print(model(inputs))
    """


    callbacks = []
    callbacks.append(tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=1, restore_best_weights=True))
    callbacks.append(
        tf.keras.callbacks.ModelCheckpoint(filepath=output_path, save_weights_only=True, save_best_only=True, monitor='val_loss'))

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
    X = path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks

    return X, Y


if __name__ == '__main__':
    main()