from typing import List, Tuple

import tensorflow as tf

from Config import Config
from utils.Types import GraphInput


def _assert_shape(x: tf.Tensor, shape: List[int]) -> None:
    assert x.shape.as_list() == shape, f"Expected shape: {shape} but was: {x.shape.as_list()}"


class Code2VecAttention(tf.keras.Model):
    """
    Attention layer only of code2vec
    Extracted for transformer model.
    """

    def __init__(
            self,
            config: Config,
            **kwargs
    ) -> None:
        self.config = config
        super(Code2VecAttention, self).__init__(**kwargs)

        self.concated_embedding_none_linear_layer = tf.keras.layers.Dense(config.CODE_VECTOR_SIZE, use_bias=False,
                                                                          activation="tanh",
                                                                          name="concated_embedding_none_linear_layer")
        self.context_combiner_layer = tf.keras.layers.Dense(1, use_bias=False, activation="linear",
                                                            name="context_combiner_layer")

        self.attention_softmax_layer = tf.keras.layers.Softmax(axis=1, name="attention_softmax_layer")

        self.dropout_layer = tf.keras.layers.Dropout(rate=1 - self.config.DROPOUT_KEEP_RATE)

    def call(
            self,
            inputs: Tuple[GraphInput, GraphInput],
            **kwargs
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        embedding_vector, mask = inputs

        batch_size = embedding_vector.shape[0]
        batch_aggregated_context = batch_size * self.config.MAX_CONTEXTS if batch_size is not None else None

        assert batch_size == mask.shape[0]

        embedding_vector = self.dropout_layer(embedding_vector, **kwargs)
        _assert_shape(embedding_vector, [batch_size, self.config.MAX_CONTEXTS, self.config.CODE_VECTOR_SIZE])

        flat_embed = tf.reshape(embedding_vector, [-1, self.config.CODE_VECTOR_SIZE])
        _assert_shape(flat_embed, [batch_aggregated_context, self.config.CODE_VECTOR_SIZE])
        flat_embed = self.concated_embedding_none_linear_layer(flat_embed)
        _assert_shape(flat_embed, [batch_aggregated_context, self.config.CODE_VECTOR_SIZE])

        contexts_weights = self.context_combiner_layer(flat_embed)
        _assert_shape(contexts_weights, [batch_aggregated_context, 1])
        batched_contexts_weights = tf.reshape(contexts_weights, [-1, self.config.MAX_CONTEXTS, 1])
        _assert_shape(batched_contexts_weights, [batch_size, self.config.MAX_CONTEXTS, 1])

        mask = tf.math.log(mask)
        mask = tf.expand_dims(mask, axis=2)
        _assert_shape(mask, [batch_size, self.config.MAX_CONTEXTS, 1])
        batched_contexts_weights += mask
        _assert_shape(batched_contexts_weights, [batch_size, self.config.MAX_CONTEXTS, 1])

        attention_weights = self.attention_softmax_layer(batched_contexts_weights)
        _assert_shape(attention_weights, [batch_size, self.config.MAX_CONTEXTS, 1])

        batched_embed = tf.reshape(flat_embed, [-1, self.config.MAX_CONTEXTS, self.config.CODE_VECTOR_SIZE])
        _assert_shape(batched_embed, [batch_size, self.config.MAX_CONTEXTS, self.config.CODE_VECTOR_SIZE])

        code_vectors = tf.reduce_sum(tf.multiply(batched_embed, attention_weights), axis=1)
        _assert_shape(code_vectors, [batch_size, self.config.CODE_VECTOR_SIZE])

        return code_vectors, attention_weights
