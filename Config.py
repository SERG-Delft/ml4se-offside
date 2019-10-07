import logging
import os
import sys
from typing import Optional


class Config:

    def set_defaults(self):

        # model hyper-params
        self.MAX_CONTEXTS = 200
        self.DEFAULT_EMBEDDINGS_SIZE = 128
        self.TOKEN_EMBEDDINGS_SIZE = self.DEFAULT_EMBEDDINGS_SIZE
        self.PATH_EMBEDDINGS_SIZE = self.DEFAULT_EMBEDDINGS_SIZE
        self.CODE_VECTOR_SIZE = self.context_vector_size
        self.DROPOUT_KEEP_RATE = 0.75
        self.SEPARATE_OOV_AND_PAD = False
        self.N_TOKEN_EMBEDDINGS = 1300853
        self.N_PATH_EMBEDDINGS = 909711
        self.MAX_PATH_LENGTH = 8
        self.MAX_PATH_WIDTH = 2

        self.ROOT = os.path.dirname(__file__)
        self.EXTRACTOR_JAR_PATH = os.path.join(self.ROOT, "jars", "JavaExtractor-0.0.2-SNAPSHOT.jar")
        self.ORIGINAL_MODEL_DIR = os.path.join(self.ROOT, "resources", "models", "java14m_trainable")
        self.ORIGINAL_MODEL_NAME = "saved_model_iter8"
        self.CUSTOM_MODEL_DIR = os.path.join(self.ROOT, "resources", "models", "custom", "model")
        self.MODEL_LOAD_PATH = os.path.join(self.ORIGINAL_MODEL_DIR, self.ORIGINAL_MODEL_NAME)
        self.VERBOSE_MODE: int = 1

    def __init__(self, set_defaults: bool = False):

        # model hyper-params
        self.MAX_CONTEXTS: int = 0
        self.DEFAULT_EMBEDDINGS_SIZE: int = 0
        self.TOKEN_EMBEDDINGS_SIZE: int = 0
        self.PATH_EMBEDDINGS_SIZE: int = 0
        self.CODE_VECTOR_SIZE: int = 0
        self.DROPOUT_KEEP_RATE: float = 0
        self.SEPARATE_OOV_AND_PAD: bool = False
        self.N_TOKEN_EMBEDDINGS: int = 0
        self.N_PATH_EMBEDDINGS: int = 909711
        self.MAX_PATH_LENGTH: int = 0
        self.MAX_PATH_WIDTH: int = 0

        self.ROOT: Optional[str] = None
        self.EXTRACTOR_JAR_PATH: Optional[str] = None
        self.ORIGINAL_MODEL_DIR: Optional[str] = None
        self.ORIGINAL_MODEL_NAME: Optional[str] = None
        self.CUSTOM_MODEL_DIR: Optional[str] = None
        self.MODEL_LOAD_PATH: Optional[str] = None
        self.VERBOSE_MODE: int = 0
        self.LOGS_PATH: Optional[str] = None

        self.__logger: Optional[logging.Logger] = None

        if set_defaults:
            self.set_defaults()

    def log(self, msg):
        self.get_logger().info(msg)

    @property
    def context_vector_size(self) -> int:
        # The context vector is actually a concatenation of the embedded
        # source & target vectors and the embedded path vector.
        return self.PATH_EMBEDDINGS_SIZE + 2 * self.TOKEN_EMBEDDINGS_SIZE

    @classmethod
    def get_vocabularies_path_from_model_path(cls, model_file_path: str) -> str:
        vocabularies_save_file_name = "dictionaries.bin"
        base_path, _ = os.path.split(model_file_path)
        return os.path.join(base_path, vocabularies_save_file_name)

    def get_logger(self) -> logging.Logger:
        if self.__logger is None:
            self.__logger = logging.getLogger('root')
            self.__logger.setLevel(logging.INFO)
            self.__logger.handlers = []
            self.__logger.propagate = 0

            formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

            if self.VERBOSE_MODE >= 1:
                ch = logging.StreamHandler(sys.stdout)
                ch.setLevel(logging.INFO)
                ch.setFormatter(formatter)
                self.__logger.addHandler(ch)

            if self.LOGS_PATH:
                fh = logging.FileHandler(self.LOGS_PATH)
                fh.setLevel(logging.INFO)
                fh.setFormatter(formatter)
                self.__logger.addHandler(fh)

        return self.__logger
