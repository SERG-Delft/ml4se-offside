from typing import List, Tuple

import tensorflow as tf

from Config import Config
from utils.Types import GraphInput


def _assert_shape(x: tf.Tensor, shape: List[int]) -> None:
    assert x.shape.as_list() == shape, f"Expected shape: {shape} but was: {x.shape.as_list()}"


class Code2VecEmbedding(tf.keras.Model):
    """
    Emmbeding layer of code2vec only.
    Extracted for transformer model.
    """

    def __init__(
            self,
            config: Config,
            **kwargs
    ) -> None:
        self.config = config
        super(Code2VecEmbedding, self).__init__(**kwargs)

        self.token_embedding_layer = tf.keras.layers.Embedding(config.N_TOKEN_EMBEDDINGS, config.TOKEN_EMBEDDINGS_SIZE,
                                                               name="token_embedding_layer")
        self.path_embedding_layer = tf.keras.layers.Embedding(config.N_PATH_EMBEDDINGS, config.PATH_EMBEDDINGS_SIZE,
                                                              name="path_embedding_layer")

    def call(
            self,
            inputs: Tuple[GraphInput, GraphInput, GraphInput],
            **kwargs
    ) -> tf.Tensor:
        path_source_token_idxs, path_idxs, path_target_token_idxs = inputs

        batch_size = path_source_token_idxs.shape[0]

        assert batch_size == path_idxs.shape[0]
        assert batch_size == path_target_token_idxs.shape[0]

        source_word_embed = self.token_embedding_layer(path_source_token_idxs)
        _assert_shape(source_word_embed, [batch_size, self.config.MAX_CONTEXTS, self.config.TOKEN_EMBEDDINGS_SIZE])
        path_embed = self.path_embedding_layer(path_idxs, **kwargs)
        _assert_shape(path_embed, [batch_size, self.config.MAX_CONTEXTS, self.config.PATH_EMBEDDINGS_SIZE])
        target_word_embed = self.token_embedding_layer(path_target_token_idxs, **kwargs)
        _assert_shape(target_word_embed, [batch_size, self.config.MAX_CONTEXTS, self.config.TOKEN_EMBEDDINGS_SIZE])

        context_embed = tf.concat([source_word_embed, path_embed, target_word_embed], axis=-1)
        _assert_shape(context_embed, [batch_size, self.config.MAX_CONTEXTS, self.config.CODE_VECTOR_SIZE])

        return context_embed
