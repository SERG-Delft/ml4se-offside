import numpy as np
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
    # Example use case of this model.
    # Create a model
    code2vec = Code2VecCustomModel(config)
    model = CustomModel(code2vec)
    model.load_weights("resources/models/custom3/model")


    input_filename = 'Input.java'
    config.get_logger().info('Starting interactive prediction...')
    vocabs = Code2VecVocabs(config)

    predict_reader = PathContextReader(vocabs=vocabs,
                                       model_input_tensors_former=_TFEvaluateModelInputTensorsFormer(),
                                       config=config)

    #@tf.function # With this tf.functionn we stack the other tf.function such that they are combined into a single call graph on the gpu.
    def predict(line):
        # Extract numerical form suitable for model
        print("line")
        print(line)
        reader_output = predict_reader.process_input_row(line)
        inputs = [reader_output[1], reader_output[2], reader_output[3], tf.cast(reader_output[4], tf.float32)]


        return model(inputs)



    try:
        predict_lines, hash_to_string_dict = path_extractor.extract_paths(input_filename)
        print("hash_to_string_dict")
        print(hash_to_string_dict)
        print("predict_lines")
        print(predict_lines)
        for line in predict_lines:
            prediction = predict(line)
            # Probability of code containing a bug
            print("Prediction: " + str(prediction.numpy()[0,0]))
    except ValueError as e:
        print(e)