from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional, Union, Any, cast
import tensorflow as tf

from Config import Config
from models.Code2VecAttention import Code2VecAttention
from models.Code2VecEmbedding import Code2VecEmbedding
from models.Transformer import EncoderLayer
from utils.Types import GraphInput


class Code2VecTransformerBased(tf.keras.Model):
    def __init__(
            self,
            config: Config,
            code2vec_embedding: Code2VecEmbedding,
            code2vec_attention: Code2VecAttention,
            **kwargs
    ) -> None:
        self.config = config
        super(Code2VecTransformerBased, self).__init__(**kwargs)
        self.code2vec_embedding = code2vec_embedding
        self.encoder1 = EncoderLayer(d_model=config.CODE_VECTOR_SIZE, dff=4 * config.CODE_VECTOR_SIZE, num_heads=8, rate=1 - self.config.DROPOUT_KEEP_RATE)
        self.encoder2 = EncoderLayer(d_model=config.CODE_VECTOR_SIZE, dff=4 * config.CODE_VECTOR_SIZE, num_heads=8, rate=1 - self.config.DROPOUT_KEEP_RATE)
        self.code2vec_attention = code2vec_attention
        #self.layernorm = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.prediction_layer = tf.keras.layers.Dense(1, activation="sigmoid")

    def call(
            self,
            inputs: Tuple[GraphInput, GraphInput, GraphInput, GraphInput],
            **kwargs
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        path_source_token_idxs, path_idxs, path_target_token_idxs, context_valid_masks = inputs
        context_embed = self.code2vec_embedding([path_source_token_idxs, path_idxs, path_target_token_idxs], **kwargs)
        encoder_mask = context_valid_masks == 1
        context_embed = self.encoder1([context_embed, encoder_mask], **kwargs)
        context_embed = self.encoder2([context_embed, encoder_mask], **kwargs)

        code_vectors, attention_weights = self.code2vec_attention([context_embed, context_valid_masks], **kwargs)
        #code_vectors = self.layernorm(code_vectors)
        outputs = self.prediction_layer(code_vectors, **kwargs)

        return outputs
 