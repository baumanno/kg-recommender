import ast
import os

from configparser import SafeConfigParser

class Config:

    __RECOMMENDABLE_SECTION_NAME = "RECOMMENDABLE"
    __RECOMMENDABLE_TYPE_KEY_NAME = "type"

    __PREDICATE_TYPES_SECTION_NAME = "PREDICATES"
    __PREDICATE_TYPES_APPLICABLE_KEY_NAME = "applicable"
    __PREDICATE_TYPES_EXTRA_METADATA_KEY_NAME = "extrametadata"

    __parser = None

    def __init__(self):
        self.__parser = SafeConfigParser(delimiters=('='))
        self.__parser.optionxform = str # we want case-sensitive keys
        self.__parser.read(os.path.join(os.path.dirname(__file__),'res/config.ini'))

    def getRecommendableType(self):
        return self.__parser.get(self.__RECOMMENDABLE_SECTION_NAME, self.__RECOMMENDABLE_TYPE_KEY_NAME)

    def getPredicateTypes(self):
        ps = self.__parser.get(self.__PREDICATE_TYPES_SECTION_NAME, self.__PREDICATE_TYPES_APPLICABLE_KEY_NAME)
        return ast.literal_eval(ps)

    def getExtraMetadataTypes(self):
        e = self.__parser.get(self.__PREDICATE_TYPES_SECTION_NAME, self.__PREDICATE_TYPES_EXTRA_METADATA_KEY_NAME)
        return ast.literal_eval(e)

