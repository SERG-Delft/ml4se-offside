import os

import tensorflow as tf

from Config import Config
from models.Code2VecCustomModel import Code2VecCustomModel, _TFEvaluateModelInputTensorsFormer
from models.CustomModel import CustomModel
from scripts.Extractor import Extractor
from scripts.PathContextReader import PathContextReader
from utils.Vocabularies import Code2VecVocabs

if __name__ == '__main__':
    config = Config(set_defaults=True)

    path_extractor = Extractor(config,
                               jar_path=config.EXTRACTOR_JAR_PATH,
                               max_path_length=config.MAX_PATH_LENGTH,
                               max_path_width=config.MAX_PATH_WIDTH)

    # Create a model
    code2vec = Code2VecCustomModel(config)
    model = CustomModel(code2vec)
    model.load_weights(config.CUSTOM_MODEL_WEIGHT_DIR)

    config.get_logger().info('Starting evaluation...')
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
        path = os.path.join(config.EVALUATION_DATA_PATH)
        config.get_logger().info("Finding bugs from context path file: " + str(path))
        config.get_logger().info("Threshold for bug finding is: " + str(config.TESTING_BUG_THRESHOLD))
        config.get_logger().info("Please wait...")
        with open(path) as f:
            for line in f:
                line = line.rstrip("\n")
                prediction = predict(line)
                if prediction.numpy()[0, 0] > config.TESTING_BUG_THRESHOLD:
                    print("BUG HERE?")
                    print("File:method name - " + line.split(" ", 1)[0])
                    print("Prediction: " + str(prediction.numpy()[0, 0]))
    except ValueError as e:
        print(e)
