from typing import Tuple

import tensorflow as tf

from models.Code2VecAttention import Code2VecAttention
from models.Code2VecEmbedding import Code2VecEmbedding
from utils.Types import GraphInput


class Code2Vec(tf.keras.Model):
    """
    Code2vec model split up into 2 parts.
    """

    def __init__(
            self,
            code2vec_embedding: Code2VecEmbedding,
            code2vec_attention: Code2VecAttention,
            **kwargs
    ) -> None:
        super(Code2Vec, self).__init__(**kwargs)
        self.code2vec_embedding = code2vec_embedding
        self.code2vec_attention = code2vec_attention

    def call(
            self,
            inputs: Tuple[GraphInput, GraphInput, GraphInput, GraphInput],
            **kwargs
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks = inputs
        context_embed = self.code2vec_embedding([path_source_token_idxs, path_idxs, path_target_token_idxs], **kwargs)
        code_vectors, attention_weights = self.code2vec_attention([context_embed, context_valid_masks], **kwargs)

        return code_vectors, attention_weights
