import abc
from functools import reduce
from typing import NamedTuple, Optional

import tensorflow as tf

from Config import Config
from utils.Vocabularies import Code2VecVocabs


class ReaderInputTensors(NamedTuple):
    """
    Used mostly for convenient-and-clear access to input parts (by their names).
    """
    path_source_token_indices: tf.Tensor
    path_indices: tf.Tensor
    path_target_token_indices: tf.Tensor
    context_valid_mask: tf.Tensor
    target_index: Optional[tf.Tensor] = None
    target_string: Optional[tf.Tensor] = None
    path_source_token_strings: Optional[tf.Tensor] = None
    path_strings: Optional[tf.Tensor] = None
    path_target_token_strings: Optional[tf.Tensor] = None


class ModelInputTensorsFormer(abc.ABC):
    """
    Should be inherited by the model implementation.
    An instance of the inherited class is passed by the model to the reader in order to help the reader
        to construct the input in the form that the model expects to receive it.
    This class also enables conveniently & clearly access input parts by their field names.
        eg: 'tensors.path_indices' instead if 'tensors[1]'.
    This allows the input tensors to be passed as pure tuples along the computation graph, while the
        python functions that construct the graph can easily (and clearly) access tensors.
    """

    @abc.abstractmethod
    def to_model_input_form(self, input_tensors: ReaderInputTensors):
        ...

    @abc.abstractmethod
    def from_model_input_form(self, input_row) -> ReaderInputTensors:
        ...


class PathContextReader:
    def __init__(self,
                 vocabs: Code2VecVocabs,
                 config: Config,
                 model_input_tensors_former: ModelInputTensorsFormer):
        self.vocabs = vocabs
        self.config = config
        self.model_input_tensors_former = model_input_tensors_former
        self.CONTEXT_PADDING = ','.join([self.vocabs.token_vocab.special_words.PAD,
                                         self.vocabs.path_vocab.special_words.PAD,
                                         self.vocabs.token_vocab.special_words.PAD])
        self.csv_record_defaults = [[self.vocabs.target_vocab.special_words.OOV]] + \
                                   ([[self.CONTEXT_PADDING]] * self.config.MAX_CONTEXTS)

        # initialize the needed lookup tables (if not already initialized).
        self.create_needed_vocabs_lookup_tables(self.vocabs)

    @classmethod
    def create_needed_vocabs_lookup_tables(cls, vocabs: Code2VecVocabs):
        vocabs.token_vocab.get_word_to_index_lookup_table()
        vocabs.path_vocab.get_word_to_index_lookup_table()
        vocabs.target_vocab.get_word_to_index_lookup_table()

    @tf.function
    def process_input_row(self, row_placeholder):
        parts = tf.io.decode_csv(
            row_placeholder, record_defaults=self.csv_record_defaults, field_delim=' ', use_quote_delim=False)

        tensors = self._map_raw_dataset_row_to_input_tensors(*parts)

        # make it batched (first batch axis is going to have dimension 1)
        tensors_expanded = ReaderInputTensors(
            **{name: None if tensor is None else tf.expand_dims(tensor, axis=0)
               for name, tensor in tensors._asdict().items()})
        return self.model_input_tensors_former.to_model_input_form(tensors_expanded)

    def _map_raw_dataset_row_to_input_tensors(self, *row_parts) -> ReaderInputTensors:
        row_parts = list(row_parts)
        target_str = row_parts[0]
        target_index = self.vocabs.target_vocab.lookup_index(target_str)

        contexts_str = tf.stack(row_parts[1:(self.config.MAX_CONTEXTS + 1)], axis=0)
        split_contexts = tf.compat.v1.string_split(contexts_str, sep=',', skip_empty=False)

        sparse_split_contexts = tf.sparse.SparseTensor(
            indices=split_contexts.indices, values=split_contexts.values, dense_shape=[self.config.MAX_CONTEXTS, 3])
        dense_split_contexts = tf.reshape(
            tf.sparse.to_dense(sp_input=sparse_split_contexts, default_value=self.vocabs.token_vocab.special_words.PAD),
            shape=[self.config.MAX_CONTEXTS, 3])  # (max_contexts, 3)

        path_source_token_strings = tf.squeeze(
            tf.slice(dense_split_contexts, begin=[0, 0], size=[self.config.MAX_CONTEXTS, 1]), axis=1)  # (max_contexts,)
        path_strings = tf.squeeze(
            tf.slice(dense_split_contexts, begin=[0, 1], size=[self.config.MAX_CONTEXTS, 1]), axis=1)  # (max_contexts,)
        path_target_token_strings = tf.squeeze(
            tf.slice(dense_split_contexts, begin=[0, 2], size=[self.config.MAX_CONTEXTS, 1]), axis=1)  # (max_contexts,)

        path_source_token_indices = self.vocabs.token_vocab.lookup_index(path_source_token_strings)  # (max_contexts, )
        path_indices = self.vocabs.path_vocab.lookup_index(path_strings)  # (max_contexts, )
        path_target_token_indices = self.vocabs.token_vocab.lookup_index(path_target_token_strings)  # (max_contexts, )

        valid_word_mask_per_context_part = [
            tf.not_equal(path_source_token_indices,
                         self.vocabs.token_vocab.word_to_index[self.vocabs.token_vocab.special_words.PAD]),
            tf.not_equal(path_target_token_indices,
                         self.vocabs.token_vocab.word_to_index[self.vocabs.token_vocab.special_words.PAD]),
            tf.not_equal(path_indices, self.vocabs.path_vocab.word_to_index[
                self.vocabs.path_vocab.special_words.PAD])]  # [(max_contexts, )]
        context_valid_mask = tf.cast(reduce(tf.logical_or, valid_word_mask_per_context_part),
                                     dtype=tf.float32)  # (max_contexts, )

        # Will cause error when tensorflow-2.0.0-beta1 -> tensorflow-2.0.0-rc1
        # assert all(tensor.shape == (self.config.MAX_CONTEXTS,) for tensor in
        #           {path_source_token_indices, path_indices, path_target_token_indices, context_valid_mask})

        return ReaderInputTensors(
            path_source_token_indices=path_source_token_indices,
            path_indices=path_indices,
            path_target_token_indices=path_target_token_indices,
            context_valid_mask=context_valid_mask,
            target_index=target_index,
            target_string=target_str,
            path_source_token_strings=path_source_token_strings,
            path_strings=path_strings,
            path_target_token_strings=path_target_token_strings
        )
