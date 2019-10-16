from collections import Iterator

import tensorflow as tf
import numpy as np

from Config import Config
from models.Code2VecCustomModel import _TFEvaluateModelInputTensorsFormer
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs


def main():
    output_prefix = "test_large_"
    dataset_path = "data/java-large-test.txt"
    n_paths = 200
    n_predictions = 1
    n_entries = read_n_entries(dataset_path)

    config = Config(set_defaults=True)
    vocabs = Code2VecVocabs(config)
    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)

    path_source_token_idxs = np.zeros([n_entries, n_paths])
    path_idxs = np.zeros([n_entries, n_paths])
    path_target_token_idxs = np.zeros([n_entries, n_paths])
    context_valid_masks = np.zeros([n_entries, n_paths])
    Y = np.zeros([n_entries, n_predictions])

    for i, line in enumerate(read_dateset(dataset_path)):
        reader_output = predict_reader.process_input_row(tf.convert_to_tensor(line))


        path_source_token_idxs[i] = reader_output[1][0].numpy()
        path_idxs[i] = reader_output[2][0].numpy()
        path_target_token_idxs[i] = reader_output[3][0].numpy()
        context_valid_masks[i] = tf.cast(reader_output[4][0], tf.float32).numpy()
        Y[i] = tf.strings.to_number(reader_output[0]).numpy()

        if i % 1000 == 0:
            print(f"{i}/{n_entries}")

    np.save(output_prefix + "path_source_token_idxs.npy", path_source_token_idxs)
    np.save(output_prefix + "path_idxs.npy", path_idxs)
    np.save(output_prefix + "path_target_token_idxs.npy", path_target_token_idxs)
    np.save(output_prefix + "context_valid_masks.npy", context_valid_masks)
    np.save(output_prefix + "train_Y.npy", Y)




def read_n_entries(path: str) -> int:
    i = 0
    for _ in read_dateset(path):
        i += 1
    return i


def read_dateset(path: str):
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            yield line


if __name__ == '__main__':
    main()
