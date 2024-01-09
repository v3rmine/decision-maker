
from enum import Enum


class Language(Enum):
    ITALIAN = "it"
    ENGLISH = "en"

class SRL_Output(Enum):
    FRAME_SEPARATOR = "-"
    FRAME_CONTAINER_START = "("
    FRAME_CONTAINER_END = ")"
    ARGUMENT_SEPARATOR = ","
    ARGUMENT_CONTAINER_START = "("
    ARGUMENT_CONTAINER_END = ")"
    ARGUMENT_IN_TEXT_START = "'"
    ARGUMENT_IN_TEXT_END = "'"

class SRL_Input(Enum):
    FEATURE_SEPARATOR = "#"
    FEATURE_ELEMENT_SEPARATOR = "&"
    CLASS_SEPARATOR = "|"
    TYPE_SEPARATOR = "|"