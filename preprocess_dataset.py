from typing import Iterator, Tuple
import tensorflow as tf
import numpy as np
import collections

from Config import Config
from models.Code2VecCustomModel import Code2VecCustomModel, _TFEvaluateModelInputTensorsFormer
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs


def main() -> None:
    config = Config(set_defaults=True)
    code2Vec = Code2VecCustomModel(config)
    code2Vec.load_weights("resources/models/custom/model")

    vocabs = Code2VecVocabs(config)
    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)

    #@tf.function
    def pre_process_line(line: str) -> Tuple[tf.Tensor, tf.Tensor]:
        reader_output = predict_reader.process_input_row(line)
        X = [reader_output[1], reader_output[2], reader_output[3], tf.cast(reader_output[4], tf.float32)]
        Y = reader_output[0]

        code_vectors, attention_weights = code2Vec(X)
        return code_vectors[0], tf.strings.to_number(Y)

    dataset_path = "result.txt"
    n_features = 384
    n_predictions = 1
    n_entries = read_n_entries(dataset_path)
    X = np.zeros((n_entries, n_features))
    Y = np.zeros((n_entries, n_predictions))


    for i, line in enumerate(read_dateset(dataset_path, padding=True)):
        x, y = pre_process_line(line)
        X[i] = x.numpy()
        Y[i] = y.numpy()


        if i % 1000 == 0:
            print(f"{i}/{n_entries}")

    np.save("X.npy", X)
    np.save("Y.npy", Y)


def count_labels_dataset(path: str):
    counter = collections.Counter()
    for line in read_dateset(path, padding=False):
        counter.update(line[0])
    return counter


def read_n_entries(path: str) -> int:
    i = 0
    for _ in read_dateset(path, padding=False):
        i += 1
    return i

def read_dateset(path: str, padding: bool = False) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            line = line.rstrip()
            if padding:
                n_fields = line.count(" ")
                if n_fields < 200:
                    line = line + "".join([" " for _ in range(200 - n_fields)])
            yield line


if __name__ == '__main__':
    main()