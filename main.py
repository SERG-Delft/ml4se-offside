import argparse

import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import _TFEvaluateModelInputTensorsFormer, Code2VecCustomModel
from models.CustomModel import CustomModel
from scripts.Extractor import Extractor
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs

parser = argparse.ArgumentParser()
parser.add_argument(
    "-w", "--weights", default="resources/models/pre_trained/model", help="path to the weights of the trained network"
)
parser.add_argument(
    "-i", "--input", default="Input.java", help="path to the weights of the trained network"
)
args = parser.parse_args()

if __name__ == '__main__':
    config = Config(set_defaults=True)

    # Create the extractor
    path_extractor = Extractor(config,
                               jar_path=config.EXTRACTOR_JAR_PATH,
                               max_path_length=config.MAX_PATH_LENGTH,
                               max_path_width=config.MAX_PATH_WIDTH)
    # Example use case of this model.
    # Create a model
    code2vec = Code2VecCustomModel(config)
    model = CustomModel(code2vec)
    model.load_weights(args.weights)

    # Create the PathContextReader
    vocabs = Code2VecVocabs(config)
    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)


    def predict(line):
        # Extract numerical form suitable for model
        reader_output = predict_reader.process_input_row(line)
        inputs = [reader_output[1], reader_output[2], reader_output[3], tf.cast(reader_output[4], tf.float32)]
        return model(inputs)


    try:
        predict_lines, hash_to_string_dict = path_extractor.extract_paths(args.input)
        # Make a prediction for each function in the file
        for line in predict_lines:
            prediction = predict(tf.convert_to_tensor(line))
            print(f"Input function name: {line.split(maxsplit=1)[0]}")
            print(f"raw input: {line}")
            # Probability of code containing a bug
            print(f"Prediction: {prediction.numpy()[0, 0] * 100}%")
    except ValueError as e:
        print(e)
