import argparse

import numpy as np
import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import _TFEvaluateModelInputTensorsFormer
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs

parser = argparse.ArgumentParser()
parser.add_argument(
    "-i", "--dataset", default="data/java-large-test-IFonly.txt", help="path to the data set."
)
parser.add_argument(
    "-o", "--output", default="data/", help="path to the output folder"
)
parser.add_argument(
    "-x", "--prefix", default="", help="prefix for the output files"
)
args = parser.parse_args()


def main():
    config = Config(set_defaults=True)
    output_prefix = args.prefix
    dataset_path = args.dataset
    if dataset_path[-1] != "/":
        dataset_path += "/"

    n_paths = config.MAX_CONTEXTS
    n_predictions = config.N_PREDICTIONS
    n_entries = read_n_entries(dataset_path)

    # Create the path context reader.
    vocabs = Code2VecVocabs(config)
    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)

    # Create the resulting numpy data structures.
    path_source_token_idxs = np.zeros([n_entries, n_paths])
    path_idxs = np.zeros([n_entries, n_paths])
    path_target_token_idxs = np.zeros([n_entries, n_paths])
    context_valid_masks = np.zeros([n_entries, n_paths])
    Y = np.zeros([n_entries, n_predictions])

    # Loop through all the ASTs and encoded them into numpy data structures.
    for i, line in enumerate(read_dateset(dataset_path)):
        # Transform ASTs into tensors.
        reader_output = predict_reader.process_input_row(tf.convert_to_tensor(line))

        # Store tensors in numpy data structures.
        path_source_token_idxs[i] = reader_output[1][0].numpy()
        path_idxs[i] = reader_output[2][0].numpy()
        path_target_token_idxs[i] = reader_output[3][0].numpy()
        context_valid_masks[i] = tf.cast(reader_output[4][0], tf.float32).numpy()
        Y[i] = tf.strings.to_number(reader_output[0]).numpy()

        if i % 1000 == 0:
            print(f"Completed {i + 1} of the {n_entries} entries")

    # Store resulting numpy data structures on disc.
    np.save(f"{dataset_path}{output_prefix}path_source_token_idxs.npy", path_source_token_idxs)
    np.save(f"{dataset_path}{output_prefix}path_idxs.npy", path_idxs)
    np.save(f"{dataset_path}{output_prefix}path_target_token_idxs.npy", path_target_token_idxs)
    np.save(f"{dataset_path}{output_prefix}context_valid_masks.npy", context_valid_masks)
    np.save(f"{dataset_path}{output_prefix}Y.npy", Y)


def read_n_entries(path: str) -> int:
    """
    :param path: Path to the the data entries.
    :return: The number of data entries.
    """
    i = 0
    for _ in read_dateset(path):
        i += 1
    return i


def read_dateset(path: str):
    """

    :param path:  Path to the the data entries.
    :return: A generator of the rows in the data set.
    """
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            types, data = line.split(maxsplit=1)
            if "NoBug" in types or "0" in types:
                data = "0 " + data
            else:
                data = "1 " + data
            yield data


if __name__ == '__main__':
    main()
