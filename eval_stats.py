from collections import defaultdict

from Config import Config
from models.Code2VecCustomModel import _TFEvaluateModelInputTensorsFormer, Code2VecCustomModel
from models.CustomModel import CustomModel
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs
import tensorflow as tf
import csv

class ConfustionMatrix(object):
    def __init__(self):
        self.tp = 0.0
        self.tn = 0.0
        self.fp = 0.0
        self.fn = 0.0

    def add(self, y_predict, y_real):
        if y_real == 1.0 and y_predict == 1.0:
            self.tp += 1
        elif y_real == 0.0 and y_predict == 0.0:
            self.tn += 1
        elif y_real == 0.0 and y_predict == 1.0:
            self.fp += 1
        elif y_real == 1.0 and y_predict == 0.0:
            self.fn += 1
        else:
            raise Exception(f"Unknown values y_predict={y_predict} y_real={y_real}")

    @property
    def accuracy(self):
        if self.tp + self.tn + self.fp + self.fn == 0:
            return 0
        return (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn)

    @property
    def recall(self):
        if self.tp + self.fn == 0:
            return 0
        return self.tp / (self.tp + self.fn)

    @property
    def precision(self):
        if self.tp + self.fp == 0:
            return 0
        return self.tp / (self.tp + self.fp)

    @property
    def f1(self):
        if self.tp + self.fp + self.fn == 0:
            return 0
        return 2 * self.tp / (2 * self.tp + self.fp + self.fn)

    def __repr__(self) -> str:
        return f"ConfustionMatrix(tp={self.tp}, tn={self.tn}, fp={self.fp}, fn={self.fn}, accuracy={self.accuracy}, recall={self.recall}, precision={self.precision}, f1={self.f1})"


def main():
    dataset_path = "data/java-large-test-stats.txt"
    threshold = 0.5

    config = Config(set_defaults=True)
    vocabs = Code2VecVocabs(config)
    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)

    code2vec = Code2VecCustomModel(config)
    model = CustomModel(code2vec)
    model.load_weights("resources/models/pre_trained/model")
    model.compile(loss='binary_crossentropy', optimizer='adam')
    #model.load_weights("resources/models/frozen/model")
    #model.load_weights("resources/models/random_init/model")

    results = defaultdict(ConfustionMatrix)

    @tf.function
    def validate_line(line):
        reader_output = predict_reader.process_input_row(line)


        inputs = [reader_output[1], reader_output[2], reader_output[3], tf.cast(reader_output[4], tf.float32)]

        Y_predict = tf.squeeze(model(inputs))
        Y = tf.squeeze(tf.strings.to_number(reader_output[0]))

        return Y_predict, Y


    for i, data in enumerate(read_dateset(dataset_path)):
        type, line = data
        Y_predict, Y = validate_line(tf.convert_to_tensor(line))
        Y = Y.numpy()
        Y_predict = Y_predict.numpy()
        Y_predict = 1.0 if Y_predict >= threshold else 0.0
        results[type].add(Y_predict, Y)

        if i % 10000 == 0:
            print(f"Step[{i}]")

    with open('data/stats.csv', 'w', newline='') as result_file:
        wr = csv.writer(result_file)
        for type, matrix in results.items():
            data = [type, str(matrix.tp), str(matrix.tn), str(matrix.fp), str(matrix.fn)]
            wr.writerow(data)

def read_dateset(path: str):
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            type, data = line.split(maxsplit=1)
            if type == "NoBug":
                data = "1 " + data
            else:
                data = "0 " + data
            yield type, data

if __name__ == '__main__':
    main()