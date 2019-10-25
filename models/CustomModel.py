from typing import Tuple

import tensorflow as tf

from models.Code2Vec import Code2Vec
from models.Code2VecCustomModel import Code2VecCustomModel
from utils.Types import GraphInput


class CustomModel(tf.keras.Model):
    """
    The custom model we train.
    """

    def __init__(
            self,
            code2vec: Code2Vec,
            **kwargs
    ) -> None:
        super(CustomModel, self).__init__(**kwargs)
        self._code2vec = code2vec
        self._prediction_layer = tf.keras.layers.Dense(1, activation="sigmoid")

    def call(
            self,
            inputs: Tuple[GraphInput, GraphInput, GraphInput, GraphInput],
            **kwargs
    ):
        outputs, _ = self._code2vec(inputs, **kwargs)

        outputs = self._prediction_layer(outputs, **kwargs)

        return outputs
