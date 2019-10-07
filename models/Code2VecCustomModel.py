from typing import List, Tuple

import numpy as np
import tensorflow as tf

from scripts.PathContextReader import ModelInputTensorsFormer, ReaderInputTensors
from utils.Types import GraphInput

# TODO Need to pass config into call somehow or make Config.py static so we can remove the ones below
DROPOUT_KEEP_RATE = 0.75
N_TOKEN_EMBEDDINGS = 1300853
N_PATH_EMBEDDINGS = 909711
MAX_CONTEXTS = 200
DEFAULT_EMBEDDINGS_SIZE = 128
PATH_EMBEDDINGS_SIZE = DEFAULT_EMBEDDINGS_SIZE
TOKEN_EMBEDDINGS_SIZE = DEFAULT_EMBEDDINGS_SIZE
CODE_VECTOR_SIZE = PATH_EMBEDDINGS_SIZE + 2 * TOKEN_EMBEDDINGS_SIZE


def _assert_shape(x: tf.Tensor, shape: List[int]) -> None:
    assert x.shape.as_list() == shape, f"Expected shape: {shape} but was: {x.shape.as_list()}"


class Code2VecCustomModel(tf.keras.Model):
    """
    Example use case of this model.
    # Create a model
    model = Code2VecCustomModel()
    # This load the weights from the original code2vec.
    # Note that these should be converted first using the ExtractWeightRealCode2Vec.py script.
    model.load_weights("../resources/models/custom/model")

    # load inputs these are example values.
    path_source_token_idxs = np.ones(shape=[1, MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
    path_idxs = np.ones(shape=[1, MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
    path_target_token_idxs = np.ones(shape=[1, MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
    context_valid_masks = np.ones(shape=[1, MAX_CONTEXTS, ], dtype=np.float32)  # (batch, max_contexts)
    inputs = [path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks]

    #make a prediction
    print(model(inputs))
    """
    def __init__(
            self,
            config,
            **kwargs
    ) -> None:
        self.config = config
        super(Code2VecCustomModel, self).__init__(**kwargs)
        self.token_embedding_layer = tf.keras.layers.Embedding(config.N_TOKEN_EMBEDDINGS, config.TOKEN_EMBEDDINGS_SIZE,
                                                               name="token_embedding_layer")
        self.path_embedding_layer = tf.keras.layers.Embedding(config.N_PATH_EMBEDDINGS, config.PATH_EMBEDDINGS_SIZE,
                                                              name="path_embedding_layer")

        self.concated_embedding_none_linear_layer = tf.keras.layers.Dense(config.CODE_VECTOR_SIZE, use_bias=False,
                                                                          activation="tanh",
                                                                          name="concated_embedding_none_linear_layer")
        self.context_combiner_layer = tf.keras.layers.Dense(1, use_bias=False, activation="linear",
                                                            name="context_combiner_layer")

        self.attention_softmax_layer = tf.keras.layers.Softmax(axis=1, name="attention_softmax_layer")

    def call(
            self,
            inputs: Tuple[GraphInput, GraphInput, GraphInput, GraphInput],
            training: bool=False,
            **kwargs
    ):
        #training = kwargs["training"] if "training" in kwargs else None
        path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks = inputs
        batch_size = path_source_token_idxs.shape[0]
        batch_aggregated_context = batch_size * MAX_CONTEXTS if batch_size is not None else None

        assert batch_size == path_idxs.shape[0]
        assert batch_size == path_target_token_idxs.shape[0]
        assert batch_size == context_valid_masks.shape[0]

        source_word_embed = self.token_embedding_layer(path_source_token_idxs)
        _assert_shape(source_word_embed, [batch_size, MAX_CONTEXTS, TOKEN_EMBEDDINGS_SIZE])
        path_embed = self.path_embedding_layer(path_idxs)
        _assert_shape(path_embed, [batch_size, MAX_CONTEXTS, PATH_EMBEDDINGS_SIZE])
        target_word_embed = self.token_embedding_layer(path_target_token_idxs)
        _assert_shape(target_word_embed, [batch_size, MAX_CONTEXTS, TOKEN_EMBEDDINGS_SIZE])

        context_embed = tf.concat([source_word_embed, path_embed, target_word_embed], axis=-1)
        if training:
            context_embed = tf.keras.layers.Dropout(rate=1 - DROPOUT_KEEP_RATE)(context_embed)
        _assert_shape(context_embed, [batch_size, MAX_CONTEXTS, CODE_VECTOR_SIZE])

        flat_embed = tf.reshape(context_embed, [-1, CODE_VECTOR_SIZE])
        _assert_shape(flat_embed, [batch_aggregated_context, CODE_VECTOR_SIZE])
        flat_embed = self.concated_embedding_none_linear_layer(flat_embed)
        _assert_shape(flat_embed, [batch_aggregated_context, CODE_VECTOR_SIZE])

        contexts_weights = self.context_combiner_layer(flat_embed)
        _assert_shape(contexts_weights, [batch_aggregated_context, 1])
        batched_contexts_weights = tf.reshape(contexts_weights, [-1, MAX_CONTEXTS, 1])
        _assert_shape(batched_contexts_weights, [batch_size, MAX_CONTEXTS, 1])

        mask = tf.math.log(context_valid_masks)
        mask = tf.expand_dims(mask, axis=2)
        _assert_shape(mask, [batch_size, MAX_CONTEXTS, 1])
        batched_contexts_weights += mask
        _assert_shape(batched_contexts_weights, [batch_size, MAX_CONTEXTS, 1])

        attention_weights = self.attention_softmax_layer(batched_contexts_weights)
        _assert_shape(attention_weights, [batch_size, MAX_CONTEXTS, 1])

        batched_embed = tf.reshape(flat_embed, [-1, MAX_CONTEXTS, CODE_VECTOR_SIZE])
        _assert_shape(batched_embed, [batch_size, MAX_CONTEXTS, CODE_VECTOR_SIZE])

        code_vectors = tf.reduce_sum(tf.multiply(batched_embed, attention_weights), axis=1)
        _assert_shape(code_vectors, [batch_size, CODE_VECTOR_SIZE])

        return code_vectors, attention_weights

    def initialize_variables(self, config) -> None:
        path_source_token_idxs = np.ones(shape=[1, config.MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
        path_idxs = np.ones(shape=[1, config.MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
        path_target_token_idxs = np.ones(shape=[1, config.MAX_CONTEXTS, ], dtype=np.int32)  # (batch, max_contexts)
        context_valid_masks = np.ones(shape=[1, config.MAX_CONTEXTS, ], dtype=np.float32)  # (batch, max_contexts)
        inputs = [path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks]
        self(inputs)

    def assign_pre_trained_weights(
            self,
            word_vocab: np.ndarray,
            path_vocab: np.ndarray,
            transformer: np.ndarray,
            attention: np.ndarray,
    ) -> None:
        self.token_embedding_layer.variables[0].assign(word_vocab)
        self.path_embedding_layer.variables[0].assign(path_vocab)
        self.concated_embedding_none_linear_layer.variables[0].assign(transformer)
        self.context_combiner_layer.variables[0].assign(attention)


class _TFEvaluateModelInputTensorsFormer(ModelInputTensorsFormer):
    def to_model_input_form(self, input_tensors: ReaderInputTensors):
        return input_tensors.target_string, input_tensors.path_source_token_indices, input_tensors.path_indices, \
               input_tensors.path_target_token_indices, input_tensors.context_valid_mask, \
               input_tensors.path_source_token_strings, input_tensors.path_strings, \
               input_tensors.path_target_token_strings

    def from_model_input_form(self, input_row) -> ReaderInputTensors:
        return ReaderInputTensors(
            target_string=input_row[0],
            path_source_token_indices=input_row[1],
            path_indices=input_row[2],
            path_target_token_indices=input_row[3],
            context_valid_mask=input_row[4],
            path_source_token_strings=input_row[5],
            path_strings=input_row[6],
            path_target_token_strings=input_row[7]
        )
