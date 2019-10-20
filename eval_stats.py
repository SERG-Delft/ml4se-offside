from collections import defaultdict

from Config import Config
from models.Code2VecCustomModel import _TFEvaluateModelInputTensorsFormer, Code2VecCustomModel
from models.CustomModel import CustomModel
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs
import tensorflow as tf
import csv
import re

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
    dataset_path = "data/java-large-test-IFonly.txt"
    threshold = 0.5
    combine_sub_cats = False

    config = Config(set_defaults=True)
    vocabs = Code2VecVocabs(config)
    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)

    code2vec = Code2VecCustomModel(config)
    model = CustomModel(code2vec)
    model.load_weights("resources/models/pre_trained/model")
    # model.load_weights("resources/models/pre_trained_if0/model")
    #model.load_weights("resources/models/frozen/model")
    #model.load_weights("resources/models/random_init/model")
    model.compile(loss='binary_crossentropy', optimizer='adam')

    results = defaultdict(ConfustionMatrix)

    @tf.function
    def validate_line(line):
        reader_output = predict_reader.process_input_row(line)


        inputs = [reader_output[1], reader_output[2], reader_output[3], tf.cast(reader_output[4], tf.float32)]

        Y_predict = tf.squeeze(model(inputs))
        Y = tf.squeeze(tf.strings.to_number(reader_output[0]))

        return Y_predict, Y


    for i, data in enumerate(read_dateset(dataset_path, combine_sub_cats=combine_sub_cats)):
        types, line = data

        Y_predict, Y = validate_line(tf.convert_to_tensor(line))
        Y = Y.numpy()
        Y_predict = Y_predict.numpy()
        Y_predict = 1.0 if Y_predict >= threshold else 0.0
        for type in types:
            results[type].add(Y_predict, Y)

        if i % 1000 == 0:
            print(f"Step[{i}]")

    with open('data/stats.csv', 'w', newline='') as result_file:
        wr = csv.writer(result_file)
        for type, matrix in results.items():
            data = [type, str(matrix.tp), str(matrix.tn), str(matrix.fp), str(matrix.fn)]
            wr.writerow(data)

def read_dateset(path: str, combine_sub_cats: bool = False):
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            types, data = line.split(maxsplit=1)
            types = list(filter(lambda x : len(x) > 0, types.split("#")))
            if "NoBug" in types:
                types = types[1:]
                data = "0 " + data
            else:
                data = "1 " + data
                types = list(map(map_to_oposite_sign, types))

            if combine_sub_cats:
                types = list(map(map_sub_catagory, types))
            yield types, data

def map_to_oposite_sign(cat: str) -> str:
    if cat.endswith("greaterEquals"):
        return cat.replace("greaterEquals", "greater")
    if cat.endswith("greater"):
        return cat.replace("greater", "greaterEquals")
    if cat.endswith("lessEquals"):
        return cat.replace("lessEquals", "less")
    if cat.endswith("less"):
        return cat.replace("less", "lessEquals")
    raise Exception(f"Unknown cat={cat}")


def map_sub_catagory(cat: str) -> str:
    if cat.startswith("NoBug"):
        return "NoBug"
    if cat.startswith("FOR"):
        return "FOR"
    if cat.startswith("WHILE"):
        return "WHILE"
    if cat.startswith("TERNARY"):
        return "TERNARY"
    if cat.startswith("IF"):
        return "IF"
    if cat.startswith("RETURN"):
        return "RETURN"
    if cat.startswith("METHOD"):
        return "METHOD"
    if cat.startswith("DO"):
        return "DO"
    if cat.startswith("ASSIGN"):
        return "ASSIGN"
    if cat.startswith("ASSERT"):
        return "ASSERT"
    if cat.startswith("VARIABLEDECLARATOR"):
        return "VARIABLEDECLARATOR"
    if cat.startswith("OBJECTCREATION"):
        return "OBJECTCREATION"
    if cat.startswith("EXPRESSION"):
        return "EXPRESSION"
    raise Exception(f"Unknown mapping cat={cat}")


if __name__ == '__main__':
    main()