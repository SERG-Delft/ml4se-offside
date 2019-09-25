import os
import pickle
from argparse import Namespace
from collections import OrderedDict
from enum import Enum
from itertools import chain
from typing import Optional, Dict, Iterable, Set

import tensorflow as tf

from Config import Config


class VocabType(Enum):
    Token = 1
    Target = 2
    Path = 3


SpecialVocabWordsType = Namespace

_SpecialVocabWords_OnlyOov = Namespace(
    OOV='<OOV>'
)

_SpecialVocabWords_SeparateOovPad = Namespace(
    PAD='<PAD>',
    OOV='<OOV>'
)

_SpecialVocabWords_JoinedOovPad = Namespace(
    PAD_OR_OOV='<PAD_OR_OOV>',
    PAD='<PAD_OR_OOV>',
    OOV='<PAD_OR_OOV>'
)


def get_unique_list(lst: Iterable) -> list:
    return list(OrderedDict(((item, 0) for item in lst)).keys())


class Vocab:
    def __init__(self, vocab_type: VocabType, words: Iterable[str],
                 special_words: Optional[SpecialVocabWordsType] = None):
        if special_words is None:
            special_words = Namespace()

        self.vocab_type = vocab_type
        self.word_to_index: Dict[str, int] = {}
        self.index_to_word: Dict[int, str] = {}
        self._word_to_index_lookup_table = None
        self._index_to_word_lookup_table = None
        self.special_words: SpecialVocabWordsType = special_words

        for index, word in enumerate(chain(get_unique_list(special_words.__dict__.values()), words)):
            self.word_to_index[word] = index
            self.index_to_word[index] = word

        self.size = len(self.word_to_index)

    @classmethod
    def load_from_file(cls, vocab_type: VocabType, file, special_words: SpecialVocabWordsType) -> 'Vocab':
        special_words_as_unique_list = get_unique_list(special_words.__dict__.values())

        # Notice: From historical reasons, a saved vocab doesn't include special words,
        #         so they should be added upon loading.

        word_to_index_wo_specials = pickle.load(file)
        index_to_word_wo_specials = pickle.load(file)
        size_wo_specials = pickle.load(file)
        assert len(index_to_word_wo_specials) == len(word_to_index_wo_specials) == size_wo_specials
        min_word_idx_wo_specials = min(index_to_word_wo_specials.keys())

        if min_word_idx_wo_specials != len(special_words_as_unique_list):
            raise ValueError(
                "Error while attempting to load vocabulary `{vocab_type}` from file `{file_path}`. "
                "The stored vocabulary has minimum word index {min_word_idx}, "
                "while expecting minimum word index to be {nr_special_words} "
                "because having to use {nr_special_words} special words, which are: {special_words}. "
                "Please check the parameter `config.SEPARATE_OOV_AND_PAD`.".format(
                    vocab_type=vocab_type, file_path=file.name, min_word_idx=min_word_idx_wo_specials,
                    nr_special_words=len(special_words_as_unique_list), special_words=special_words))

        vocab = cls(vocab_type, [], special_words)
        vocab.word_to_index = {**word_to_index_wo_specials,
                               **{word: idx for idx, word in enumerate(special_words_as_unique_list)}}
        vocab.index_to_word = {**index_to_word_wo_specials,
                               **{idx: word for idx, word in enumerate(special_words_as_unique_list)}}
        vocab.size = size_wo_specials + len(special_words_as_unique_list)
        return vocab

    @staticmethod
    def _create_word_to_index_lookup_table(word_to_index: Dict[str, int], default_value: int):
        return tf.lookup.StaticHashTable(
            tf.lookup.KeyValueTensorInitializer(
                list(word_to_index.keys()), list(word_to_index.values()), key_dtype=tf.string, value_dtype=tf.int32),
            default_value=tf.constant(default_value, dtype=tf.int32))

    @staticmethod
    def _create_index_to_word_lookup_table(index_to_word: Dict[int, str], default_value: str) \
            -> tf.lookup.StaticHashTable:
        return tf.lookup.StaticHashTable(
            tf.lookup.KeyValueTensorInitializer(
                list(index_to_word.keys()), list(index_to_word.values()), key_dtype=tf.int32, value_dtype=tf.string),
            default_value=tf.constant(default_value, dtype=tf.string))

    def get_word_to_index_lookup_table(self) -> tf.lookup.StaticHashTable:
        if self._word_to_index_lookup_table is None:
            self._word_to_index_lookup_table = self._create_word_to_index_lookup_table(
                self.word_to_index, default_value=self.word_to_index[self.special_words.OOV])
        return self._word_to_index_lookup_table

    def lookup_index(self, word: tf.Tensor) -> tf.Tensor:
        return self.get_word_to_index_lookup_table().lookup(word)


class Code2VecVocabs:
    def __init__(self, config: Config):
        self.config = config
        self.token_vocab: Optional[Vocab] = None
        self.path_vocab: Optional[Vocab] = None
        self.target_vocab: Optional[Vocab] = None

        # Used to avoid re-saving a non-modified vocabulary to a path it is already saved in.
        self._already_saved_in_paths: Set[str] = set()

        self._load_or_create()

    def _load_or_create(self):
        vocabularies_load_path = self.config.get_vocabularies_path_from_model_path(self.config.MODEL_LOAD_PATH)
        if not os.path.isfile(vocabularies_load_path):
            raise ValueError(
                "Model dictionaries file is not found in model load dir. "
                "Expecting file `{vocabularies_load_path}`.".format(vocabularies_load_path=vocabularies_load_path))
        self._load_from_path(vocabularies_load_path)

    def _load_from_path(self, vocabularies_load_path: str):
        assert os.path.exists(vocabularies_load_path)
        self.config.log('Loading model vocabularies from: `%s` ... ' % vocabularies_load_path)
        with open(vocabularies_load_path, 'rb') as file:
            self.token_vocab = Vocab.load_from_file(
                VocabType.Token, file, self._get_special_words_by_vocab_type(VocabType.Token))
            self.target_vocab = Vocab.load_from_file(
                VocabType.Target, file, self._get_special_words_by_vocab_type(VocabType.Target))
            self.path_vocab = Vocab.load_from_file(
                VocabType.Path, file, self._get_special_words_by_vocab_type(VocabType.Path))
        self.config.log('Done loading model vocabularies.')
        # print('Done loading model vocabularies.')
        self._already_saved_in_paths.add(vocabularies_load_path)

    def _get_special_words_by_vocab_type(self, vocab_type: VocabType) -> SpecialVocabWordsType:
        if not self.config.SEPARATE_OOV_AND_PAD:
            return _SpecialVocabWords_JoinedOovPad
        if vocab_type == VocabType.Target:
            return _SpecialVocabWords_OnlyOov
        return _SpecialVocabWords_SeparateOovPad
